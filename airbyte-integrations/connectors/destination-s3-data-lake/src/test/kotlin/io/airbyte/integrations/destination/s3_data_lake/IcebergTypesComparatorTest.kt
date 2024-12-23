/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import org.apache.iceberg.Schema
import org.apache.iceberg.types.Type
import org.apache.iceberg.types.Types
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

/** Extensive test suite for [IcebergTypesComparator]. */
class IcebergTypesComparatorTest {

    private val comparator = IcebergTypesComparator()

    /**
     * Helper function to create a simple Iceberg field.
     *
     * @param name the field name
     * @param type the field type
     * @param isOptional indicates whether the field is optional
     */
    private fun field(name: String, type: Type, isOptional: Boolean): Types.NestedField {
        val fieldId = name.hashCode() and 0x7fffffff // A simple, stable ID generator for test
        return if (isOptional) {
            Types.NestedField.optional(fieldId, name, type)
        } else {
            Types.NestedField.required(fieldId, name, type)
        }
    }

    /** Convenience function to build an Iceberg [Schema] from a list of [Types.NestedField]. */
    private fun buildSchema(vararg fields: Types.NestedField): Schema {
        return Schema(fields.toList())
    }

    @Test
    fun testNoDifferencesForIdenticalSchemas() {
        val schema =
            buildSchema(
                field("id", Types.IntegerType.get(), false),
                field("name", Types.StringType.get(), true),
                field("created_at", Types.TimestampType.withoutZone(), false),
            )

        val diff = comparator.compareSchemas(schema, schema)

        assertThat(diff.newColumns).isEmpty()
        assertThat(diff.updatedDataTypes).isEmpty()
        assertThat(diff.removedColumns).isEmpty()
        assertThat(diff.newlyOptionalColumns).isEmpty()
    }

    @Test
    fun testNewColumns() {
        val existingSchema =
            buildSchema(
                field("id", Types.IntegerType.get(), false),
            )
        val incomingSchema =
            buildSchema(
                field("id", Types.IntegerType.get(), false),
                field("new_col_1", Types.StringType.get(), true),
                field("new_col_2", Types.TimestampType.withZone(), true),
            )

        val diff = comparator.compareSchemas(incomingSchema, existingSchema)

        assertThat(diff.newColumns).containsExactlyInAnyOrder("new_col_1", "new_col_2")
        assertThat(diff.updatedDataTypes).isEmpty()
        assertThat(diff.removedColumns).isEmpty()
        assertThat(diff.newlyOptionalColumns).isEmpty()
    }

    @Test
    fun testRemovedColumns() {
        val existingSchema =
            buildSchema(
                field("id", Types.IntegerType.get(), false),
                field("legacy_col", Types.StringType.get(), true),
            )
        val incomingSchema =
            buildSchema(
                field("id", Types.IntegerType.get(), false),
            )

        val diff = comparator.compareSchemas(incomingSchema, existingSchema)

        assertThat(diff.newColumns).isEmpty()
        assertThat(diff.updatedDataTypes).isEmpty()
        assertThat(diff.removedColumns).containsExactly("legacy_col")
        assertThat(diff.newlyOptionalColumns).isEmpty()
    }

    @Test
    fun testUpdatedDataTypes() {
        val existingSchema =
            buildSchema(
                field("id", Types.IntegerType.get(), false),
                field("age", Types.IntegerType.get(), true),
            )
        val incomingSchema =
            buildSchema(
                field("id", Types.IntegerType.get(), false),
                // age is changed from INTEGER -> LONG
                field("age", Types.LongType.get(), true),
            )

        val diff = comparator.compareSchemas(incomingSchema, existingSchema)

        assertThat(diff.newColumns).isEmpty()
        assertThat(diff.updatedDataTypes).containsExactly("age")
        assertThat(diff.removedColumns).isEmpty()
        assertThat(diff.newlyOptionalColumns).isEmpty()
    }

