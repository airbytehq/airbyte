/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.write.transform

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.integrations.destination.databricks.write.transform.DatabricksValueCoercerTest.Fixtures.mockCoercedUnionValue
import io.airbyte.integrations.destination.databricks.write.transform.DatabricksValueCoercerTest.Fixtures.mockCoercedValue
import io.airbyte.integrations.destination.databricks.write.transform.DatabricksValueCoercerTest.Fixtures.toAirbyteIntegerValue
import io.airbyte.integrations.destination.databricks.write.transform.DatabricksValueCoercerTest.Fixtures.toAirbyteNumberValue
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.mockk.impl.annotations.InjectMockKs
import io.mockk.junit5.MockKExtension
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetTime
import java.time.ZoneOffset
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

@ExtendWith(MockKExtension::class)
class DatabricksValueCoercerTest {

    @InjectMockKs private lateinit var coercer: DatabricksValueCoercer

    // -- Integer (LONG / INT64) validation --

    @ParameterizedTest
    @MethodSource("validIntegers")
    fun `validate integers - valid values are left unchanged`(value: String) {
        val input = mockCoercedValue(value.toAirbyteIntegerValue())
        val result = coercer.validate(input)
        assertEquals(ValidationResult.Valid, result)
    }

    @ParameterizedTest
    @MethodSource("invalidIntegers")
    fun `validate integers - out of INT64 range values are nulled`(value: String) {
        val input = mockCoercedValue(value.toAirbyteIntegerValue())
        val result = coercer.validate(input)
        assertShouldNullify(result)
    }

    // -- Number (DECIMAL(38, 10)) validation --

    @ParameterizedTest
    @MethodSource("validNumbers")
    fun `validate numbers - valid values are left unchanged`(value: String) {
        val input = mockCoercedValue(value.toAirbyteNumberValue())
        val result = coercer.validate(input)
        assertEquals(ValidationResult.Valid, result)
    }

    @ParameterizedTest
    @MethodSource("invalidNumbers")
    fun `validate numbers - out of DECIMAL range values are nulled`(value: String) {
        val input = mockCoercedValue(value.toAirbyteNumberValue())
        val result = coercer.validate(input)
        assertShouldNullify(result)
    }

    // -- Other types always valid --

    @Test
    fun `validate returns Valid for string values`() {
        val input = mockCoercedValue(StringValue("any string"))
        assertEquals(ValidationResult.Valid, coercer.validate(input))
    }

    @Test
    fun `validate returns Valid for boolean values`() {
        val input = mockCoercedValue(BooleanValue(true))
        assertEquals(ValidationResult.Valid, coercer.validate(input))
    }

    @Test
    fun `validate returns Valid for null values`() {
        val input = mockCoercedValue(NullValue)
        assertEquals(ValidationResult.Valid, coercer.validate(input))
    }

    @Test
    fun `validate returns Valid for date values`() {
        val input = mockCoercedValue(DateValue(LocalDate.of(2026, 1, 1)))
        assertEquals(ValidationResult.Valid, coercer.validate(input))
    }

    @Test
    fun `validate returns Valid for timestamp values`() {
        val input =
            mockCoercedValue(
                TimestampWithTimezoneValue(
                    LocalDateTime.of(2026, 1, 1, 0, 0).atOffset(ZoneOffset.UTC),
                ),
            )
        assertEquals(ValidationResult.Valid, coercer.validate(input))
    }

    // -- map() tests --

    @ParameterizedTest
    @MethodSource("nonNullValues")
    fun `map passes through non-union values unchanged`(value: AirbyteValue) {
        val input = mockCoercedValue(value)
        val result = coercer.map(input)
        assertEquals(input.abValue, result.abValue)
    }

    @Test
    fun `map passes through null values unchanged`() {
        val input = mockCoercedValue(NullValue)
        val result = coercer.map(input)
        assertEquals(NullValue, result.abValue)
    }

    @ParameterizedTest
    @MethodSource("nonNullValues")
    fun `map converts union type values to JSON strings`(value: AirbyteValue) {
        val input = mockCoercedUnionValue(value)
        val result = coercer.map(input)
        assert(result.abValue is StringValue)
    }

    @Test
    fun `map preserves null within union type`() {
        val input = mockCoercedUnionValue(NullValue)
        val result = coercer.map(input)
        assertEquals(NullValue, result.abValue)
    }

