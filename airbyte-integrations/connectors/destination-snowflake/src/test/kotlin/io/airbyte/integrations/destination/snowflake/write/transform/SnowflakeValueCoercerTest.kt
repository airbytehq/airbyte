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
import java.math.BigDecimal
import java.math.BigInteger
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
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
    fun testInvalidInteger() {
        val integerValue = IntegerValue(INT_MAX.plus(BigInteger.ONE))
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = integerValue,
                type = IntegerType,
                name = "name",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.ShouldNullify::class, result::class)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            (result as ValidationResult.ShouldNullify).reason
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
        assertEquals(ValidationResult.Valid, result)
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
        assertEquals(ValidationResult.ShouldNullify::class, result::class)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            (result as ValidationResult.ShouldNullify).reason
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
        assertEquals(ValidationResult.ShouldNullify::class, result::class)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            (result as ValidationResult.ShouldNullify).reason
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
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun testDecimalAtMaximumBoundary() {
        // Test decimal at maximum boundary for NUMBER(38,9) - 29 integer digits + 9 decimal digits
        val maxDecimal = NumberValue(BigDecimal("99999999999999999999999999999.999999999"))
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = maxDecimal,
                type = NumberType,
                name = "max_decimal",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun testDecimalAtMinimumBoundary() {
        // Test decimal at minimum boundary for NUMBER(38,9) - 29 integer digits + 9 decimal digits
        val minDecimal = NumberValue(BigDecimal("-99999999999999999999999999999.999999999"))
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = minDecimal,
                type = NumberType,
                name = "min_decimal",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun testDecimalExceedsMaximum() {
        // Test decimal exceeding NUMBER(38,9) maximum (30 integer digits)
        val oversizedDecimal = NumberValue(BigDecimal("999999999999999999999999999999.0"))
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = oversizedDecimal,
                type = NumberType,
                name = "oversized_decimal",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.ShouldNullify::class, result::class)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            (result as ValidationResult.ShouldNullify).reason
        )
    }

    @Test
    fun testDecimalExceedsMinimum() {
        // Test decimal exceeding NUMBER(38,9) minimum (30 integer digits)
        val undersizedDecimal = NumberValue(BigDecimal("-999999999999999999999999999999.0"))
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = undersizedDecimal,
                type = NumberType,
                name = "undersized_decimal",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.ShouldNullify::class, result::class)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            (result as ValidationResult.ShouldNullify).reason
        )
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
    fun testVerySmallPositiveNumber() {
        // Test very small positive number close to zero
        // 0.000000000001 has 12 decimal places, exceeds NUMBER(38,9) scale limit of 9
        // This should be nulled with NUMBER(38,9) (previously passed with FLOAT)
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
        assertTrue(result is ValidationResult.ShouldNullify)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            (result as ValidationResult.ShouldNullify).reason
        )
    }

    @Test
    fun testScientificNotationNumbers() {
        // Test numbers in scientific notation
        // 1.23E-10 = 0.000000000123 has 12 decimal places, exceeds NUMBER(38,9) scale limit of 9
        // This should be nulled with NUMBER(38,9) (previously passed with FLOAT)
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
        assertTrue(result is ValidationResult.ShouldNullify)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            (result as ValidationResult.ShouldNullify).reason
        )
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
    fun testDecimalAtExactBoundary() {
        // Test decimal at exact boundary values defined in DECIMAL_RANGE
        val exactMaxDecimal = NumberValue(DECIMAL_MAX)
        val exactMinDecimal = NumberValue(DECIMAL_MIN)

        val maxValue =
            EnrichedAirbyteValue(
                abValue = exactMaxDecimal,
                type = NumberType,
                name = "exact_max_decimal",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val minValue =
            EnrichedAirbyteValue(
                abValue = exactMinDecimal,
                type = NumberType,
                name = "exact_min_decimal",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        assertEquals(ValidationResult.Valid, coercer.validate(maxValue))
        assertEquals(ValidationResult.Valid, coercer.validate(minValue))
    }

    @Test
    fun testDecimalJustOutsideBoundary() {
        // Test decimal just outside the boundary
        val justOverMax = NumberValue(DECIMAL_MAX.add(BigDecimal.ONE))
        val justUnderMin = NumberValue(DECIMAL_MIN.subtract(BigDecimal.ONE))

        val overMaxValue =
            EnrichedAirbyteValue(
                abValue = justOverMax,
                type = NumberType,
                name = "over_max_decimal",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val underMinValue =
            EnrichedAirbyteValue(
                abValue = justUnderMin,
                type = NumberType,
                name = "under_min_decimal",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val overResult = coercer.validate(overMaxValue)
        val underResult = coercer.validate(underMinValue)

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
        // Test integers just outside the boundary
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
    fun testLargeIntegerAsNumber() {
        // Test 19-digit integer (like MongoDB NumberLong) that would have failed with FLOAT
        // This is the exact case from the bug report: submittime: 1740710103515266826
        val largeInteger = NumberValue(BigDecimal("1740710103515266826"))
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = largeInteger,
                type = NumberType,
                name = "large_integer_as_number",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun testMultipleLargeIntegersAsNumbers() {
        // Test multiple 19-digit integers from the bug report
        val testCases = listOf(
            "1740710103515266826",
            "1740710199999999999",
            "1234567890123456789"
        )

        testCases.forEach { value ->
            val numberValue = NumberValue(BigDecimal(value))
            val airbyteValue =
                EnrichedAirbyteValue(
                    abValue = numberValue,
                    type = NumberType,
                    name = "large_integer_$value",
                    changes = mutableListOf(),
                    airbyteMetaField = null,
                )

            val result = coercer.validate(airbyteValue)
            assertEquals(ValidationResult.Valid, result, "Failed for value: $value")
        }
    }

    @Test
    fun testDecimalWithExactly9DecimalPlaces() {
        // Test decimal with exactly 9 decimal places (should pass)
        val validDecimal = NumberValue(BigDecimal("1.123456789"))
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = validDecimal,
                type = NumberType,
                name = "valid_9_decimal_places",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun testDecimalWithMoreThan9DecimalPlaces() {
        // Test decimal with 10 significant decimal places (should be nulled)
        // Note: trailing zeros are stripped, so we need 10 non-zero decimal digits
        val invalidDecimal = NumberValue(BigDecimal("1.1234567891"))
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = invalidDecimal,
                type = NumberType,
                name = "invalid_10_decimal_places",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertTrue(result is ValidationResult.ShouldNullify)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            (result as ValidationResult.ShouldNullify).reason
        )
    }

    @Test
    fun testDecimalWith30IntegerDigits() {
        // Test decimal with 30 integer digits (exceeds MAX_INTEGER_DIGITS of 29, should be nulled)
        val invalidDecimal = NumberValue(BigDecimal("999999999999999999999999999999.0"))
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = invalidDecimal,
                type = NumberType,
                name = "invalid_30_integer_digits",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertTrue(result is ValidationResult.ShouldNullify)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            (result as ValidationResult.ShouldNullify).reason
        )
    }

    @Test
    fun testDecimalWithTrailingZeros() {
        // Test that trailing zeros don't cause false negatives
        // 1.2300000000 has 10 digits after decimal point, but only 2 significant decimal places
        val validDecimal = NumberValue(BigDecimal("1.2300000000"))
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = validDecimal,
                type = NumberType,
                name = "valid_with_trailing_zeros",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.Valid, result)
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
