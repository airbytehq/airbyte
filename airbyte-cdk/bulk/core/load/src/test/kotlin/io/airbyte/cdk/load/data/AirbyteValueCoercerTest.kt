/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

// Test cases ported from legacy-task-loader's AirbyteValueDeepCoercingMapperTest.kt,
// adapted to call AirbyteValueCoercer.coerce() directly with hardcoded expected values.
// All tests run against both legacy (flag=false) and fast (flag=true) implementations.

package io.airbyte.cdk.load.data

import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.util.stream.Stream
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

// spotless:off
// Formatting disabled — breaking up timestamp creation across lines makes it much harder to read
class AirbyteValueCoercerTest {

    private val legacyCoercer = AirbyteValueCoercer(useFastTimestampParsing = false)
    private val fastCoercer = AirbyteValueCoercer(useFastTimestampParsing = true)

    @ParameterizedTest(name = "{0}")
    @MethodSource("timestampWithTimezoneArgs")
    fun testCoerceTimestampWithTimezone(input: String, expected: AirbyteValue) {
        assertEquals(expected, legacyCoercer.coerce(StringValue(input), TimestampTypeWithTimezone))
        assertEquals(expected, fastCoercer.coerce(StringValue(input), TimestampTypeWithTimezone))
    }

    @ParameterizedTest(name = "{0}")
    @MethodSource("timestampWithoutTimezoneArgs")
    fun testCoerceTimestampWithoutTimezone(input: String, expected: AirbyteValue) {
        assertEquals(expected, legacyCoercer.coerce(StringValue(input), TimestampTypeWithoutTimezone))
        assertEquals(expected, fastCoercer.coerce(StringValue(input), TimestampTypeWithoutTimezone))
    }

    @ParameterizedTest(name = "{0}")
    @MethodSource("timeWithTimezoneArgs")
    fun testCoerceTimeWithTimezone(input: String, expected: AirbyteValue) {
        assertEquals(expected, legacyCoercer.coerce(StringValue(input), TimeTypeWithTimezone))
        assertEquals(expected, fastCoercer.coerce(StringValue(input), TimeTypeWithTimezone))
    }

    @ParameterizedTest(name = "{0}")
    @MethodSource("timeWithoutTimezoneArgs")
    fun testCoerceTimeWithoutTimezone(input: String, expected: AirbyteValue) {
        assertEquals(expected, legacyCoercer.coerce(StringValue(input), TimeTypeWithoutTimezone))
        assertEquals(expected, fastCoercer.coerce(StringValue(input), TimeTypeWithoutTimezone))
    }

    @ParameterizedTest(name = "{0}")
    @MethodSource("dateArgs")
    fun testCoerceDate(input: String, expected: AirbyteValue) {
        assertEquals(expected, legacyCoercer.coerce(StringValue(input), DateType))
        assertEquals(expected, fastCoercer.coerce(StringValue(input), DateType))
    }

    @Test
    fun testCoerceNullValue() {
        assertEquals(NullValue, legacyCoercer.coerce(NullValue, TimestampTypeWithTimezone))
        assertEquals(NullValue, fastCoercer.coerce(NullValue, TimestampTypeWithTimezone))
    }

    @Test
    fun testCoerceAlreadyTypedTimestamp() {
        val value: AirbyteValue = TimestampWithTimezoneValue(OffsetDateTime.of(2024, 1, 23, 1, 23, 45, 0, ZoneOffset.UTC))
        assertEquals(value, legacyCoercer.coerce(value, TimestampTypeWithTimezone))
        assertEquals(value, fastCoercer.coerce(value, TimestampTypeWithTimezone))
    }

    @Test
    fun testCoerceAlreadyTypedTime() {
        val value: AirbyteValue = TimeWithTimezoneValue(OffsetTime.of(1, 23, 45, 0, ZoneOffset.UTC))
        assertEquals(value, legacyCoercer.coerce(value, TimeTypeWithTimezone))
        assertEquals(value, fastCoercer.coerce(value, TimeTypeWithTimezone))
    }

