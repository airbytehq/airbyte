/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
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
import io.airbyte.integrations.destination.snowflake.spec.NumberDataType
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
        coercer =
            SnowflakeValueCoercer(
                mockk {
                    every { legacyRawTablesOnly } returns false
                    every { numberDataTypeConversion } returns NumberDataType.FLOAT
                }
            )
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

    // NUMBER(38,9) mode
    private fun numericModeCoercer(rawMode: Boolean = false) =
        SnowflakeValueCoercer(
            mockk {
                every { legacyRawTablesOnly } returns rawMode
                every { numberDataTypeConversion } returns NumberDataType.NUMBER_38_9
            }
        )

    private fun enrichedNumber(value: String) =
        EnrichedAirbyteValue(
            abValue = NumberValue(BigDecimal(value)),
            type = NumberType,
            name = "number_col",
            changes = mutableListOf(),
            airbyteMetaField = null,
        )

    @Test
    fun testNumberDataTypeToggleControlsNumberValidation() {
        // 2^53 + 1: the first integer a FLOAT (64-bit double) cannot represent.
        val value = "9007199254740993"

        // FLOAT mode (the default fixture) loses the last digit and flags the row.
        val floatResult = coercer.validate(enrichedNumber(value))
        assertEquals(ValidationResult.ShouldTruncate::class, floatResult::class)
        assertEquals(
            BigDecimal.valueOf(9.007199254740992E15),
            ((floatResult as ValidationResult.ShouldTruncate).truncatedValue as NumberValue).value
        )

        // NUMBER(38,9) mode keeps the exact value with no change flag.
        assertEquals(ValidationResult.Valid, numericModeCoercer().validate(enrichedNumber(value)))
    }

    @Test
    fun testNumericModeMaximumValueIsValid() {
        // 29 digits before the decimal point and 9 after: the largest NUMBER(38,9) value,
        // which is still valid.
        val max = "9".repeat(29) + "." + "9".repeat(9)
        assertEquals(ValidationResult.Valid, numericModeCoercer().validate(enrichedNumber(max)))
        assertEquals(ValidationResult.Valid, numericModeCoercer().validate(enrichedNumber("-$max")))
    }

    @Test
    fun testNumericModeThirtyIntegerDigitsAreNullified() {
        // Values with more than 29 digits before the decimal point are set to NULL.
        val tooBig = "1" + "0".repeat(29)
        listOf(tooBig, "-$tooBig").forEach { value ->
            val result = numericModeCoercer().validate(enrichedNumber(value))
            assertEquals(ValidationResult.ShouldNullify::class, result::class)
            assertEquals(
                AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
                (result as ValidationResult.ShouldNullify).reason
            )
        }
    }

    @Test
    fun testNumericModeExcessDecimalPlacesRoundedHalfUp() {
        // Values with more than 9 decimal places are truncated to 9, rounding half away from
        // zero (HALF_UP) to match Snowflake's cast semantics.
        val result = numericModeCoercer().validate(enrichedNumber("0.1234567885"))
        assertEquals(ValidationResult.ShouldTruncate::class, result::class)
        val truncated = result as ValidationResult.ShouldTruncate
        assertEquals(BigDecimal("0.123456789"), (truncated.truncatedValue as NumberValue).value)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            truncated.reason
        )

        // Negative values also round away from zero.
        val negativeResult = numericModeCoercer().validate(enrichedNumber("-0.1234567885"))
        assertEquals(
            BigDecimal("-0.123456789"),
            ((negativeResult as ValidationResult.ShouldTruncate).truncatedValue as NumberValue)
                .value
        )
    }

    @Test
    fun testNumericModeTrailingZerosBeyondScaleAreNotFlagged() {
        // Scale > 9 but numerically unchanged by rounding: not a truncation.
        assertEquals(
            ValidationResult.Valid,
            numericModeCoercer().validate(enrichedNumber("1.0000000000"))
        )
    }

    @Test
    fun testNumericModeRoundingCarryIntoThirtiethDigitIsNullified() {
        // Rounding the 10th decimal up carries through all 29 nines into a 30th integer digit.
        // NUMERIC(38,9) can only store 29 digits before the decimal point, so the rounded
        // value is set to NULL.
        val value = "9".repeat(29) + ".9999999995"
        val result = numericModeCoercer().validate(enrichedNumber(value))
        assertEquals(ValidationResult.ShouldNullify::class, result::class)
    }

    @Test
    fun testNumericModeInRawTablesModeKeepsFloatValidation() {
        // The toggle has no effect in legacy raw tables mode: values still go through the FLOAT
        // validation, so 2^53 + 1 is truncated exactly as in FLOAT mode.
        val result = numericModeCoercer(rawMode = true).validate(enrichedNumber("9007199254740993"))
        assertEquals(ValidationResult.ShouldTruncate::class, result::class)
        assertEquals(
            BigDecimal.valueOf(9.007199254740992E15),
            ((result as ValidationResult.ShouldTruncate).truncatedValue as NumberValue).value
        )
    }
}
