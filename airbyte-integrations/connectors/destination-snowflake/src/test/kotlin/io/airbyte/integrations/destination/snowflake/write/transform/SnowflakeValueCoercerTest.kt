/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.transform

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Change
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

internal class SnowflakeValueCoercerTest {

    private lateinit var coercer: SnowflakeValueCoercer

    @BeforeEach
    fun setUp() {
        coercer = SnowflakeValueCoercer()
    }

    @Test
    fun testMap() {
        val airbyteValue = StringValue("test")
        val enrichedAirbyteValue =
            EnrichedAirbyteValue(
                abValue = airbyteValue,
                type = airbyteValue.airbyteType,
                name = "test",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )
        val result = coercer.map(enrichedAirbyteValue)
        assertEquals(enrichedAirbyteValue, result)
        assertEquals(airbyteValue, result.abValue)
    }

    @Test
    fun testMapUnionType() {
        val airbyteValue =
            ObjectValue(
                values = LinkedHashMap(),
            )
        val enrichedAirbyteValue =
            EnrichedAirbyteValue(
                abValue = airbyteValue,
                type = UnionType(options = setOf(StringType), isLegacyUnion = false),
                name = "test",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )
        val result = coercer.map(enrichedAirbyteValue)
        assertEquals(enrichedAirbyteValue, result)
        assertEquals(StringType, result.abValue.airbyteType)
    }

