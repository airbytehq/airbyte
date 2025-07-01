/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.transform

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.integrations.destination.clickhouse_v2.write.transform.ClickhouseCoercingValidator.Constants.DATE32_MAX
import io.airbyte.integrations.destination.clickhouse_v2.write.transform.ClickhouseCoercingValidator.Constants.DATE32_MIN
import io.airbyte.integrations.destination.clickhouse_v2.write.transform.ClickhouseCoercingValidator.Constants.DECIMAL128_MAX
import io.airbyte.integrations.destination.clickhouse_v2.write.transform.ClickhouseCoercingValidator.Constants.DECIMAL128_MIN
import io.airbyte.integrations.destination.clickhouse_v2.write.transform.ClickhouseCoercingValidator.Constants.INT64_MAX
import io.airbyte.integrations.destination.clickhouse_v2.write.transform.ClickhouseCoercingValidator.Constants.INT64_MIN
import io.airbyte.integrations.destination.clickhouse_v2.write.transform.ClickhouseCoercingValidatorTest.Fixtures.toAirbyteIntegerValue
import io.airbyte.integrations.destination.clickhouse_v2.write.transform.ClickhouseCoercingValidatorTest.Fixtures.toAirbyteNumberValue
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.mockk.impl.annotations.InjectMockKs
import io.mockk.junit5.MockKExtension
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.ZoneOffset
import kotlin.test.assertEquals
import org.junit.jupiter.api.extension.ExtendWith
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

@ExtendWith(MockKExtension::class)
class ClickhouseCoercingValidatorTest {

    @InjectMockKs private lateinit var validator: ClickhouseCoercingValidator

    @ParameterizedTest
    @MethodSource("validFloats")
    fun `validate and coerces big decimals - valid values are left unchanged`(value: String) {
        val input = Fixtures.mockCoercedValue(value.toAirbyteNumberValue())

        val result = validator.validateAndCoerce(input)

        assertEquals(input, result)
        assertEquals(input.abValue, result.abValue)
        assertEquals(mutableListOf(), result.changes)
    }

