/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.write.transform

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
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
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import com.fasterxml.jackson.databind.node.NullNode
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class RedshiftValueCoercerTest {

    private lateinit var coercer: RedshiftValueCoercer

    @BeforeEach
    fun setUp() {
        coercer = RedshiftValueCoercer()
    }

    // ================================================================
    // map() tests
    // ================================================================

    @Test
    fun `map passes through non-union types unchanged`() {
        val value = StringValue("hello")
        val enriched = enriched(value, StringType)

        val result = coercer.map(enriched)

        assertEquals(value, result.abValue)
    }

    @Test
    fun `map serializes union type values to string`() {
        val value = ObjectValue(linkedMapOf("key" to StringValue("val")))
        val enriched =
            enriched(value, UnionType(options = setOf(StringType), isLegacyUnion = false))

        val result = coercer.map(enriched)

        assertTrue(result.abValue is StringValue)
        assertEquals(StringType, result.abValue.airbyteType)
    }

    @Test
    fun `map serializes unknown type values to string`() {
        val value = IntegerValue(42)
        val enriched = enriched(value, UnknownType(schema = NullNode.instance))

        val result = coercer.map(enriched)

        assertTrue(result.abValue is StringValue)
        assertEquals("42", (result.abValue as StringValue).value)
    }

    @Test
    fun `map preserves NullValue for union types`() {
        val enriched =
            enriched(NullValue, UnionType(options = setOf(StringType), isLegacyUnion = false))

        val result = coercer.map(enriched)

        assertEquals(NullValue, result.abValue)
    }

    // ================================================================
    // validate() — Integer (BIGINT) tests
    // ================================================================

    @Test
    fun `validate accepts valid integer`() {
        val result = coercer.validate(enriched(IntegerValue(10000.toBigInteger()), IntegerType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts integer at BIGINT_MAX boundary`() {
        val result = coercer.validate(enriched(IntegerValue(BIGINT_MAX), IntegerType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts integer at BIGINT_MIN boundary`() {
        val result = coercer.validate(enriched(IntegerValue(BIGINT_MIN), IntegerType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate nullifies integer above BIGINT_MAX`() {
        val result =
            coercer.validate(enriched(IntegerValue(BIGINT_MAX + BigInteger.ONE), IntegerType))
        assertShouldNullify(result)
    }

    @Test
    fun `validate nullifies integer below BIGINT_MIN`() {
        val result =
            coercer.validate(enriched(IntegerValue(BIGINT_MIN - BigInteger.ONE), IntegerType))
        assertShouldNullify(result)
    }

    @Test
    fun `validate accepts zero integer`() {
        val result = coercer.validate(enriched(IntegerValue(BigInteger.ZERO), IntegerType))
        assertEquals(ValidationResult.Valid, result)
    }

    // ================================================================
    // validate() — Number (NUMERIC) tests
    // ================================================================

    @Test
    fun `validate accepts valid number`() {
        val result = coercer.validate(enriched(NumberValue(BigDecimal("10000.123")), NumberType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate nullifies number exceeding maximum`() {
        val result =
            coercer.validate(
                enriched(NumberValue(NUMERIC_MAX.multiply(BigDecimal.TEN)), NumberType)
            )
        assertShouldNullify(result)
    }

    @Test
    fun `validate nullifies number below minimum`() {
        val result =
            coercer.validate(
                enriched(NumberValue(NUMERIC_MIN.multiply(BigDecimal.TEN)), NumberType)
            )
        assertShouldNullify(result)
    }

    @Test
    fun `validate accepts zero number`() {
        val result = coercer.validate(enriched(NumberValue(BigDecimal.ZERO), NumberType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts very small positive number`() {
        val result =
            coercer.validate(enriched(NumberValue(BigDecimal("0.000000000001")), NumberType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts scientific notation number`() {
        val result =
            coercer.validate(enriched(NumberValue(BigDecimal("1.23E-10")), NumberType))
        assertEquals(ValidationResult.Valid, result)
    }

    // ================================================================
    // validate() — String (VARCHAR 65535) tests
    // ================================================================

    @Test
    fun `validate accepts short string`() {
        val result = coercer.validate(enriched(StringValue("hello world"), StringType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts empty string`() {
        val result = coercer.validate(enriched(StringValue(""), StringType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts string at VARCHAR byte boundary`() {
        // ASCII string at exactly 65535 bytes (1 byte per char)
        val boundaryString = "a".repeat(VARCHAR_LIMIT_BYTES)
        val result = coercer.validate(enriched(StringValue(boundaryString), StringType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate nullifies string exceeding VARCHAR byte limit`() {
        // ASCII string 1 byte over the 65535 limit
        val overLimitString = "a".repeat(VARCHAR_LIMIT_BYTES + 1)
        val result = coercer.validate(enriched(StringValue(overLimitString), StringType))
        assertShouldNullify(result)
    }

    @Test
    fun `validate accepts string with unicode characters within limit`() {
        val result =
            coercer.validate(
                enriched(StringValue("Hello \u4e16\u754c \ud83c\udf0d"), StringType)
            )
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate sanitizes null bytes in strings`() {
        val input = "before\u0000after"
        val enrichedValue = enriched(StringValue(input), StringType)

        val result = coercer.validate(enrichedValue)

        assertEquals(ValidationResult.Valid, result)
        assertEquals("beforeafter", (enrichedValue.abValue as StringValue).value)
    }

    @Test
    fun `validate sanitizes multiple null bytes`() {
        val input = "\u0000a\u0000b\u0000"
        val enrichedValue = enriched(StringValue(input), StringType)

        coercer.validate(enrichedValue)

        assertEquals("ab", (enrichedValue.abValue as StringValue).value)
    }

    @Test
    fun `validate handles multi-byte characters near VARCHAR limit`() {
        // Each CJK character is 3 bytes in UTF-8. Fill up to just under the 65535 limit.
        val cjkChar = "\u4e16" // 3 bytes in UTF-8
        val count = VARCHAR_LIMIT_BYTES / 3 // 21845 chars = 65535 bytes exactly
        val justFits = cjkChar.repeat(count)
        val result = coercer.validate(enriched(StringValue(justFits), StringType))
        assertEquals(ValidationResult.Valid, result)

        // One more character pushes it over
        val overLimit = cjkChar.repeat(count + 1)
        val result2 = coercer.validate(enriched(StringValue(overLimit), StringType))
        assertShouldNullify(result2)
    }

    // ================================================================
    // validate() — Object/Array (SUPER 16MB) tests
    // ================================================================

    @Test
    fun `validate accepts small object`() {
        val obj =
            ObjectValue(
                linkedMapOf(
                    "foo" to IntegerValue(1),
                    "bar" to IntegerValue(2),
                )
            )
        val result =
            coercer.validate(
                enriched(
                    obj,
                    ObjectType(
                        properties = linkedMapOf(),
                        additionalProperties = true,
                        required = emptyList(),
                    ),
                )
            )
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts small array`() {
        val arr = ArrayValue(listOf(IntegerValue(1), IntegerValue(2), IntegerValue(3)))
        val result =
            coercer.validate(enriched(arr, ArrayType(FieldType(IntegerType, false))))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts deeply nested object`() {
        val deepObj =
            ObjectValue(
                linkedMapOf<String, AirbyteValue>(
                    "l1" to
                        ObjectValue(
                            linkedMapOf<String, AirbyteValue>(
                                "l2" to
                                    ObjectValue(
                                        linkedMapOf<String, AirbyteValue>(
                                            "l3" to StringValue("deep"),
                                        )
                                    ),
                            )
                        ),
                )
            )
        val result =
            coercer.validate(
                enriched(
                    deepObj,
                    ObjectType(
                        properties = linkedMapOf(),
                        additionalProperties = true,
                        required = emptyList(),
                    ),
                )
            )
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts large array under SUPER limit`() {
        val largeArray = ArrayValue((1..1000).map { IntegerValue(it.toBigInteger()) })
        val result =
            coercer.validate(enriched(largeArray, ArrayType(FieldType(IntegerType, false))))
        assertEquals(ValidationResult.Valid, result)
    }

    // ================================================================
    // validate() — Timestamp tests
    // ================================================================

    @Test
    fun `validate accepts valid timestamp with timezone`() {
        val ts = OffsetDateTime.of(2023, 1, 1, 12, 0, 0, 0, ZoneOffset.UTC)
        val result =
            coercer.validate(
                enriched(TimestampWithTimezoneValue(ts), TimestampTypeWithTimezone)
            )
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate nullifies timestamp with timezone beyond maximum`() {
        val ts =
            OffsetDateTime.ofInstant(
                java.time.Instant.ofEpochSecond(TIMESTAMP_MAX_EPOCH_SECONDS + 1),
                ZoneOffset.UTC,
            )
        val result =
            coercer.validate(
                enriched(TimestampWithTimezoneValue(ts), TimestampTypeWithTimezone)
            )
        assertShouldNullify(result)
    }

    @Test
    fun `validate nullifies timestamp with timezone before minimum`() {
        val ts =
            OffsetDateTime.ofInstant(
                java.time.Instant.ofEpochSecond(TIMESTAMP_MIN_EPOCH_SECONDS - 1),
                ZoneOffset.UTC,
            )
        val result =
            coercer.validate(
                enriched(TimestampWithTimezoneValue(ts), TimestampTypeWithTimezone)
            )
        assertShouldNullify(result)
    }

    @Test
    fun `validate accepts timestamp at maximum boundary`() {
        val ts =
            OffsetDateTime.ofInstant(
                java.time.Instant.ofEpochSecond(TIMESTAMP_MAX_EPOCH_SECONDS),
                ZoneOffset.UTC,
            )
        val result =
            coercer.validate(
                enriched(TimestampWithTimezoneValue(ts), TimestampTypeWithTimezone)
            )
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts timestamp at minimum boundary`() {
        val ts =
            OffsetDateTime.ofInstant(
                java.time.Instant.ofEpochSecond(TIMESTAMP_MIN_EPOCH_SECONDS),
                ZoneOffset.UTC,
            )
        val result =
            coercer.validate(
                enriched(TimestampWithTimezoneValue(ts), TimestampTypeWithTimezone)
            )
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts valid timestamp without timezone`() {
        val ts = LocalDateTime.of(2023, 1, 1, 12, 0, 0, 0)
        val result =
            coercer.validate(
                enriched(TimestampWithoutTimezoneValue(ts), TimestampTypeWithoutTimezone)
            )
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate nullifies timestamp without timezone beyond maximum`() {
        val ts =
            LocalDateTime.ofEpochSecond(TIMESTAMP_MAX_EPOCH_SECONDS + 1, 0, ZoneOffset.UTC)
        val result =
            coercer.validate(
                enriched(TimestampWithoutTimezoneValue(ts), TimestampTypeWithoutTimezone)
            )
        assertShouldNullify(result)
    }

    // ================================================================
    // validate() — Other types
    // ================================================================

    @Test
    fun `validate accepts NullValue`() {
        val result = coercer.validate(enriched(NullValue, StringType))
        assertEquals(ValidationResult.Valid, result)
    }

    @Test
    fun `validate accepts BooleanValue`() {
        val result =
            coercer.validate(
                enriched(BooleanValue(true), io.airbyte.cdk.load.data.BooleanType)
            )
        assertEquals(ValidationResult.Valid, result)
    }

    // ================================================================
    // Helpers
    // ================================================================

    private fun enriched(
        value: AirbyteValue,
        type: io.airbyte.cdk.load.data.AirbyteType,
    ): EnrichedAirbyteValue =
        EnrichedAirbyteValue(
            abValue = value,
            type = type,
            name = "test_field",
            changes = mutableListOf(),
            airbyteMetaField = null,
        )

    private fun assertShouldNullify(result: ValidationResult) {
        assertEquals(ValidationResult.ShouldNullify::class, result::class)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            (result as ValidationResult.ShouldNullify).reason,
        )
    }
}
