/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import jakarta.inject.Singleton
import org.apache.iceberg.Schema
import org.apache.iceberg.types.Type
import org.apache.iceberg.types.Types

/**
 * Compares two Iceberg [Schema] definitions (including nested structs) to identify:
 * - New columns that do not exist in the "existing" schema.
 * - Columns whose data types have changed.
 * - Columns that no longer exist in the incoming schema (removed).
 * - Columns that changed from required to optional.
 */
@Singleton
class S3DataLakeTypesComparator {

    companion object {
        /** Separator used to represent nested field paths: parent~child. */
        const val PARENT_CHILD_SEPARATOR: Char = '~'

        /**
         * Returns a fully-qualified field name by appending `child` to `parent` using
         * [PARENT_CHILD_SEPARATOR]. If `parent` is blank, returns `child` alone.
         */
        private fun fullyQualifiedName(parent: String?, child: String): String =
            if (parent.isNullOrBlank()) child else "$parent$PARENT_CHILD_SEPARATOR$child"

        /**
         * Splits a fully-qualified name (e.g. `"outer~inner~field"`) into:
         * ```
         * parent = "outer~inner"
         * leaf   = "field"
         * ```
         * If there's no [PARENT_CHILD_SEPARATOR], then it's top-level:
         * ```
         * parent = ""
         * leaf   = "outer"
         * ```
         */
        fun splitIntoParentAndLeaf(fqName: String): Pair<String, String> {
            val idx = fqName.lastIndexOf(PARENT_CHILD_SEPARATOR)
            return if (idx < 0) {
                "" to fqName
            } else {
                fqName.substring(0, idx) to fqName.substring(idx + 1)
            }
        }
    }

    /**
     * A data class representing differences between two Iceberg schemas.
     *
     * @property newColumns list of fully-qualified column names that are new in the incoming
     * schema.
     * @property updatedDataTypes list of fully-qualified column names whose types differ.
     * @property removedColumns list of fully-qualified column names that are no longer in the
     * incoming schema.
     * @property newlyOptionalColumns list of fully-qualified column names that changed from
     * required -> optional.
     */
    data class ColumnDiff(
        val newColumns: MutableList<String> = mutableListOf(),
        val updatedDataTypes: MutableList<String> = mutableListOf(),
        val removedColumns: MutableList<String> = mutableListOf(),
        val newlyOptionalColumns: MutableList<String> = mutableListOf(),
        var identifierFieldsChanged: Boolean = false
    ) {
        fun hasChanges(): Boolean {
            return newColumns.isNotEmpty() ||
                updatedDataTypes.isNotEmpty() ||
                removedColumns.isNotEmpty() ||
                newlyOptionalColumns.isNotEmpty() ||
                identifierFieldsChanged
        }
    }

    /**
     * Compares [incomingSchema] with [existingSchema], returning a [ColumnDiff].
     *
     * @param incomingSchema the schema of incoming data.
     * @param existingSchema the schema currently known/used by Iceberg.
     */
    fun compareSchemas(incomingSchema: Schema, existingSchema: Schema): ColumnDiff {
        val diff = ColumnDiff()
        compareStructFields(
            parentPath = null,
            incomingType = incomingSchema.asStruct(),
            existingType = existingSchema.asStruct(),
            diff = diff
        )

        val incomingIdentifierNames = incomingSchema.identifierFieldNames().toSet()
        val existingIdentifierNames = existingSchema.identifierFieldNames().toSet()
        diff.identifierFieldsChanged = incomingIdentifierNames != existingIdentifierNames
        return diff
    }