    @Test
    fun testValidateValidArray() {
        val arrayValue = ArrayValue(listOf(IntegerValue(1), IntegerValue(2), IntegerValue(3)))
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = arrayValue,
                type = ArrayType(FieldType(IntegerType, false)),
                name = "name",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )
        val result = coercer.validate(airbyteValue)
        assertEquals(airbyteValue, result)
    }

    @Test
    fun testValidateValidObject() {
        val values =
            LinkedHashMap<String, AirbyteValue>().apply {
                put("foo", IntegerValue(1))
                put("bar", IntegerValue(2))
            }
        val objectValue = ObjectValue(values)
        val properties =
            LinkedHashMap<String, FieldType>().apply {
                put("foo", FieldType(IntegerType, false))
                put("bar", FieldType(IntegerType, false))
            }
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = objectValue,
                type =
                    ObjectType(
                        properties = properties,
                        additionalProperties = false,
                        required = emptyList()
                    ),
                name = "name",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(airbyteValue, result)
    }

    @Test
    fun testValidInteger() {
        val integerValue = IntegerValue(10000.toBigInteger())
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = integerValue,
                type = IntegerType,
                name = "name",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(airbyteValue, result)
    }

    @Test
    fun testInvalidInteger() {
        val integerValue =
            IntegerValue("1${"0".repeat(INTEGER_PRECISION_LIMIT + 1)}".toBigInteger())
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = integerValue,
                type = IntegerType,
                name = "name",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(NullValue, result.abValue)
        assertEquals(1, result.changes.size)
        assertEquals(Change.NULLED, result.changes.first().change)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            result.changes.first().reason
        )
    }

    @Test
    fun testValidNumber() {
        val numberValue = NumberValue(10000.123.toBigDecimal())
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = numberValue,
                type = NumberType,
                name = "name",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(airbyteValue, result)
    }

    @ParameterizedTest
    @CsvSource(value = ["-3.4028235E38", "${Float.MAX_VALUE}"])
    fun testInvalidNumber(value: Float) {
        val numberValue = NumberValue(value.toBigDecimal())
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = numberValue,
                type = NumberType,
                name = "name",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(NullValue, result.abValue)
        assertEquals(1, result.changes.size)
        assertEquals(Change.NULLED, result.changes.first().change)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            result.changes.first().reason
        )
    }

    @Test
    fun testValidString() {
        val stringValue = StringValue("a valid string")
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = stringValue,
                type = StringType,
                name = "name",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(airbyteValue, result)
    }

    @Test
    fun testMaximumIntegerValue() {
        // Test the maximum 38-digit integer
        val maxInteger = IntegerValue("9".repeat(38).toBigInteger())
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = maxInteger,
                type = IntegerType,
                name = "max_int",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(airbyteValue, result)
    }

    @Test
    fun testIntegerExceedsPrecisionLimit() {
        // Test integer with 39 digits (exceeds 38 digit limit)
        val oversizedInteger = IntegerValue("1${"0".repeat(38)}".toBigInteger())
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = oversizedInteger,
                type = IntegerType,
                name = "oversized_int",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(NullValue, result.abValue)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            result.changes.first().reason
        )
    }

    @Test
    fun testNegativeMaximumIntegerValue() {
        // Test the minimum (most negative) 38-digit integer
        val minInteger = IntegerValue(("-" + "9".repeat(38)).toBigInteger())
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = minInteger,
                type = IntegerType,
                name = "min_int",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(airbyteValue, result)
    }

    @Test
    fun testFloatAtMaximumBoundary() {
        // Test float at maximum boundary (9.007199E15)
        val maxFloat = NumberValue(9.007199E15.toBigDecimal())
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = maxFloat,
                type = NumberType,
                name = "max_float",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(airbyteValue, result)
    }

    @Test
    fun testFloatAtMinimumBoundary() {
        // Test float at minimum boundary (-9.007199E15)
        val minFloat = NumberValue((-9.007199E15).toBigDecimal())
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = minFloat,
                type = NumberType,
                name = "min_float",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(airbyteValue, result)
    }

    @Test
    fun testFloatExceedsMaximum() {
        val oversizedFloat = NumberValue(1E20.toBigDecimal())
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = oversizedFloat,
                type = NumberType,
                name = "oversized_float",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(NullValue, result.abValue)
    }

    @Test
    fun testFloatExceedsMinimum() {
        val undersizedFloat = NumberValue((-1E20).toBigDecimal())
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = undersizedFloat,
                type = NumberType,
                name = "undersized_float",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(NullValue, result.abValue)
    }

    @Test
    fun testStringWithUnicodeCharacters() {
        // Test string with various unicode characters
        val unicodeString = StringValue("Hello 世界 🌍 Здравствуй мир नमस्ते संसार")
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = unicodeString,
                type = StringType,
                name = "unicode_string",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(airbyteValue, result)
    }

    @Test
    fun testStringWithSpecialCharacters() {
        // Test string with special characters that might cause issues
        val specialString = StringValue("Line1\nLine2\tTab\rCarriage\u0000Null")
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = specialString,
                type = StringType,
                name = "special_string",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(airbyteValue, result)
    }

    @Test
    fun testZeroValues() {
        // Test that zero values are handled correctly
        val zeroInt = IntegerValue(0.toBigInteger())
        val zeroFloat = NumberValue(0.0.toBigDecimal())

        val intValue =
            EnrichedAirbyteValue(
                abValue = zeroInt,
                type = IntegerType,
                name = "zero_int",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val floatValue =
            EnrichedAirbyteValue(
                abValue = zeroFloat,
                type = NumberType,
                name = "zero_float",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        assertEquals(intValue, coercer.validate(intValue))
        assertEquals(floatValue, coercer.validate(floatValue))
    }

    @Test
    fun testEmptyString() {
        val emptyString = StringValue("")
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = emptyString,
                type = StringType,
                name = "empty_string",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(airbyteValue, result)
    }

    @Test
    fun testStringWithOnlyWhitespace() {
        val whitespaceString = StringValue("   \t\n\r   ")
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = whitespaceString,
                type = StringType,
                name = "whitespace_string",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(airbyteValue, result)
    }

    @Test
    fun testVerySmallPositiveNumber() {
        // Test very small positive number close to zero
        val tinyNumber = NumberValue(0.000000000001.toBigDecimal())
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = tinyNumber,
                type = NumberType,
                name = "tiny_number",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(airbyteValue, result)
    }

    @Test
    fun testScientificNotationNumbers() {
        // Test numbers in scientific notation
        val scientificNumber = NumberValue(1.23E-10.toBigDecimal())
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = scientificNumber,
                type = NumberType,
                name = "scientific",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(airbyteValue, result)
    }

    @Test
    fun testDeeplyNestedObject() {
        // Test deeply nested object structure
        val deepObject =
            ObjectValue(
                LinkedHashMap<String, AirbyteValue>().apply {
                    put(
                        "level1",
                        ObjectValue(
                            LinkedHashMap<String, AirbyteValue>().apply {
                                put(
                                    "level2",
                                    ObjectValue(
                                        LinkedHashMap<String, AirbyteValue>().apply {
                                            put(
                                                "level3",
                                                ObjectValue(
                                                    LinkedHashMap<String, AirbyteValue>().apply {
                                                        put("level4", StringValue("deep value"))
                                                    }
                                                )
                                            )
                                        }
                                    )
                                )
                            }
                        )
                    )
                }
            )

        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = deepObject,
                type =
                    ObjectType(
                        properties = LinkedHashMap(),
                        additionalProperties = true,
                        required = emptyList()
                    ),
                name = "deep_object",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        // Should pass as long as total size is within limits
        assertEquals(airbyteValue, result)
    }

    @Test
    fun testLargeArrayOfNumbers() {
        // Test array with many elements
        val largeArray = ArrayValue((1..1000).map { IntegerValue(it.toBigInteger()) })

        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = largeArray,
                type = ArrayType(FieldType(IntegerType, false)),
                name = "large_array",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        // Should pass as long as total size is within limits
        assertEquals(airbyteValue, result)
    }
}