    @Test
    fun testNewlyOptionalColumns() {
        val existingSchema =
            buildSchema(
                field("id", Types.IntegerType.get(), false),
                // name was previously required
                field("name", Types.StringType.get(), false),
            )
        val incomingSchema =
            buildSchema(
                field("id", Types.IntegerType.get(), false),
                // name is now optional
                field("name", Types.StringType.get(), true),
            )

        val diff = comparator.compareSchemas(incomingSchema, existingSchema)

        assertThat(diff.newColumns).isEmpty()
        assertThat(diff.updatedDataTypes).isEmpty()
        assertThat(diff.removedColumns).isEmpty()
        // name is newly optional
        assertThat(diff.newlyOptionalColumns).containsExactly("name")
    }

    @Test
    fun testTimestampTypeWithZoneVersusWithoutZone() {
        val existingSchema =
            buildSchema(
                // with UTC adjustment
                field("timestamp_col", Types.TimestampType.withZone(), true),
            )
        val incomingSchema =
            buildSchema(
                // without UTC adjustment
                field("timestamp_col", Types.TimestampType.withoutZone(), true),
            )

        val diff = comparator.compareSchemas(incomingSchema, existingSchema)

        // The type has changed in terms of shouldAdjustToUTC()
        assertThat(diff.updatedDataTypes).containsExactly("timestamp_col")
        assertThat(diff.newColumns).isEmpty()
        assertThat(diff.removedColumns).isEmpty()
        assertThat(diff.newlyOptionalColumns).isEmpty()
    }

    @Test
    fun testListTypeElementChanged() {
        val existingSchema =
            buildSchema(
                field(
                    "tags",
                    Types.ListType.ofRequired(
                        100,
                        Types.StringType.get(),
                    ),
                    true,
                ),
            )
        val incomingSchema =
            buildSchema(
                // The element type changed from String to Integer
                field(
                    "tags",
                    Types.ListType.ofRequired(
                        100,
                        Types.IntegerType.get(),
                    ),
                    true,
                ),
            )

        val diff = comparator.compareSchemas(incomingSchema, existingSchema)
        assertThat(diff.updatedDataTypes).containsExactly("tags")
        assertThat(diff.newColumns).isEmpty()
        assertThat(diff.removedColumns).isEmpty()
        assertThat(diff.newlyOptionalColumns).isEmpty()
    }

    @Test
    fun testListTypeElementOptionalityChanged() {
        val existingSchema =
            buildSchema(
                field(
                    "values",
                    Types.ListType.ofRequired(
                        101,
                        Types.StringType.get(),
                    ),
                    false,
                ),
            )
        val incomingSchema =
            buildSchema(
                // The element type is the same, but changed from required to optional
                field(
                    "values",
                    Types.ListType.ofOptional(
                        101,
                        Types.StringType.get(),
                    ),
                    false,
                ),
            )

        val diff = comparator.compareSchemas(incomingSchema, existingSchema)
        assertThat(diff.updatedDataTypes).containsExactly("values")
        assertThat(diff.newColumns).isEmpty()
        assertThat(diff.removedColumns).isEmpty()
        // Column itself didn't become optional, but the list element did ->
        // In this comparator's logic, that’s an updated data type.
        // There's no concept of a "newly optional element" in ColumnDiff,
        // so we won't see it in newlyOptionalColumns.
        assertThat(diff.newlyOptionalColumns).isEmpty()
    }

    @Test
    fun testStructFieldChanged() {
        val existingStructType =
            Types.StructType.of(
                field("nested_id", Types.IntegerType.get(), false),
                field("nested_name", Types.StringType.get(), true),
            )
        val incomingStructType =
            Types.StructType.of(
                // nested_id changes from Integer to Long
                field("nested_id", Types.LongType.get(), false),
                field("nested_name", Types.StringType.get(), true),
            )

        val existingSchema =
            buildSchema(
                field("user_info", existingStructType, true),
            )
        val incomingSchema =
            buildSchema(
                field("user_info", incomingStructType, true),
            )

        val diff = comparator.compareSchemas(incomingSchema, existingSchema)

        assertThat(diff.updatedDataTypes).containsExactly("user_info")
        assertThat(diff.newColumns).isEmpty()
        assertThat(diff.removedColumns).isEmpty()
        assertThat(diff.newlyOptionalColumns).isEmpty()
    }