    @ParameterizedTest
    @MethodSource("invalidFloats")
    fun `validate and coerces big decimals - invalid values are nulled`(value: String) {
        val input = Fixtures.mockCoercedValue(value.toAirbyteNumberValue())

        val result = validator.validateAndCoerce(input)

        assertEquals(NullValue, result.abValue)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            result.changes[0].reason
        )
    }

    @ParameterizedTest
    @MethodSource("validIntegers")
    fun `validate and coerces big integers - valid values are left unchanged`(value: String) {
        val input = Fixtures.mockCoercedValue(value.toAirbyteIntegerValue())

        val result = validator.validateAndCoerce(input)

        assertEquals(input, result)
        assertEquals(input.abValue, result.abValue)
        assertEquals(mutableListOf(), result.changes)
    }

    @ParameterizedTest
    @MethodSource("invalidIntegers")
    fun `validate and coerces big integers - invalid values are nulled`(value: String) {
        val input = Fixtures.mockCoercedValue(value.toAirbyteIntegerValue())

        val result = validator.validateAndCoerce(input)

        assertEquals(NullValue, result.abValue)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            result.changes[0].reason
        )
    }

    @ParameterizedTest
    @MethodSource("validDates")
    fun `validate and coerces dates - valid values are left unchanged`(value: Long) {
        val date = LocalDate.ofEpochDay(value)
        val input = Fixtures.mockCoercedValue(DateValue(date))

        val result = validator.validateAndCoerce(input)

        assertEquals(input, result)
        assertEquals(input.abValue, result.abValue)
        assertEquals(mutableListOf(), result.changes)
    }

    @ParameterizedTest
    @MethodSource("invalidDates")
    fun `validate and coerces dates - invalid values are nulled`(value: Long) {
        val date = LocalDate.ofEpochDay(value)
        val input = Fixtures.mockCoercedValue(DateValue(date))

        val result = validator.validateAndCoerce(input)

        assertEquals(NullValue, result.abValue)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            result.changes[0].reason
        )
    }

    @ParameterizedTest
    @MethodSource("validDates")
    fun `validate and coerces timestamps with timezones - valid values are left unchanged`(
        value: Long
    ) {
        val timestamp =
            LocalDateTime.of(LocalDate.ofEpochDay(value), LocalTime.MAX).atOffset(ZoneOffset.UTC)
        val input = Fixtures.mockCoercedValue(TimestampWithTimezoneValue(timestamp))

        val result = validator.validateAndCoerce(input)

        assertEquals(input, result)
        assertEquals(input.abValue, result.abValue)
        assertEquals(mutableListOf(), result.changes)
    }

    @ParameterizedTest
    @MethodSource("invalidDates")
    fun `validate and coerces timestamps with timezones - invalid values are nulled`(value: Long) {
        val timestamp =
            LocalDateTime.of(LocalDate.ofEpochDay(value), LocalTime.MAX).atOffset(ZoneOffset.UTC)
        val input = Fixtures.mockCoercedValue(TimestampWithTimezoneValue(timestamp))

        val result = validator.validateAndCoerce(input)

        assertEquals(NullValue, result.abValue)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            result.changes[0].reason
        )
    }

    @ParameterizedTest
    @MethodSource("validDates")
    fun `validate and coerces timestamps without timezones - valid values are left unchanged`(
        value: Long
    ) {
        val timestamp = LocalDateTime.of(LocalDate.ofEpochDay(value), LocalTime.MAX)
        val input = Fixtures.mockCoercedValue(TimestampWithoutTimezoneValue(timestamp))

        val result = validator.validateAndCoerce(input)

        assertEquals(input, result)
        assertEquals(input.abValue, result.abValue)
        assertEquals(mutableListOf(), result.changes)
    }

    @ParameterizedTest
    @MethodSource("invalidDates")
    fun `validate and coerces timestamps without timezones - invalid values are nulled`(
        value: Long
    ) {
        val timestamp = LocalDateTime.of(LocalDate.ofEpochDay(value), LocalTime.MAX)
        val input = Fixtures.mockCoercedValue(TimestampWithoutTimezoneValue(timestamp))

        val result = validator.validateAndCoerce(input)

        assertEquals(NullValue, result.abValue)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            result.changes[0].reason
        )
    }

    companion object {
        @JvmStatic
        fun validFloats() =
            listOf(
                Arguments.of("100000000.870132478"),
                Arguments.of("42"),
                Arguments.of("-10000000000000000.33"),
                Arguments.of("100000000000000000.3"),
                Arguments.of(DECIMAL128_MIN.add(BigDecimal.valueOf(1)).toString()),
                Arguments.of(DECIMAL128_MAX.subtract(BigDecimal.valueOf(1)).toString()),
                Arguments.of("1"),
                Arguments.of("80327031.865312"),
                Arguments.of("-80327031.8954"),
            )

        @JvmStatic
        fun invalidFloats() =
            listOf(
                Arguments.of(DECIMAL128_MIN.toString()),
                Arguments.of(DECIMAL128_MAX.toString()),
                Arguments.of(DECIMAL128_MIN.subtract(BigDecimal.valueOf(124)).toString()),
                Arguments.of(DECIMAL128_MAX.add(BigDecimal.valueOf(81)).toString()),
                Arguments.of("100000000000000000000000000000000000001"),
                Arguments.of("999999999999999999999999999999999999999.9"),
                Arguments.of("-999999999999999999999999999999999999999.12"),
            )

        @JvmStatic
        fun validIntegers() =
            listOf(
                Arguments.of(INT64_MAX.toString()),
                Arguments.of(INT64_MIN.toString()),
                Arguments.of("89123763152678031"),
                Arguments.of("89123763152678031"),
                Arguments.of("88"),
                Arguments.of("124"),
                Arguments.of("-9870021087"),
                Arguments.of("573"),
                Arguments.of("-1"),
                Arguments.of("0"),
                Arguments.of("100000000"),
                Arguments.of("6"),
            )

        @JvmStatic
        fun invalidIntegers() =
            listOf(
                Arguments.of(INT64_MAX.add(BigInteger.valueOf(1)).toString()),
                Arguments.of(INT64_MIN.subtract(BigInteger.valueOf(1)).toString()),
                Arguments.of("-1000000000000000000000000000"),
                Arguments.of("1000000000000000000000000000"),
                Arguments.of("12345678901234567890"),
                Arguments.of("-12345678901234567890"),
            )

        @JvmStatic
        fun validDates() =
            listOf(
                Arguments.of(DATE32_MAX),
                Arguments.of(DATE32_MIN),
                Arguments.of(DATE32_MAX - 1),
                Arguments.of(DATE32_MIN + 1),
                Arguments.of(250),
                Arguments.of(-1000),
            )

        @JvmStatic
        fun invalidDates() =
            listOf(
                Arguments.of(DATE32_MAX + 1),
                Arguments.of(DATE32_MIN - 1),
                Arguments.of(255670),
                Arguments.of(-255670),
            )
    }

    object Fixtures {
        fun String.toAirbyteNumberValue() = NumberValue(BigDecimal(this))

        fun String.toAirbyteIntegerValue() = IntegerValue(BigInteger(this))

        fun mockCoercedValue(value: AirbyteValue) =
            EnrichedAirbyteValue(
                abValue = value,
                // the below fields are not under test
                type = StringType,
                name = "fixture",
                airbyteMetaField = null,
            )
    }
}