    @Test
    fun testCoerceWrongTypeReturnsNull() {
        assertNull(legacyCoercer.coerce(IntegerValue(12345), TimestampTypeWithTimezone))
        assertNull(fastCoercer.coerce(IntegerValue(12345), TimestampTypeWithTimezone))
    }

    @Test
    fun testCoerceInvalidStringReturnsNull() {
        assertNull(legacyCoercer.coerce(StringValue("not-a-timestamp"), TimestampTypeWithTimezone))
        assertNull(fastCoercer.coerce(StringValue("not-a-timestamp"), TimestampTypeWithTimezone))
    }

    companion object {
        // Expected values below were captured from the output of the legacy coercion code
        // (the original try-ZonedDateTime/catch-LocalDateTime pattern) to ensure the new
        // fast path produces identical results.

        private val UTC = ZoneOffset.UTC

        @JvmStatic
        fun timestampWithTimezoneArgs(): Stream<Arguments> = Stream.of(
            // ISO formats — no timezone (assumes UTC)
            Arguments.of(
                "2018-09-15 12:00:00",
                TimestampWithTimezoneValue(OffsetDateTime.of(2018, 9, 15, 12, 0, 0, 0, UTC)),
            ),
            Arguments.of(
                "2018-09-15 12:00:00.006542",
                TimestampWithTimezoneValue(OffsetDateTime.of(2018, 9, 15, 12, 0, 0, 6542000, UTC)),
            ),
            // Slash separators
            Arguments.of(
                "2018/09/15 12:00:00",
                TimestampWithTimezoneValue(OffsetDateTime.of(2018, 9, 15, 12, 0, 0, 0, UTC)),
            ),
            // Dot separators
            Arguments.of(
                "2018.09.15 12:00:00",
                TimestampWithTimezoneValue(OffsetDateTime.of(2018, 9, 15, 12, 0, 0, 0, UTC)),
            ),
            // Abbreviated month name
            Arguments.of(
                "2018 Jul 15 12:00:00",
                TimestampWithTimezoneValue(OffsetDateTime.of(2018, 7, 15, 12, 0, 0, 0, UTC)),
            ),
            // Single-digit month/day
            Arguments.of(
                "2021-1-1 01:01:01",
                TimestampWithTimezoneValue(OffsetDateTime.of(2021, 1, 1, 1, 1, 1, 0, UTC)),
            ),
            Arguments.of(
                "2021.1.1 01:01:01",
                TimestampWithTimezoneValue(OffsetDateTime.of(2021, 1, 1, 1, 1, 1, 0, UTC)),
            ),
            Arguments.of(
                "2021/1/1 01:01:01",
                TimestampWithTimezoneValue(OffsetDateTime.of(2021, 1, 1, 1, 1, 1, 0, UTC)),
            ),
            Arguments.of(
                "2021-01-01 01:01:01",
                TimestampWithTimezoneValue(OffsetDateTime.of(2021, 1, 1, 1, 1, 1, 0, UTC)),
            ),
            // With timezone offset — various formats
            Arguments.of(
                "2021-1-1 01:01:01 +01",
                TimestampWithTimezoneValue(OffsetDateTime.of(2021, 1, 1, 1, 1, 1, 0, ZoneOffset.ofHours(1))),
            ),
            Arguments.of(
                "2018 Jul 15 12:00:00 GMT+08:00",
                TimestampWithTimezoneValue(OffsetDateTime.of(2018, 7, 15, 12, 0, 0, 0, ZoneOffset.ofHours(8))),
            ),
            // Known bug: 'GMT+07' without a space is parsed as a ZoneId (not a ZoneOffset),
            // causing toOffsetDateTime() to normalize to UTC instead of preserving +07:00.
            // TODO: The correct result should be
            // TimestampWithTimezoneValue(OffsetDateTime.of(2018, 7, 15, 12, 0, 0, 0, ZoneOffset.ofHours(7))).
            Arguments.of(
                "2018 Jul 15 12:00:00GMT+07",
                TimestampWithTimezoneValue(OffsetDateTime.of(2018, 7, 15, 5, 0, 0, 0, UTC)),
            ),
            Arguments.of(
                "2021-01-01T01:01:01+01:00",
                TimestampWithTimezoneValue(OffsetDateTime.of(2021, 1, 1, 1, 1, 1, 0, ZoneOffset.ofHours(1))),
            ),
            Arguments.of(
                "2021-01-01T01:01:01.546+01:00",
                TimestampWithTimezoneValue(OffsetDateTime.of(2021, 1, 1, 1, 1, 1, 546000000, ZoneOffset.ofHours(1))),
            ),
            Arguments.of(
                "2021-01-01 01:01:01 +0000",
                TimestampWithTimezoneValue(OffsetDateTime.of(2021, 1, 1, 1, 1, 1, 0, UTC)),
            ),
            Arguments.of(
                "2021/01/01 01:01:01 +0000",
                TimestampWithTimezoneValue(OffsetDateTime.of(2021, 1, 1, 1, 1, 1, 0, UTC)),
            ),
            // Z suffix
            Arguments.of(
                "2021-01-01T01:01:01Z",
                TimestampWithTimezoneValue(OffsetDateTime.of(2021, 1, 1, 1, 1, 1, 0, UTC)),
            ),
            // Negative offsets
            Arguments.of(
                "2021-01-01T01:01:01-01:00",
                TimestampWithTimezoneValue(OffsetDateTime.of(2021, 1, 1, 1, 1, 1, 0, ZoneOffset.ofHours(-1))),
            ),
            Arguments.of(
                "2021-01-01T01:01:01+01:00",
                TimestampWithTimezoneValue(OffsetDateTime.of(2021, 1, 1, 1, 1, 1, 0, ZoneOffset.ofHours(1))),
            ),
            // Named timezones
            Arguments.of(
                "2021-01-01 01:01:01 UTC",
                TimestampWithTimezoneValue(OffsetDateTime.of(2021, 1, 1, 1, 1, 1, 0, UTC)),
            ),
            Arguments.of(
                "2021-01-01T01:01:01 PST",
                TimestampWithTimezoneValue(OffsetDateTime.of(2021, 1, 1, 1, 1, 1, 0, ZoneOffset.ofHours(-8))),
            ),
            // Compact offsets
            Arguments.of(
                "2021-01-01T01:01:01 +0000",
                TimestampWithTimezoneValue(OffsetDateTime.of(2021, 1, 1, 1, 1, 1, 0, UTC)),
            ),
            Arguments.of(
                "2021-01-01T01:01:01+0000",
                TimestampWithTimezoneValue(OffsetDateTime.of(2021, 1, 1, 1, 1, 1, 0, UTC)),
            ),
            // Appended named timezone
            Arguments.of(
                "2021-01-01T01:01:01UTC",
                TimestampWithTimezoneValue(OffsetDateTime.of(2021, 1, 1, 1, 1, 1, 0, UTC)),
            ),
            // Short offset
            Arguments.of(
                "2021-01-01T01:01:01+01",
                TimestampWithTimezoneValue(OffsetDateTime.of(2021, 1, 1, 1, 1, 1, 0, ZoneOffset.ofHours(1))),
            ),
            // BC era — year 2022 BC maps to proleptic year -2021
            Arguments.of(
                "2022-01-23T01:23:45.678-11:30 BC",
                TimestampWithTimezoneValue(OffsetDateTime.of(-2021, 1, 23, 1, 23, 45, 678000000, ZoneOffset.ofHoursMinutes(-11, -30))),
            ),
            Arguments.of(
                "2022-01-23T01:23:45.678-11:30",
                TimestampWithTimezoneValue(OffsetDateTime.of(2022, 1, 23, 1, 23, 45, 678000000, ZoneOffset.ofHoursMinutes(-11, -30))),
            ),
        )

        @JvmStatic
        fun timestampWithoutTimezoneArgs(): Stream<Arguments> = Stream.of(
            Arguments.of(
                "2018-09-15 12:00:00",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2018, 9, 15, 12, 0, 0, 0)),
            ),
            Arguments.of(
                "2018-09-15 12:00:00.006542",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2018, 9, 15, 12, 0, 0, 6542000)),
            ),
            Arguments.of(
                "2018/09/15 12:00:00",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2018, 9, 15, 12, 0, 0, 0)),
            ),
            Arguments.of(
                "2018.09.15 12:00:00",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2018, 9, 15, 12, 0, 0, 0)),
            ),
            Arguments.of(
                "2018 Jul 15 12:00:00",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2018, 7, 15, 12, 0, 0, 0)),
            ),
            Arguments.of(
                "2021-1-1 01:01:01",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2021, 1, 1, 1, 1, 1, 0)),
            ),
            Arguments.of(
                "2021.1.1 01:01:01",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2021, 1, 1, 1, 1, 1, 0)),
            ),
            Arguments.of(
                "2021/1/1 01:01:01",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2021, 1, 1, 1, 1, 1, 0)),
            ),
            Arguments.of(
                "2021-01-01 01:01:01",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2021, 1, 1, 1, 1, 1, 0)),
            ),
            Arguments.of(
                "2021-1-1 01:01:01 +01",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2021, 1, 1, 1, 1, 1, 0)),
            ),
            Arguments.of(
                "2018 Jul 15 12:00:00 GMT+08:00",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2018, 7, 15, 12, 0, 0, 0)),
            ),
            // Known bug: see timestampWithTimezoneArgs for details
            Arguments.of(
                "2018 Jul 15 12:00:00GMT+07",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2018, 7, 15, 5, 0, 0, 0)),
            ),
            Arguments.of(
                "2021-01-01T01:01:01+01:00",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2021, 1, 1, 1, 1, 1, 0)),
            ),
            Arguments.of(
                "2021-01-01T01:01:01.546+01:00",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2021, 1, 1, 1, 1, 1, 546000000)),
            ),
            Arguments.of(
                "2021-01-01 01:01:01 +0000",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2021, 1, 1, 1, 1, 1, 0)),
            ),
            Arguments.of(
                "2021/01/01 01:01:01 +0000",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2021, 1, 1, 1, 1, 1, 0)),
            ),
            Arguments.of(
                "2021-01-01T01:01:01Z",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2021, 1, 1, 1, 1, 1, 0)),
            ),
            Arguments.of(
                "2021-01-01T01:01:01-01:00",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2021, 1, 1, 1, 1, 1, 0)),
            ),
            Arguments.of(
                "2021-01-01T01:01:01+01:00",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2021, 1, 1, 1, 1, 1, 0)),
            ),
            Arguments.of(
                "2021-01-01 01:01:01 UTC",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2021, 1, 1, 1, 1, 1, 0)),
            ),
            Arguments.of(
                "2021-01-01T01:01:01 PST",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2021, 1, 1, 1, 1, 1, 0)),
            ),
            Arguments.of(
                "2021-01-01T01:01:01 +0000",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2021, 1, 1, 1, 1, 1, 0)),
            ),
            Arguments.of(
                "2021-01-01T01:01:01+0000",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2021, 1, 1, 1, 1, 1, 0)),
            ),
            Arguments.of(
                "2021-01-01T01:01:01UTC",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2021, 1, 1, 1, 1, 1, 0)),
            ),
            Arguments.of(
                "2021-01-01T01:01:01+01",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2021, 1, 1, 1, 1, 1, 0)),
            ),
            Arguments.of(
                "2022-01-23T01:23:45.678-11:30 BC",
                TimestampWithoutTimezoneValue(LocalDateTime.of(-2021, 1, 23, 1, 23, 45, 678000000)),
            ),
            Arguments.of(
                "2022-01-23T01:23:45.678-11:30",
                TimestampWithoutTimezoneValue(LocalDateTime.of(2022, 1, 23, 1, 23, 45, 678000000)),
            ),
        )

        @JvmStatic
        fun timeWithTimezoneArgs(): Stream<Arguments> = Stream.of(
            // Bare times — no timezone, assumes UTC
            Arguments.of(
                "01:01:01",
                TimeWithTimezoneValue(OffsetTime.of(1, 1, 1, 0, UTC)),
            ),
            Arguments.of(
                "01:01",
                TimeWithTimezoneValue(OffsetTime.of(1, 1, 0, 0, UTC)),
            ),
            Arguments.of(
                "12:23:01.541",
                TimeWithTimezoneValue(OffsetTime.of(12, 23, 1, 541000000, UTC)),
            ),
            Arguments.of(
                "12:23:01.541214",
                TimeWithTimezoneValue(OffsetTime.of(12, 23, 1, 541214000, UTC)),
            ),
            // With timezone offset
            Arguments.of(
                "12:00:00.000000+01:00",
                TimeWithTimezoneValue(OffsetTime.of(12, 0, 0, 0, ZoneOffset.ofHours(1))),
            ),
            Arguments.of(
                "10:00:00.000000-01:00",
                TimeWithTimezoneValue(OffsetTime.of(10, 0, 0, 0, ZoneOffset.ofHours(-1))),
            ),
            Arguments.of(
                "03:30:00.000000+04:00",
                TimeWithTimezoneValue(OffsetTime.of(3, 30, 0, 0, ZoneOffset.ofHours(4))),
            ),
        )

        @JvmStatic
        fun timeWithoutTimezoneArgs(): Stream<Arguments> = Stream.of(
            Arguments.of(
                "01:01:01",
                TimeWithoutTimezoneValue(LocalTime.of(1, 1, 1, 0)),
            ),
            Arguments.of(
                "01:01",
                TimeWithoutTimezoneValue(LocalTime.of(1, 1, 0, 0)),
            ),
            Arguments.of(
                "12:23:01.541",
                TimeWithoutTimezoneValue(LocalTime.of(12, 23, 1, 541000000)),
            ),
            Arguments.of(
                "12:23:01.541214",
                TimeWithoutTimezoneValue(LocalTime.of(12, 23, 1, 541214000)),
            ),
            Arguments.of(
                "12:00:00.000000+01:00",
                TimeWithoutTimezoneValue(LocalTime.of(12, 0, 0, 0)),
            ),
            Arguments.of(
                "10:00:00.000000-01:00",
                TimeWithoutTimezoneValue(LocalTime.of(10, 0, 0, 0)),
            ),
            Arguments.of(
                "03:30:00.000000+04:00",
                TimeWithoutTimezoneValue(LocalTime.of(3, 30, 0, 0)),
            ),
        )

        @JvmStatic
        fun dateArgs(): Stream<Arguments> = Stream.of(
            Arguments.of(
                "2021-1-1",
                DateValue(LocalDate.of(2021, 1, 1)),
            ),
            Arguments.of(
                "2021-01-01",
                DateValue(LocalDate.of(2021, 1, 1)),
            ),
            Arguments.of(
                "2021/01/02",
                DateValue(LocalDate.of(2021, 1, 2)),
            ),
            Arguments.of(
                "2021.01.03",
                DateValue(LocalDate.of(2021, 1, 3)),
            ),
            Arguments.of(
                "2021 Jan 04",
                DateValue(LocalDate.of(2021, 1, 4)),
            ),
            Arguments.of(
                "2021-1-1 BC",
                DateValue(LocalDate.of(-2020, 1, 1)),
            ),
        )
    }
}
// spotless:on
