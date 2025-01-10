/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import org.apache.iceberg.types.Type
import org.apache.iceberg.types.Type.TypeID.DOUBLE
import org.apache.iceberg.types.Type.TypeID.LONG
import org.apache.iceberg.types.Type.TypeID.TIMESTAMP_NANO
import org.apache.iceberg.types.Types
import org.apache.iceberg.types.Types.TimestampType
import org.assertj.core.api.Assertions.assertThat
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.jupiter.api.Test

/** Comprehensive test suite for [S3DataLakeSuperTypeFinder]. */
class S3DataLakeSuperTypeFinderTest {

    private val superTypeFinder = S3DataLakeSuperTypeFinder(S3DataLakeTypesComparator())

    @Test
    fun testIdenticalPrimitiveTypes() {
        val intType = Types.IntegerType.get()
        val result = superTypeFinder.findSuperType(intType, intType, "column_name")

        // They are "equal" => expect the existing type to be returned
        assertThat(result).isSameAs(intType)
    }

    @Test
    fun testIdenticalTimestampTypesWithZone() {
        val tsWithZone = TimestampType.withZone()
        val result = superTypeFinder.findSuperType(tsWithZone, tsWithZone, "column_name")

        assertThat(result).isSameAs(tsWithZone)
    }

    @Test
    fun testDifferentTimestampZoneThrows() {
        val tsWithZone = TimestampType.withZone()
        val tsWithoutZone = TimestampType.withoutZone()

        assertThatThrownBy {
                superTypeFinder.findSuperType(tsWithZone, tsWithoutZone, "column_name")
            }
            .isInstanceOf(IllegalArgumentException::class.java)
            .hasMessageContaining("Conversion for column \"column_name\" between")
    }

    @Test
    fun testIntToLongPromotion() {
        val intType = Types.IntegerType.get()
        val longType = Types.LongType.get()

        val result = superTypeFinder.findSuperType(intType, longType, "column_name")
        // INT -> LONG => LONG is the supertype
        assertThat(result.typeId()).isEqualTo(LONG)
    }

    @Test
    fun testFloatToDoublePromotion() {
        val floatType = Types.FloatType.get()
        val doubleType = Types.DoubleType.get()

        val result = superTypeFinder.findSuperType(floatType, doubleType, "column_name")
        assertThat(result.typeId()).isEqualTo(DOUBLE)
    }

    @Test
    fun testIntToDoubleIsNotAllowed() {
        val intType = Types.IntegerType.get()
        val doubleType = Types.DoubleType.get()

        // By default, TypeUtil.isPromotionAllowed(int, double) returns false
        assertThatThrownBy { superTypeFinder.findSuperType(intType, doubleType, "column_name") }
            .isInstanceOf(IllegalArgumentException::class.java)
            .hasMessageContaining(
                "Conversion for column \"column_name\" between int and double is not allowed."
            )
    }

    @Test
    fun testPrimitiveToNonPrimitiveThrows() {
        val intType = Types.IntegerType.get()
        val structType =
            Types.StructType.of(
                Types.NestedField.optional(1, "field", Types.StringType.get()),
            )

        // Attempting to combine int (primitive) with struct (non-primitive) => error
        assertThatThrownBy { superTypeFinder.findSuperType(intType, structType, "column_name") }
            .isInstanceOf(IllegalArgumentException::class.java)
            .hasMessageContaining(
                "Conversion for column \"column_name\" between int and struct<1: field: optional string> is not allowed."
            )
    }

    @Test
    fun testNonPrimitiveToPrimitiveThrows() {
        val structType =
            Types.StructType.of(
                Types.NestedField.optional(1, "field", Types.StringType.get()),
            )
        val intType = Types.IntegerType.get()

        assertThatThrownBy { superTypeFinder.findSuperType(structType, intType, "column_name") }
            .isInstanceOf(IllegalArgumentException::class.java)
            .hasMessageContaining(
                "Conversion for column \"column_name\" between struct<1: field: optional string> and int is not allowed."
            )
    }

    @Test
    fun testBinaryIsUnsupported() {
        val binaryType = Types.BinaryType.get()
        val intType = Types.IntegerType.get()

        // Fails in validateTypeIds => BINARY is not supported
        assertThatThrownBy { superTypeFinder.findSuperType(binaryType, intType, "column_name") }
            .isInstanceOf(IllegalArgumentException::class.java)
            .hasMessageContaining(
                "Conversion for column \"column_name\" between binary and int is not allowed."
            )
    }

    @Test
    fun testDecimalIsUnsupported() {
        val decimalType = Types.DecimalType.of(10, 2)
        val intType = Types.IntegerType.get()

        // Fails in validateTypeIds => DECIMAL is not supported
        assertThatThrownBy { superTypeFinder.findSuperType(decimalType, intType, "column_name") }
            .isInstanceOf(IllegalArgumentException::class.java)
            .hasMessageContaining(
                "Conversion for column \"column_name\" between decimal(10, 2) and int is not allowed."
            )
    }

    @Test
    fun testFixedIsUnsupported() {
        val fixedType = Types.FixedType.ofLength(16)
        val intType = Types.IntegerType.get()

        // Fails in validateTypeIds => FIXED is not supported
        assertThatThrownBy { superTypeFinder.findSuperType(fixedType, intType, "column_name") }
            .isInstanceOf(IllegalArgumentException::class.java)
            .hasMessageContaining(
                "Conversion for column \"column_name\" between fixed[16] and int is not allowed."
            )
    }

    @Test
    fun testUUIDIsUnsupported() {
        val uuidType = Types.UUIDType.get()
        val intType = Types.IntegerType.get()

        // Fails in validateTypeIds => UUID is not supported
        assertThatThrownBy { superTypeFinder.findSuperType(uuidType, intType, "column_name") }
            .isInstanceOf(IllegalArgumentException::class.java)
            .hasMessageContaining(
                "Conversion for column \"column_name\" between uuid and int is not allowed."
            )
    }

    @Test
    fun testTimestampNanoIsUnsupported() {
        // For illustration, let's assume TypeID.TIMESTAMP_NANO is an unsupported extension.
        // This is a hypothetical scenario in some Iceberg versions.
        // We'll fake it with reflection or a custom type (if needed).
        // Alternatively, just a conceptual test that TIMESTAMP_NANO is not allowed.

        // We'll mimic that with a custom type object for demonstration:
        val nanoTimestamp =
            object : Type.PrimitiveType() {
                override fun typeId() = TIMESTAMP_NANO
                override fun isPrimitiveType() = true
            }
        val normalTimestamp = TimestampType.withoutZone()

        assertThatThrownBy {
                superTypeFinder.findSuperType(nanoTimestamp, normalTimestamp, "column_name")
            }
            .isInstanceOf(IllegalArgumentException::class.java)
    }

    @Test
    fun testPromotionIsNotAllowedByIceberg() {
        // Suppose the user tries to do INT -> FLOAT
        val intType = Types.IntegerType.get()
        val floatType = Types.FloatType.get()

        // By default, TypeUtil.isPromotionAllowed(int, float) is false
        assertThatThrownBy { superTypeFinder.findSuperType(intType, floatType, "column_name") }
            .isInstanceOf(IllegalArgumentException::class.java)
            .hasMessageContaining(
                "Conversion for column \"column_name\" between int and float is not allowed."
            )
    }
}
