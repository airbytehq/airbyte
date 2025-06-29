/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTypesComparator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTypesComparator.Companion.splitIntoParentAndLeaf
import org.apache.iceberg.Schema
import org.apache.iceberg.types.Type
import org.apache.iceberg.types.Types
import org.assertj.core.api.Assertions.assertThat
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.jupiter.api.Test

/** Comprehensive test suite for [IcebergTypesComparator]. */
class S3DataLakeTypesComparatorTest {

    private val comparator = IcebergTypesComparator()

    /**
     * Helper function to create a simple Iceberg [Types.NestedField].
     *
     * @param name the field name
     * @param type the field type
     * @param isOptional indicates whether the field is optional
     */
    private fun field(name: String, type: Type, isOptional: Boolean): Types.NestedField {
        val fieldId = name.hashCode() and 0x7fffffff // Simple, stable ID generator for test
        return if (isOptional) {
            Types.NestedField.optional(fieldId, name, type)
        } else {
            Types.NestedField.required(fieldId, name, type)
        }
    }

    /** Convenience function to build an Iceberg [Schema] from a list of fields. */
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
                // age changes from INTEGER -> LONG
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
                // name is previously required
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

        // The type changes with respect to shouldAdjustToUTC()
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
                // element type changed from String to Integer
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
                // same element type, but changed from required -> optional
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

        // This appears as a type update because list element optionality changed
        assertThat(diff.updatedDataTypes).containsExactly("values")
        assertThat(diff.newColumns).isEmpty()
        assertThat(diff.removedColumns).isEmpty()
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
                // renamed from nested_id -> nested_identifier
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

        // Because the struct’s fields differ by name, the entire struct is considered different
        assertThat(diff.updatedDataTypes).containsExactly("user_info")
        // The renamed field is effectively a new column in nested context
        assertThat(diff.newColumns).containsExactly("user_info~nested_identifier")
        assertThat(diff.removedColumns).isEmpty()
        assertThat(diff.newlyOptionalColumns).isEmpty()
    }

    @Test
    fun testStructFieldAdded() {
        val existingStructType =
            Types.StructType.of(
                field("nested_id", Types.IntegerType.get(), false),
                field(
                    "nested_struct",
                    Types.StructType.of(
                        field("nested_struct_id", Types.IntegerType.get(), false),
                    ),
                    false,
                ),
            )
        val incomingStructType =
            Types.StructType.of(
                field("nested_id", Types.IntegerType.get(), false),
                field("new_id", Types.IntegerType.get(), false),
                field(
                    "nested_struct",
                    Types.StructType.of(
                        field("nested_struct_id", Types.IntegerType.get(), false),
                        field("nested_struct_new_id", Types.IntegerType.get(), false),
                    ),
                    false,
                ),
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

        assertThat(diff.updatedDataTypes).isEmpty()
        assertThat(diff.newColumns)
            .containsExactlyInAnyOrder(
                "user_info~new_id",
                "user_info~nested_struct~nested_struct_new_id",
            )
        assertThat(diff.removedColumns).isEmpty()
        assertThat(diff.newlyOptionalColumns).isEmpty()
    }

    @Test
    fun testMultipleDifferences() {
        val existingSchema =
            buildSchema(
                // 1) remove_me -> will be removed
                field("remove_me", Types.StringType.get(), true),
                // 2) keep_optional -> remains as is
                field("keep_optional", Types.StringType.get(), true),
                // 3) make_optional -> changes from required to optional
                field("make_optional", Types.IntegerType.get(), false),
                // 4) type_change -> changes from INT to LONG
                field("type_change", Types.IntegerType.get(), false),
            )
        val incomingSchema =
            buildSchema(
                // remove_me is missing => REMOVED
                field("keep_optional", Types.StringType.get(), true),
                field("make_optional", Types.IntegerType.get(), true),
                field("type_change", Types.LongType.get(), false),
                // brand_new is newly added
                field("brand_new", Types.FloatType.get(), true),
            )

        val diff = comparator.compareSchemas(incomingSchema, existingSchema)

        assertThat(diff.newColumns).containsExactly("brand_new")
        assertThat(diff.updatedDataTypes).containsExactly("type_change")
        assertThat(diff.removedColumns).containsExactly("remove_me")
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

        // The code in typesAreEqual() throws for TypeID.BINARY
        assertThatThrownBy { comparator.compareSchemas(incomingSchema, existingSchema) }
            .isInstanceOf(IllegalArgumentException::class.java)
            .hasMessageContaining("Unsupported or unmapped Iceberg type: BINARY")
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

        // The code in typesAreEqual() throws for TypeID.DECIMAL
        assertThatThrownBy { comparator.compareSchemas(incomingSchema, existingSchema) }
            .isInstanceOf(IllegalArgumentException::class.java)
            .hasMessageContaining("Unsupported or unmapped Iceberg type: DECIMAL")
    }

    @Test
    fun testSplitWithNoSeparatorReturnsEmptyParentAndFullNameAsLeaf() {
        val (parent, leaf) = splitIntoParentAndLeaf("field")
        assertThat(parent).isEmpty()
        assertThat(leaf).isEqualTo("field")
    }

    @Test
    fun testSplitWithSingleSeparatorReturnsExpectedParentAndLeaf() {
        val (parent, leaf) = splitIntoParentAndLeaf("outer~field")
        assertThat(parent).isEqualTo("outer")
        assertThat(leaf).isEqualTo("field")
    }

    @Test
    fun testSplitWithMultipleSeparatorsUsesLastSeparatorForSplitting() {
        // "outer~inner~field" => parent = "outer~inner", leaf = "field"
        val (parent, leaf) = splitIntoParentAndLeaf("outer~inner~field")
        assertThat(parent).isEqualTo("outer~inner")
        assertThat(leaf).isEqualTo("field")
    }

    @Test
    fun testSplitStringEndingInSeparatorHasEmptyLeaf() {
        // "outer~inner~" => parent = "outer~inner", leaf = ""
        val (parent, leaf) = splitIntoParentAndLeaf("outer~inner~")
        assertThat(parent).isEqualTo("outer~inner")
        assertThat(leaf).isEmpty()
    }

    @Test
    fun testSplitStringBeginningWithSeparatorHasEmptyParent() {
        // "~innerField" => parent = "", leaf = "innerField"
        val (parent, leaf) = splitIntoParentAndLeaf("~innerField")
        assertThat(parent).isEmpty()
        assertThat(leaf).isEqualTo("innerField")
    }

    @Test
    fun testSplitStringThatIsOnlySeparator() {
        // "~" => parent = "", leaf = ""
        val (parent, leaf) = splitIntoParentAndLeaf("~")
        assertThat(parent).isEmpty()
        assertThat(leaf).isEmpty()
    }

    @Test
    fun testSplitEmptyString() {
        val (parent, leaf) = splitIntoParentAndLeaf("")
        assertThat(parent).isEmpty()
        assertThat(leaf).isEmpty()
    }
}
