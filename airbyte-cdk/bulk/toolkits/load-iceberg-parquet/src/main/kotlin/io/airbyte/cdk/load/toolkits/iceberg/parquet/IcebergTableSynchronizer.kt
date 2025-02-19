/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTypesComparator.Companion.PARENT_CHILD_SEPARATOR
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTypesComparator.Companion.splitIntoParentAndLeaf
import jakarta.inject.Singleton
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.UpdateSchema
import org.apache.iceberg.types.Type
import org.apache.iceberg.types.Type.PrimitiveType

/** Describes how the [IcebergTableSynchronizer] handles column type changes. */
enum class ColumnTypeChangeBehavior {
    /**
     * Find the supertype between the old and new types, throwing an error if Iceberg does not
     * support safely altering the column in this way.
     */
    SAFE_SUPERTYPE {
        override val commitImmediately = true
    },

    /** Set the column's type to the new type, executing an incompatible schema change if needed. */
    OVERWRITE {
        override val commitImmediately = false
    };

    /**
     * If true, [IcebergTableSynchronizer.maybeApplySchemaChanges] will commit the schema update
     * itself. If false, the caller is responsible for calling
     * `schemaUpdateResult.pendingUpdate?.commit()`.
     */
    abstract val commitImmediately: Boolean
}

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
class IcebergTableSynchronizer(
    private val comparator: IcebergTypesComparator,
    private val superTypeFinder: IcebergSuperTypeFinder,
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
    fun maybeApplySchemaChanges(
        table: Table,
        incomingSchema: Schema,
        columnTypeChangeBehavior: ColumnTypeChangeBehavior,
    ): SchemaUpdateResult {
        val existingSchema = table.schema()
        val diff = comparator.compareSchemas(incomingSchema, existingSchema)

        if (!diff.hasChanges()) {
            // If no differences, return the existing schema as-is.
            return SchemaUpdateResult(existingSchema, pendingUpdate = null)
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

            when (columnTypeChangeBehavior) {
                ColumnTypeChangeBehavior.SAFE_SUPERTYPE -> {
                    val superType: Type =
                        superTypeFinder.findSuperType(
                            existingType = existingField.type(),
                            incomingType = incomingField.type(),
                            columnName = columnName
                        )
                    if (superType !is PrimitiveType) {
                        throw ConfigErrorException(
                            "Currently only primitive type updates are supported. Attempted type: $superType"
                        )
                    }
                    update.updateColumn(columnName, superType)
                }
                ColumnTypeChangeBehavior.OVERWRITE -> {
                    // Even when allowIncompatibleChanges is enabled, Iceberg still doesn't allow
                    // arbitrary type changes.
                    // So we have to drop+add the column here.
                    update.deleteColumn(columnName)
                    update.addColumn(columnName, incomingField.type())
                }
            }
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
                throw ConfigErrorException(
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

        // 5) Update identifier fields
        if (diff.identifierFieldsChanged) {
            val updatedIdentifierFields = incomingSchema.identifierFieldNames().toList()
            updatedIdentifierFields.forEach { update.requireColumn(it) }
            update.setIdentifierFields(updatedIdentifierFields)
        }

        // `apply` just validates that the schema change is valid, it doesn't actually commit().
        // It returns the schema that the table _would_ have after committing.
        val newSchema: Schema = update.apply()
        if (columnTypeChangeBehavior.commitImmediately) {
            update.commit()
            return SchemaUpdateResult(newSchema, pendingUpdate = null)
        } else {
            return SchemaUpdateResult(newSchema, update)
        }
    }
}

data class SchemaUpdateResult(val schema: Schema, val pendingUpdate: UpdateSchema?)
