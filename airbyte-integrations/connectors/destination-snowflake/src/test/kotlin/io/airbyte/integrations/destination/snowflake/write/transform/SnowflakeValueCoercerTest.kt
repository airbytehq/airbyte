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
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.mockk.every
import io.mockk.mockk
import java.math.BigDecimal
import java.math.BigInteger
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class SnowflakeValueCoercerTest {

    private lateinit var coercer: SnowflakeValueCoercer

    @BeforeEach
    fun setUp() {
        coercer = SnowflakeValueCoercer(mockk { every { legacyRawTablesOnly } returns false })
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
        assertEquals(ValidationResult.Valid, result)
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
        assertEquals(ValidationResult.Valid, result)
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
        assertEquals(ValidationResult.Valid, result)
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
        assertEquals(ValidationResult.Valid, result)
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
        assertEquals(ValidationResult.Valid, result)
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
        assertEquals(ValidationResult.Valid, result)
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
        assertEquals(ValidationResult.Valid, result)
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
        assertEquals(ValidationResult.Valid, result)
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
        assertEquals(ValidationResult.Valid, result)
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
        assertEquals(ValidationResult.Valid, result)
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
        assertEquals(ValidationResult.Valid, result)
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

        assertEquals(ValidationResult.Valid, coercer.validate(intValue))
        assertEquals(ValidationResult.Valid, coercer.validate(floatValue))
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
        assertEquals(ValidationResult.Valid, result)
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
        assertEquals(ValidationResult.Valid, result)
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
        assertEquals(ValidationResult.Valid, result)
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
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun testStringJustUnderSizeLimit() {
        val largeString = StringValue("a".repeat(VARCHAR_LIMIT_BYTES))
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = largeString,
                type = StringType,
                name = "large_string",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun testStringAtExactSizeLimit() {
        // Test string at exactly the 16777216 character limit
        val exactLimitString = StringValue("a".repeat(VARCHAR_LIMIT_BYTES))
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = exactLimitString,
                type = StringType,
                name = "exact_limit_string",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        // This should still be valid as each 'a' is 1 byte
        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun testVariantJustUnderSizeLimit() {
        // Test ObjectValue just under the VARIANT_LIMIT_BYTES limit
        // When serialized to JSON, the format will be {"field":"aaa...aaa"}
        // The overhead for {"field":""} is 12 bytes, so we need VARIANT_LIMIT_BYTES - 12 characters
        // in the value
        val stringLength = VARIANT_LIMIT_BYTES - 12
        val largeObject =
            ObjectValue(
                LinkedHashMap<String, AirbyteValue>().apply {
                    put("field", StringValue("a".repeat(stringLength)))
                }
            )
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = largeObject,
                type =
                    ObjectType(
                        properties = LinkedHashMap(),
                        additionalProperties = true,
                        required = emptyList()
                    ),
                name = "large_variant",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun testVariantAtExactSizeLimit() {
        // Test ObjectValue at exactly the VARIANT_LIMIT_BYTES byte limit
        // When serialized to JSON, the format will be {"field":"aaa...aaa"}
        // The overhead for {"field":""} is 12 bytes, so we need VARIANT_LIMIT_BYTES - 12
        // characters in the value
        val stringLength = VARIANT_LIMIT_BYTES - 12
        val objectValue =
            ObjectValue(
                LinkedHashMap<String, AirbyteValue>().apply {
                    put("field", StringValue("a".repeat(stringLength)))
                }
            )
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = objectValue,
                type =
                    ObjectType(
                        properties = LinkedHashMap(),
                        additionalProperties = true,
                        required = emptyList()
                    ),
                name = "exact_limit_variant",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        // This should still be valid as each 'a' is 1 byte and total is at the limit
        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun testFloatAtExactBoundary() {
        // Test float at exact boundary values defined in FLOAT_RANGE
        val exactMaxFloat = NumberValue(FLOAT_MAX)
        val exactMinFloat = NumberValue(FLOAT_MIN)

        val maxValue =
            EnrichedAirbyteValue(
                abValue = exactMaxFloat,
                type = NumberType,
                name = "exact_max_float",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val minValue =
            EnrichedAirbyteValue(
                abValue = exactMinFloat,
                type = NumberType,
                name = "exact_min_float",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        assertEquals(ValidationResult.Valid, coercer.validate(maxValue))
        assertEquals(ValidationResult.Valid, coercer.validate(minValue))
    }

    @Test
    fun testFloatJustOutsideBoundary() {
        // Test float just outside the boundary - these should now be truncated instead of nullified
        val justOverMax = NumberValue(FLOAT_MAX.add(BigDecimal.ONE))
        val justUnderMin = NumberValue(FLOAT_MIN.subtract(BigDecimal.ONE))

        val overMaxValue =
            EnrichedAirbyteValue(
                abValue = justOverMax,
                type = NumberType,
                name = "over_max_float",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val underMinValue =
            EnrichedAirbyteValue(
                abValue = justUnderMin,
                type = NumberType,
                name = "under_min_float",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val overResult = coercer.validate(overMaxValue)
        val underResult = coercer.validate(underMinValue)

        // Values just outside boundary should be truncated to fit
        assertEquals(ValidationResult.ShouldNullify::class, overResult::class)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            (overResult as ValidationResult.ShouldNullify).reason
        )
        assertEquals(ValidationResult.ShouldNullify::class, underResult::class)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            (underResult as ValidationResult.ShouldNullify).reason
        )
    }

    @Test
    fun testIntegerAtExactBoundary() {
        // Test integers at exact boundary values
        val exactMaxInt = IntegerValue(INT_MAX)
        val exactMinInt = IntegerValue(INT_MIN)

        val maxValue =
            EnrichedAirbyteValue(
                abValue = exactMaxInt,
                type = IntegerType,
                name = "exact_max_int",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val minValue =
            EnrichedAirbyteValue(
                abValue = exactMinInt,
                type = IntegerType,
                name = "exact_min_int",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        assertEquals(ValidationResult.Valid, coercer.validate(maxValue))
        assertEquals(ValidationResult.Valid, coercer.validate(minValue))
    }

    @Test
    fun testIntegerJustOutsideBoundary() {
        // Test integers just outside the boundary - these should now be truncated instead of
        // nullified
        val justOverMax = IntegerValue(INT_MAX.add(BigInteger.ONE))
        val justUnderMin = IntegerValue(INT_MIN.subtract(BigInteger.ONE))

        val overMaxValue =
            EnrichedAirbyteValue(
                abValue = justOverMax,
                type = IntegerType,
                name = "over_max_int",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val underMinValue =
            EnrichedAirbyteValue(
                abValue = justUnderMin,
                type = IntegerType,
                name = "under_min_int",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val overResult = coercer.validate(overMaxValue)
        val underResult = coercer.validate(underMinValue)

        // Values just outside boundary should be truncated to fit
        assertEquals(ValidationResult.ShouldNullify::class, overResult::class)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            (overResult as ValidationResult.ShouldNullify).reason
        )
        assertEquals(ValidationResult.ShouldNullify::class, underResult::class)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            (underResult as ValidationResult.ShouldNullify).reason
        )
    }

    @Test
    fun testNullValue() {
        // Test that null values pass through without changes
        val nullValue = NullValue
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = nullValue,
                type = StringType,
                name = "null_value",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun testStringWithMultiByteCharactersNearLimit() {
        // Test string with multi-byte UTF-8 characters
        // Each emoji is 4 bytes, so we need fewer characters to hit the limit
        val multiByteCount = MAX_UTF_8_VARCHAR_LENGTH_UNDER_LIMIT
        val emojiString = StringValue("🎉".repeat(multiByteCount))

        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = emojiString,
                type = StringType,
                name = "emoji_string",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun testFloatWithExcessivePrecisionTruncated() {
        // Test that a large value with many digits gets truncated to fit within range
        // Example: 1740710103515266826 (19 digits) should be truncated to fit
        val highPrecisionValue = NumberValue(BigDecimal("1740710103515266826"))
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = highPrecisionValue,
                type = NumberType,
                name = "high_precision_float",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)

        // Should be truncated, not nullified
        assertEquals(ValidationResult.ShouldTruncate::class, result::class)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            (result as ValidationResult.ShouldTruncate).reason
        )

        // The truncated value should be within range
        val truncatedValue = result.truncatedValue as NumberValue
        // note that we've lost some precision
        assertEquals(BigDecimal.valueOf(1.7407101035152668E18), truncatedValue.value)
    }

    @Test
    fun testVariantWithMultiByteCharactersNearLimit() {
        // Test ObjectValue with multi-byte UTF-8 characters
        // Each emoji is 4 bytes, so we need fewer characters to hit the limit
        // JSON overhead for {"field":""} is 12 bytes, so we account for that
        val multiByteCount = (VARIANT_LIMIT_BYTES - 12) / 4
        val emojiObject =
            ObjectValue(
                LinkedHashMap<String, AirbyteValue>().apply {
                    put("field", StringValue("🎉".repeat(multiByteCount)))
                }
            )

        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = emojiObject,
                type =
                    ObjectType(
                        properties = LinkedHashMap(),
                        additionalProperties = true,
                        required = emptyList()
                    ),
                name = "emoji_variant",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.Valid, result)
    }
}
