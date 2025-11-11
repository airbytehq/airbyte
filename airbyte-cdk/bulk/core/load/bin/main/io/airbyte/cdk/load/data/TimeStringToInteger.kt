/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.time.temporal.ChronoUnit

/**
 * NOTE: To keep parity with the old avro/parquet code, we will always first try to parse the value
 * as with timezone, then fall back to without. But in theory we should be more strict.
 */
class TimeStringToInteger : AirbyteValueIdentityMapper() {

    override fun mapDate(value: AirbyteValue, context: Context): Pair<AirbyteValue, Context> {
        value as DateValue
        val epochDay = value.value.toEpochDay()
        return IntegerValue(epochDay) to context
    }

    private fun toMicrosOfDayWithTimezone(time: OffsetTime): Long {
        return time.withOffsetSameInstant(ZoneOffset.UTC).toLocalTime().toNanoOfDay() / 1_000
    }

    private fun toMicrosOfDayWithoutTimezone(time: LocalTime): Long {
        return time.toNanoOfDay() / 1_000
    }

    override fun mapTimeWithTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> =
        IntegerValue(toMicrosOfDayWithTimezone((value as TimeWithTimezoneValue).value)) to context

    override fun mapTimeWithoutTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> =
        IntegerValue(toMicrosOfDayWithoutTimezone((value as TimeWithoutTimezoneValue).value)) to
            context

    private fun toEpochMicrosWithTimezone(odt: OffsetDateTime): Long {
        return odt.toInstant().truncatedTo(ChronoUnit.MICROS).toEpochMilli() * 1_000 +
            odt.toInstant().nano / 1_000 % 1_000
    }

    private fun toEpochMicrosWithoutTimezone(dt: LocalDateTime): Long {
        val instant = dt.toInstant(ZoneOffset.UTC)
        return instant.epochSecond * 1_000_000 + instant.nano / 1_000
    }

    override fun mapTimestampWithTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> =
        IntegerValue(toEpochMicrosWithTimezone((value as TimestampWithTimezoneValue).value)) to
            context
    override fun mapTimestampWithoutTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> =
        IntegerValue(
            toEpochMicrosWithoutTimezone((value as TimestampWithoutTimezoneValue).value)
        ) to context
}
