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
     * @param columnTypeChangeBehavior How to handle column type changes.
     * @param requireSeparateCommitsForColumnReplace If true, when replacing a column (deleting and
     * re-adding with the same name but different type), the delete and add operations are committed
     * separately. This is required for some catalogs (like BigLake) that don't support deleting and
     * adding a column with the same name in a single commit, even with different field IDs. Default
     * is false for backward compatibility.
     * @return The updated [Schema], after changes have been applied and committed.
     */
    fun maybeApplySchemaChanges(
        table: Table,
        incomingSchema: Schema,
        columnTypeChangeBehavior: ColumnTypeChangeBehavior,
        requireSeparateCommitsForColumnReplace: Boolean = false,
    ): SchemaUpdateResult {
        val existingSchema = table.schema()
        val diff = comparator.compareSchemas(incomingSchema, existingSchema)

        if (!diff.hasChanges()) {
            // If no differences, return the existing schema as-is.
            return SchemaUpdateResult(existingSchema, pendingUpdates = emptyList())
        }

        val update: UpdateSchema = table.updateSchema().allowIncompatibleChanges()

        // 1) Remove columns that no longer exist in the incoming schema
        diff.removedColumns.forEach { removedColumn -> update.deleteColumn(removedColumn) }

        // 2) Update types => find a supertype for each changed column
        val columnsToReplaceInSecondCommit =
            mutableMapOf<String, org.apache.iceberg.types.Types.NestedField>()

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
                    // arbitrary type changes via updateColumn().
                    // So we have to drop+add the column (replace it).

                    if (requireSeparateCommitsForColumnReplace) {
                        // For catalogs like BigLake that don't support delete+add in single commit,
                        // we only delete here and will add in a separate update later.
                        update.deleteColumn(columnName)
                        // Store the field to add back later
                        columnsToReplaceInSecondCommit[columnName] = incomingField
                    } else {
                        // Standard Iceberg behavior: delete+add in single commit
                        update.deleteColumn(columnName)
                        update.addColumn(columnName, incomingField.type())
                    }
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

        // If we're doing separate commits for column replacements, we must commit the delete
        // immediately. This is required because BigLake needs separate transactions, and Iceberg's
        // UpdateSchema API is stateless (each call to table.updateSchema() is based on the
        // committed schema). We commit the delete first, then create the add operation.
        if (requireSeparateCommitsForColumnReplace && columnsToReplaceInSecondCommit.isNotEmpty()) {
            // Commit the delete operation immediately
            update.commit()
            table.refresh()

            // Create a new update for adding the replaced columns back with their new types
            val addUpdate = table.updateSchema().allowIncompatibleChanges()

            // Add back the replaced columns with their new types
            columnsToReplaceInSecondCommit.forEach { (columnName, field) ->
                addUpdate.addColumn(null, columnName, field.type())
            }

            // Commit or defer the add operation based on columnTypeChangeBehavior
            val finalSchema = addUpdate.apply()
            return if (columnTypeChangeBehavior.commitImmediately) {
                addUpdate.commit()
                SchemaUpdateResult(finalSchema, pendingUpdates = emptyList())
            } else {
                SchemaUpdateResult(finalSchema, pendingUpdates = listOf(addUpdate))
            }
        }

        // `apply` just validates that the schema change is valid, it doesn't actually commit().
        // It returns the schema that the table _would_ have after committing.
        val newSchema: Schema = update.apply()
        if (columnTypeChangeBehavior.commitImmediately) {
            update.commit()
            return SchemaUpdateResult(newSchema, pendingUpdates = emptyList())
        } else {
            return SchemaUpdateResult(newSchema, pendingUpdates = listOf(update))
        }
    }
}

data class SchemaUpdateResult(val schema: Schema, val pendingUpdates: List<UpdateSchema>)
