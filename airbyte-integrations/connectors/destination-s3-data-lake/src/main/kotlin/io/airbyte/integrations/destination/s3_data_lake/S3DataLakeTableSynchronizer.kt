/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.integrations.destination.s3_data_lake.S3DataLakeTypesComparator.Companion.PARENT_CHILD_SEPARATOR
import io.airbyte.integrations.destination.s3_data_lake.S3DataLakeTypesComparator.Companion.splitIntoParentAndLeaf
import jakarta.inject.Singleton
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.UpdateSchema
import org.apache.iceberg.types.Type
import org.apache.iceberg.types.Type.PrimitiveType

/**
 * Applies schema changes to an Iceberg [Table], including nested columns (struct fields).
 *
 * Supports:
 * - Adding new columns (possibly nested).
 * - Removing top-level columns.
 * - Updating types (finding a supertype).
 * - Marking columns newly optional.
 *
 * @property comparator Used to compare schemas and find differences.
 * @property superTypeFinder Used to find a common supertype when data types differ.
 */
@Singleton
class S3DataLakeTableSynchronizer(
    private val comparator: S3DataLakeTypesComparator,
    private val superTypeFinder: S3DataLakeSuperTypeFinder,
) {

    /**
     * Compare [table]'s current schema with [incomingSchema] and apply changes as needed:
     *
     * 1. Remove columns that are no longer in the incoming schema.
     * 2. Update column types to a common supertype if they differ.
     * 3. Mark columns newly optional if changed from required.
     * 4. Add columns that don't exist in the existing schema.
     *
     * @param table The Iceberg table to update.
     * @param incomingSchema The schema describing incoming data.
     * @return The updated [Schema], after changes have been applied and committed.
     */
    fun applySchemaChanges(table: Table, incomingSchema: Schema): Schema {
        val existingSchema = table.schema()
        val diff = comparator.compareSchemas(incomingSchema, existingSchema)

        if (!diff.hasChanges()) {
            // If no differences, return the existing schema as-is.
            return existingSchema
        }

        val update: UpdateSchema = table.updateSchema().allowIncompatibleChanges()

        // 1) Remove columns that no longer exist in the incoming schema
        diff.removedColumns.forEach { removedColumn -> update.deleteColumn(removedColumn) }

        // 2) Update types => find a supertype for each changed column
        diff.updatedDataTypes.forEach { columnName ->
            val existingField =
                existingSchema.findField(columnName)
                    ?: error("Field \"$columnName\" not found in the existing schema!")
            val incomingField =
                incomingSchema.findField(columnName)
                    ?: error("Field \"$columnName\" not found in the incoming schema!")

            val superType: Type =
                superTypeFinder.findSuperType(
                    existingType = existingField.type(),
                    incomingType = incomingField.type(),
                    columnName = columnName
                )
            require(superType is PrimitiveType) {
                "Currently only primitive type updates are supported. Attempted type: $superType"
            }

            // Update the column to the supertype
            update.updateColumn(columnName, superType)
        }

        // 3) Mark columns newly optional
        diff.newlyOptionalColumns.forEach { columnName -> update.makeColumnOptional(columnName) }

        // 4) Add new columns, sorted by nesting depth (so that parents are created before children)
        val sortedNewColumns =
            diff.newColumns.sortedBy { it.count { char -> char == PARENT_CHILD_SEPARATOR } }

        for (newColumnFqn in sortedNewColumns) {
            val (parentPath, leafName) = splitIntoParentAndLeaf(newColumnFqn)

            // Only 1-level nesting is supported
            if (parentPath.count { it == PARENT_CHILD_SEPARATOR } > 0) {
                throw IllegalArgumentException(
                    "Adding nested columns more than 1 level deep is not supported: $newColumnFqn"
                )
            }

            // Locate the appropriate incoming field
            val incomingField =
                if (parentPath.isEmpty()) {
                    // Top-level column
                    incomingSchema.findField(leafName)
                        ?: error("Field \"$leafName\" not found in the incoming schema.")
                } else {
                    // 1-level nested column: "structFieldName~childField"
                    val parentField =
                        incomingSchema.findField(parentPath)
                            ?: error(
                                "Parent field \"$parentPath\" not found in the incoming schema."
                            )

                    require(parentField.type().isStructType) {
                        "Attempting to add a sub-field to a non-struct parent field: $parentPath"
                    }

                    parentField.type().asStructType().asSchema().findField(leafName)
                        ?: error(
                            "Sub-field \"$leafName\" not found in the schema under \"$parentPath\"."
                        )
                }

            // Add the column via the Iceberg API
            if (parentPath.isEmpty()) {
                update.addColumn(null, leafName, incomingField.type())
            } else {
                update.addColumn(parentPath, leafName, incomingField.type())
            }
        }

        // Commit all changes and refresh the table schema
        update.commit()
        table.refresh()

        return table.schema()
    }
}