    // -- Helpers --

    private fun assertShouldNullify(result: ValidationResult) {
        assertEquals(ValidationResult.ShouldNullify::class, result::class)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            (result as ValidationResult.ShouldNullify).reason,
        )
    }

    companion object {
        @JvmStatic
        fun validIntegers() =
            listOf(
                // Long.MAX_VALUE and Long.MIN_VALUE (63-bit magnitude)
                Arguments.of("9223372036854775807"),
                Arguments.of("-9223372036854775808"),
                Arguments.of("0"),
                Arguments.of("1"),
                Arguments.of("-1"),
                Arguments.of("89123763152678031"),
                Arguments.of("-9870021087"),
                Arguments.of("100000000"),
            )

        @JvmStatic
        fun invalidIntegers() =
            listOf(
                // Long.MAX_VALUE + 1 and Long.MIN_VALUE - 1 (64-bit magnitude)
                Arguments.of("9223372036854775808"),
                Arguments.of("-9223372036854775809"),
                Arguments.of("1000000000000000000000000000"),
                Arguments.of("-1000000000000000000000000000"),
                Arguments.of("12345678901234567890"),
                Arguments.of("-12345678901234567890"),
            )

        @JvmStatic
        fun validNumbers() =
            listOf(
                Arguments.of("0"),
                Arguments.of("1"),
                Arguments.of("42"),
                Arguments.of("-1"),
                Arguments.of("100000000.870132478"),
                Arguments.of("-10000000000000000.33"),
                Arguments.of("80327031.865312"),
                Arguments.of("-80327031.8954"),
                // Max valid: 28 integer digits (DECIMAL(38,10) allows up to 28)
                Arguments.of("9999999999999999999999999999.9999999999"),
                Arguments.of("-9999999999999999999999999999.9999999999"),
            )

        @JvmStatic
        fun invalidNumbers() =
            listOf(
                // 29+ integer digits exceed DECIMAL(38,10)'s 28 integer digit limit
                Arguments.of("10000000000000000000000000000"),
                Arguments.of("-10000000000000000000000000000"),
                Arguments.of("-10000000000000000000000000124"),
                Arguments.of("10000000000000000000000000081"),
                Arguments.of("100000000000000000000000000000000000001"),
                Arguments.of("999999999999999999999999999999999999999.9"),
                Arguments.of("-999999999999999999999999999999999999999.12"),
            )

        @JvmStatic
        fun nonNullValues() =
            listOf(
                Arguments.of(NumberValue(BigDecimal("89214.7834"))),
                Arguments.of(IntegerValue(BigInteger("72317631278"))),
                Arguments.of(StringValue("this should just stay the same")),
                Arguments.of(
                    ObjectValue(
                        linkedMapOf("cat" to StringValue("dog"), "bird" to StringValue("fish")),
                    ),
                ),
                Arguments.of(ArrayValue(listOf(StringValue("cat"), StringValue("dog")))),
                Arguments.of(BooleanValue(true)),
                Arguments.of(BooleanValue(false)),
                Arguments.of(DateValue(LocalDate.of(2026, 6, 1))),
                Arguments.of(
                    TimestampWithTimezoneValue(
                        LocalDateTime.of(2026, 1, 1, 0, 0).atOffset(ZoneOffset.UTC),
                    ),
                ),
                Arguments.of(TimestampWithoutTimezoneValue(LocalDateTime.of(2026, 1, 1, 0, 0))),
                Arguments.of(TimeWithoutTimezoneValue(LocalTime.now())),
                Arguments.of(TimeWithTimezoneValue(OffsetTime.now())),
            )
    }

    object Fixtures {
        fun String.toAirbyteNumberValue() = NumberValue(BigDecimal(this))

        fun String.toAirbyteIntegerValue() = IntegerValue(BigInteger(this))

        fun mockCoercedValue(value: AirbyteValue) =
            EnrichedAirbyteValue(
                abValue = value,
                type = StringType,
                name = "fixture",
                airbyteMetaField = null,
            )

        fun mockCoercedUnionValue(value: AirbyteValue) =
            EnrichedAirbyteValue(
                abValue = value,
                type = UnionType(setOf(), false),
                name = "fixture",
                airbyteMetaField = null,
            )
    }
}
