/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write.transform

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
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.math.BigDecimal
import java.math.BigInteger
import java.time.OffsetDateTime
import java.time.ZoneOffset
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class PostgresValueCoercerTest {

    private lateinit var coercer: PostgresValueCoercer

    @BeforeEach
    fun setUp() {
        coercer = PostgresValueCoercer()
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
        val integerValue = IntegerValue(BIGINT_MAX.plus(BigInteger.ONE))
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
    fun testIntegerBelowMinimum() {
        val integerValue = IntegerValue(BIGINT_MIN.minus(BigInteger.ONE))
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

    @Test
    fun testInvalidNumberExceedsMaximum() {
        val numberValue = NumberValue(NUMERIC_MAX.multiply(BigDecimal.TEN))
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
    fun testInvalidNumberBelowMinimum() {
        val numberValue = NumberValue(NUMERIC_MIN.multiply(BigDecimal.TEN))
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
    fun testInvalidStringTooLarge() {
        // Create a string that would exceed TEXT_LIMIT_BYTES when considering UTF-8 encoding
        // We multiply by 4 (max bytes per UTF-8 char), so any string longer than TEXT_LIMIT_BYTES /
        // 4
        // will be rejected
        val largeString = StringValue("a".repeat(TEXT_LIMIT_BYTES / 4 + 1))
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = largeString,
                type = StringType,
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
    fun testValidStringAtBoundary() {
        // Test string exactly at the boundary (TEXT_LIMIT_BYTES / 4 characters)
        val boundaryString = StringValue("a".repeat(TEXT_LIMIT_BYTES / 4))
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = boundaryString,
                type = StringType,
                name = "name",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun testMaximumBigIntValue() {
        // Test the maximum BIGINT value
        val maxInteger = IntegerValue(BIGINT_MAX)
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
    fun testMinimumBigIntValue() {
        // Test the minimum BIGINT value
        val minInteger = IntegerValue(BIGINT_MIN)
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
    fun testValidTimestampWithTimezone() {
        // Test valid timestamp with timezone
        val validTimestamp = OffsetDateTime.of(2023, 1, 1, 12, 0, 0, 0, ZoneOffset.UTC)
        val timestampValue = TimestampWithTimezoneValue(validTimestamp)
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = timestampValue,
                type = TimestampTypeWithTimezone,
                name = "timestamp",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun testInvalidTimestampWithTimezoneExceedsMaximum() {
        // Test timestamp beyond PostgreSQL's maximum (294276 AD)
        // Using epoch second beyond TIMESTAMP_MAX_EPOCH_SECONDS
        val invalidTimestamp =
            OffsetDateTime.ofInstant(
                java.time.Instant.ofEpochSecond(TIMESTAMP_MAX_EPOCH_SECONDS + 1),
                ZoneOffset.UTC
            )
        val timestampValue = TimestampWithTimezoneValue(invalidTimestamp)
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = timestampValue,
                type = TimestampTypeWithTimezone,
                name = "timestamp",
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
    fun testInvalidTimestampWithTimezoneBelowMinimum() {
        // Test timestamp before PostgreSQL's minimum (4713 BC)
        // Using epoch second below TIMESTAMP_MIN_EPOCH_SECONDS
        val invalidTimestamp =
            OffsetDateTime.ofInstant(
                java.time.Instant.ofEpochSecond(TIMESTAMP_MIN_EPOCH_SECONDS - 1),
                ZoneOffset.UTC
            )
        val timestampValue = TimestampWithTimezoneValue(invalidTimestamp)
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = timestampValue,
                type = TimestampTypeWithTimezone,
                name = "timestamp",
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
    fun testValidTimestampWithoutTimezone() {
        // Test valid timestamp without timezone
        val validTimestamp = java.time.LocalDateTime.of(2023, 1, 1, 12, 0, 0, 0)
        val timestampValue = TimestampWithoutTimezoneValue(validTimestamp)
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = timestampValue,
                type = TimestampTypeWithoutTimezone,
                name = "timestamp",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun testTimestampAtMaximumBoundary() {
        // Test timestamp at exactly the maximum boundary
        val maxTimestamp =
            OffsetDateTime.ofInstant(
                java.time.Instant.ofEpochSecond(TIMESTAMP_MAX_EPOCH_SECONDS),
                ZoneOffset.UTC
            )
        val timestampValue = TimestampWithTimezoneValue(maxTimestamp)
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = timestampValue,
                type = TimestampTypeWithTimezone,
                name = "timestamp",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun testTimestampAtMinimumBoundary() {
        // Test timestamp at exactly the minimum boundary
        val minTimestamp =
            OffsetDateTime.ofInstant(
                java.time.Instant.ofEpochSecond(TIMESTAMP_MIN_EPOCH_SECONDS),
                ZoneOffset.UTC
            )
        val timestampValue = TimestampWithTimezoneValue(minTimestamp)
        val airbyteValue =
            EnrichedAirbyteValue(
                abValue = timestampValue,
                type = TimestampTypeWithTimezone,
                name = "timestamp",
                changes = mutableListOf(),
                airbyteMetaField = null,
            )

        val result = coercer.validate(airbyteValue)
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
        assertEquals(ValidationResult.Valid, result)
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
        assertEquals(ValidationResult.Valid, result)
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
        assertEquals(ValidationResult.Valid, result)
    }
}