    @Test
    fun testStructFieldRenamed() {
        val existingStructType =
            Types.StructType.of(
                field("nested_id", Types.IntegerType.get(), false),
            )
        val incomingStructType =
            Types.StructType.of(
                // field is renamed from nested_id -> nested_identifier
                field("nested_identifier", Types.IntegerType.get(), false),
            )

        val existingSchema =
            buildSchema(
                field("user_info", existingStructType, false),
            )
        val incomingSchema =
            buildSchema(
                field("user_info", incomingStructType, false),
            )

        val diff = comparator.compareSchemas(incomingSchema, existingSchema)

        // Because the struct fields differ by name, the entire struct is considered different
        assertThat(diff.updatedDataTypes).containsExactly("user_info")
        assertThat(diff.newColumns).isEmpty()
        assertThat(diff.removedColumns).isEmpty()
        assertThat(diff.newlyOptionalColumns).isEmpty()
    }

    @Test
    fun testMultipleDifferences() {
        val existingSchema =
            buildSchema(
                // 1) remove_me - to be removed
                field("remove_me", Types.StringType.get(), true),
                // 2) optional_to_required - stays optional in new, so no change
                field("keep_optional", Types.StringType.get(), true),
                // 3) required_to_optional
                field("make_optional", Types.IntegerType.get(), false),
                // 4) type change from INT to LONG
                field("type_change", Types.IntegerType.get(), false),
            )
        val incomingSchema =
            buildSchema(
                // remove_me is missing -> REMOVED
                field("keep_optional", Types.StringType.get(), true),
                field("make_optional", Types.IntegerType.get(), true),
                field("type_change", Types.LongType.get(), false),
                // brand_new is a new column
                field("brand_new", Types.FloatType.get(), true),
            )

        val diff = comparator.compareSchemas(incomingSchema, existingSchema)

        assertThat(diff.newColumns).containsExactly("brand_new")
        assertThat(diff.updatedDataTypes).containsExactly("type_change")
        assertThat(diff.removedColumns).containsExactly("remove_me")
        // make_optional changed from required -> optional
        assertThat(diff.newlyOptionalColumns).containsExactly("make_optional")
    }

    @Test
    fun testUnsupportedTypeBinary() {
        val existingSchema =
            buildSchema(
                field("binary_col", Types.BinaryType.get(), false),
            )
        val incomingSchema =
            buildSchema(
                field("binary_col", Types.BinaryType.get(), false),
            )

        // Currently, the code in typesAreEqual() throws an exception for TypeID.BINARY
        val exception =
            assertThrows(IllegalArgumentException::class.java) {
                comparator.compareSchemas(incomingSchema, existingSchema)
            }
        assertThat(exception.message)
            .contains(
                "Unsupported or unmapped Iceberg type: BINARY. Please implement handling if needed."
            )
    }

    @Test
    fun testUnsupportedTypeDecimal() {
        val existingSchema =
            buildSchema(
                field("decimal_col", Types.DecimalType.of(10, 2), false),
            )
        val incomingSchema =
            buildSchema(
                field("decimal_col", Types.DecimalType.of(10, 2), false),
            )

        // Should throw an exception for DECIMAL
        val exception =
            assertThrows(IllegalArgumentException::class.java) {
                comparator.compareSchemas(incomingSchema, existingSchema)
            }
        assertThat(exception.message)
            .contains(
                "Unsupported or unmapped Iceberg type: DECIMAL. Please implement handling if needed."
            )
    }
}
