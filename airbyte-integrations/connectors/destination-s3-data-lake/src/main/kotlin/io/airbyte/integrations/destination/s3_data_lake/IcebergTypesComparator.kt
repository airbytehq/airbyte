/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import org.apache.iceberg.Schema
import org.apache.iceberg.types.Type
import org.apache.iceberg.types.Types

/**
 * Compares two Iceberg [Schema] definitions to identify:
 * - New columns that do not exist in the "existing" schema.
 * - Columns whose data types have changed.
 * - Columns that no longer exist in the incoming schema (i.e., removed).
 * - Columns that changed from required to optional.
 */
class IcebergTypesComparator {

    /**
     * Represents the differences between two Iceberg schemas.
     *
     * @property newColumns list of column names that are new in the incoming schema.
     * @property updatedDataTypes list of column names whose types differ between incoming and
     * existing schema.
     * @property removedColumns list of column names that no longer exist in the incoming schema.
     * @property newlyOptionalColumns list of column names that changed from required (existing) to
     * optional (incoming).
     */
    data class ColumnDiff(
        val newColumns: List<String>,
        val updatedDataTypes: List<String>,
        val removedColumns: List<String>,
        val newlyOptionalColumns: List<String>
    )

    /**
     * Compares two Iceberg schemas and returns a [ColumnDiff] describing how they differ.
     *
     * @param incomingSchema the new or updated schema.
     * @param existingSchema the currently stored schema.
     * @return a [ColumnDiff] representing the changes between the existing and the incoming
     * schemas.
     */
    fun compareSchemas(incomingSchema: Schema, existingSchema: Schema): ColumnDiff {
        val incomingFields = incomingSchema.asStruct().fields().associateBy { it.name() }
        val existingFields = existingSchema.asStruct().fields().associateBy { it.name() }

        val newColumns = mutableListOf<String>()
        val updatedDataTypes = mutableListOf<String>()
        val removedColumns = mutableListOf<String>()
        val newlyOptionalColumns = mutableListOf<String>()

        // Identify new, updated, and columns that became optional
        for ((incomingName, incomingField) in incomingFields) {
            val existingField = existingFields[incomingName]

            if (existingField == null) {
                // Column doesn't exist in the existing schema
                newColumns.add(incomingName)
            } else {
                // Column exists in both. Check for type or structure changes
                if (!typesAreEqual(incomingField.type(), existingField.type())) {
                    updatedDataTypes.add(incomingName)
                }

                // Check if it changed from required to optional
                val wasRequired = !existingField.isOptional
                val isNowOptional = incomingField.isOptional
                if (wasRequired && isNowOptional) {
                    newlyOptionalColumns.add(incomingName)
                }
            }
        }

        // Identify removed columns
        for ((existingName, _) in existingFields) {
            if (!incomingFields.containsKey(existingName)) {
                removedColumns.add(existingName)
            }
        }

        return ColumnDiff(
            newColumns = newColumns,
            updatedDataTypes = updatedDataTypes,
            removedColumns = removedColumns,
            newlyOptionalColumns = newlyOptionalColumns
        )
    }

    /**
     * Checks if two Iceberg [Type]s are semantically equal. For example:
     * - Primitive types must match by [Type.TypeID].
     * - Timestamp types must match with respect to UTC adjustment.
     * - Structs are compared field-by-field.
     * - Lists compare the element type.
     *
     * @param existingType the type in the existing schema
     * @param incomingType the type in the incoming schema
     * @return `true` if the types are considered the same, otherwise `false`.
     */
    private fun typesAreEqual(existingType: Type?, incomingType: Type?): Boolean {
        // If either is null (shouldn't happen if the schema is valid), treat as not equal
        if (existingType == null || incomingType == null) return false

        // Check the top-level type ID
        if (existingType.typeId() != incomingType.typeId()) {
            return false
        }

        return when (val typeId = existingType.typeId()) {
            Type.TypeID.BOOLEAN,
            Type.TypeID.INTEGER,
            Type.TypeID.LONG,
            Type.TypeID.FLOAT,
            Type.TypeID.DOUBLE,
            Type.TypeID.DATE,
            Type.TypeID.TIME,
            Type.TypeID.STRING -> {
                // For these primitive types, the type ID match is enough
                true
            }
            Type.TypeID.TIMESTAMP -> {
                require(
                    existingType is Types.TimestampType && incomingType is Types.TimestampType
                ) { "Expected timestamp types, but received $existingType and $incomingType." }
                // Both must either adjust to UTC or not adjust
                existingType.shouldAdjustToUTC() == incomingType.shouldAdjustToUTC()
            }
            Type.TypeID.LIST -> {
                require(existingType is Types.ListType && incomingType is Types.ListType) {
                    "Expected list types, but received $existingType and $incomingType."
                }
                val sameElementType =
                    typesAreEqual(existingType.elementType(), incomingType.elementType())
                sameElementType &&
                    (existingType.isElementOptional == incomingType.isElementOptional)
            }
            Type.TypeID.STRUCT -> {
                val struct1 = existingType.asStructType()
                val struct2 = incomingType.asStructType()

                // Must have the same number of fields
                if (struct1.fields().size != struct2.fields().size) return false

                // Compare each field by index
                struct1.fields().indices.forEach { i ->
                    val field1 = struct1.fields()[i]
                    val field2 = struct2.fields()[i]

                    if (field1.name() != field2.name()) return false
                    if (field1.isOptional != field2.isOptional) return false
                    if (!typesAreEqual(field1.type(), field2.type())) return false
                }
                true
            }
            Type.TypeID.BINARY,
            Type.TypeID.DECIMAL,
            Type.TypeID.FIXED,
            Type.TypeID.UUID,
            Type.TypeID.MAP,
            Type.TypeID.TIMESTAMP_NANO -> {
                throw IllegalArgumentException(
                    "Unsupported or unmapped Iceberg type: $typeId. " +
                        "Please implement handling if needed."
                )
            }
        }
    }
}