    /**
     * Recursively compares fields of two struct types, identifying new, updated, or removed
     * columns, and appending the results to [diff].
     *
     * @param parentPath fully-qualified parent path, or `null` if at top-level.
     * @param incomingType struct type of the incoming schema.
     * @param existingType struct type of the existing schema.
     * @param diff the [ColumnDiff] object to be updated.
     */
    private fun compareStructFields(
        parentPath: String?,
        incomingType: Types.StructType,
        existingType: Types.StructType,
        diff: ColumnDiff
    ) {
        val incomingFieldsByName = incomingType.fields().associateBy { it.name() }
        val existingFieldsByName = existingType.fields().associateBy { it.name() }

        // 1) Identify new and changed fields
        for ((fieldName, incomingField) in incomingFieldsByName) {
            val fqName = fullyQualifiedName(parentPath, fieldName)
            val existingField = existingFieldsByName[fieldName]

            if (existingField == null) {
                // This column does not exist in the existing schema => new column
                diff.newColumns.add(fqName)
            } else {
                // The column exists in both => check for type differences at top-level
                if (
                    parentPath.isNullOrBlank() &&
                        !typesAreEqual(incomingField.type(), existingField.type())
                ) {
                    diff.updatedDataTypes.add(fqName)
                }

                // Check if it changed from required to optional at top-level
                val wasRequired = !existingField.isOptional
                val isNowOptional = incomingField.isOptional
                if (parentPath.isNullOrBlank() && wasRequired && isNowOptional) {
                    diff.newlyOptionalColumns.add(fqName)
                }

                // If both are struct types, recursively compare subfields
                if (incomingField.type().isStructType && existingField.type().isStructType) {
                    compareStructFields(
                        parentPath = fqName,
                        incomingType = incomingField.type().asStructType(),
                        existingType = existingField.type().asStructType(),
                        diff = diff
                    )
                }
            }
        }

        // 2) Identify removed fields (only at top-level)
        if (parentPath.isNullOrBlank()) {
            for ((existingName) in existingFieldsByName) {
                if (!incomingFieldsByName.containsKey(existingName)) {
                    val fqName = fullyQualifiedName(parentPath, existingName)
                    diff.removedColumns.add(fqName)
                }
            }
        }
    }

    /**
     * Checks if two Iceberg [Type]s are semantically equal by comparing type IDs and any relevant
     * sub-properties (e.g., for timestamps, lists, structs).
     *
     * @param incomingType the type from the incoming schema.
     * @param existingType the type from the existing schema.
     * @return `true` if they are effectively the same type, `false` otherwise.
     * @throws IllegalArgumentException if an unsupported or unmapped Iceberg type is encountered.
     */
    fun typesAreEqual(incomingType: Type, existingType: Type): Boolean {
        if (existingType.typeId() != incomingType.typeId()) return false

        return when (val typeId = existingType.typeId()) {
            Type.TypeID.BOOLEAN,
            Type.TypeID.INTEGER,
            Type.TypeID.LONG,
            Type.TypeID.FLOAT,
            Type.TypeID.DOUBLE,
            Type.TypeID.DATE,
            Type.TypeID.TIME,
            Type.TypeID.STRING -> {
                // Matching primitive types
                true
            }
            Type.TypeID.TIMESTAMP -> {
                require(
                    existingType is Types.TimestampType && incomingType is Types.TimestampType
                ) { "Expected TIMESTAMP types, got $existingType and $incomingType." }
                // Must match UTC adjustment or not
                existingType.shouldAdjustToUTC() == incomingType.shouldAdjustToUTC()
            }
            Type.TypeID.LIST -> {
                require(existingType is Types.ListType && incomingType is Types.ListType) {
                    "Expected LIST types, but received $existingType and $incomingType."
                }
                val sameElementType =
                    typesAreEqual(incomingType.elementType(), existingType.elementType())
                sameElementType &&
                    (existingType.isElementOptional == incomingType.isElementOptional)
            }
            Type.TypeID.STRUCT -> {
                val incomingStructFields =
                    incomingType.asStructType().fields().associateBy { it.name() }
                val existingStructFields =
                    existingType.asStructType().fields().associateBy { it.name() }

                // For all fields in existing, ensure there's a matching field in incoming
                for ((name, existingField) in existingStructFields) {
                    val incomingField = incomingStructFields[name] ?: return false
                    if (existingField.isOptional != incomingField.isOptional) return false
                    if (!typesAreEqual(incomingField.type(), existingField.type())) return false
                }
                // If there are extra fields in `incoming`, that doesn't mean they're "unequal" per
                // se —
                // but for this function's purpose, we only check the existing fields.
                true
            }
            Type.TypeID.BINARY,
            Type.TypeID.DECIMAL,
            Type.TypeID.FIXED,
            Type.TypeID.UUID,
            Type.TypeID.MAP,
            Type.TypeID.TIMESTAMP_NANO -> {
                throw IllegalArgumentException(
                    "Unsupported or unmapped Iceberg type: $typeId. Implement handling if needed."
                )
            }
        }
    }
}
