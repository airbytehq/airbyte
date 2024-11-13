/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit

/**
 * NOTE: To keep parity with the old avro/parquet code, we will always first try to parse the value
 * as with timezone, then fall back to without. But in theory we should be more strict.
 */
class TimeStringToInteger : AirbyteValueIdentityMapper() {
    companion object {
        private val DATE_TIME_FORMATTER: DateTimeFormatter =
            DateTimeFormatter.ofPattern(
                "[yyyy][yy]['-']['/']['.'][' '][MMM][MM][M]['-']['/']['.'][' '][dd][d][[' '][G]][[' ']['T']HH:mm[':'ss[.][SSSSSS][SSSSS][SSSS][SSS][' '][z][zzz][Z][O][x][XXX][XX][X][[' '][G]]]]"
            )
        private val TIME_FORMATTER: DateTimeFormatter =
            DateTimeFormatter.ofPattern(
                "HH:mm[':'ss[.][SSSSSS][SSSSS][SSSS][SSS][' '][z][zzz][Z][O][x][XXX][XX][X]]"
            )
    }

    override fun mapDate(value: DateValue, context: Context): Pair<AirbyteValue, Context> {
        val epochDay = LocalDate.parse(value.value, DATE_TIME_FORMATTER).toEpochDay()
        return IntValue(epochDay.toInt()) to context
    }

    private fun toMicrosOfDayWithTimezone(timeString: String): Long {
        val time = OffsetTime.parse(timeString, TIME_FORMATTER)
        return time.withOffsetSameInstant(ZoneOffset.UTC).toLocalTime().toNanoOfDay() / 1_000
    }

    private fun toMicrosOfDayWithoutTimezone(timeString: String): Long {
        val time = LocalTime.parse(timeString, TIME_FORMATTER)
        return time.toNanoOfDay() / 1_000
    }

    private fun toMicrosOfDay(timeString: String): Long {
        return try {
            toMicrosOfDayWithTimezone(timeString)
        } catch (e: Exception) {
            toMicrosOfDayWithoutTimezone(timeString)
        }
    }

    override fun mapTimeWithTimezone(
        value: TimeValue,
        context: Context
    ): Pair<AirbyteValue, Context> = IntegerValue(toMicrosOfDay(value.value)) to context

    override fun mapTimeWithoutTimezone(
        value: TimeValue,
        context: Context
    ): Pair<AirbyteValue, Context> = IntegerValue(toMicrosOfDay(value.value)) to context

    private fun toEpochMicrosWithTimezone(timestampString: String): Long {
        val zdt = ZonedDateTime.parse(timestampString, DATE_TIME_FORMATTER)
        return zdt.toInstant().truncatedTo(ChronoUnit.MICROS).toEpochMilli() * 1_000 +
            zdt.toInstant().nano / 1_000 % 1_000
    }

    private fun toEpochMicrosWithoutTimezone(timestampString: String): Long {
        val dt = LocalDateTime.parse(timestampString, DATE_TIME_FORMATTER)
        val instant = dt.toInstant(ZoneOffset.UTC)
        return instant.epochSecond * 1_000_000 + instant.nano / 1_000
    }

    private fun toEpochMicros(timestampString: String): Long {
        return try {
            toEpochMicrosWithTimezone(timestampString)
        } catch (e: Exception) {
            toEpochMicrosWithoutTimezone(timestampString)
        }
    }

    override fun mapTimestampWithTimezone(
        value: TimestampValue,
        context: Context
    ): Pair<AirbyteValue, Context> = IntegerValue(toEpochMicros(value.value)) to context
    override fun mapTimestampWithoutTimezone(
        value: TimestampValue,
        context: Context
    ): Pair<AirbyteValue, Context> = IntegerValue(toEpochMicros(value.value)) to context
}
