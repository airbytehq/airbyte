/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.util

import io.airbyte.cdk.load.data.AirbyteValueDeepCoercingMapper
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.time.ZonedDateTime

/** Collection of time/date string to time/date object conversion utilities. */
object TimeStringUtility {

    fun toLocalDate(dateString: String): LocalDate {
        return LocalDate.parse(dateString, AirbyteValueDeepCoercingMapper.DATE_TIME_FORMATTER)
    }

    fun toLocalDateTime(dateString: String): LocalDateTime {
        return LocalDateTime.parse(dateString, AirbyteValueDeepCoercingMapper.DATE_TIME_FORMATTER)
    }

    fun toOffset(timeString: String): LocalTime {
        return try {
            toMicrosOfDayWithTimezone(timeString)
        } catch (e: Exception) {
            toMicrosOfDayWithoutTimezone(timeString)
        }
    }

    private fun toMicrosOfDayWithTimezone(timeString: String): LocalTime {
        return OffsetTime.parse(timeString, AirbyteValueDeepCoercingMapper.TIME_FORMATTER)
            .toLocalTime()
    }

    private fun toMicrosOfDayWithoutTimezone(timeString: String): LocalTime {
        return LocalTime.parse(timeString, AirbyteValueDeepCoercingMapper.TIME_FORMATTER)
    }

    fun toOffsetDateTime(timestampString: String): OffsetDateTime {
        return try {
            toOffsetDateTimeWithTimezone(timestampString)
        } catch (e: Exception) {
            toOffsetDateTimeWithoutTimezone(timestampString)
        }
    }

    private fun toOffsetDateTimeWithTimezone(timestampString: String): OffsetDateTime {
        return ZonedDateTime.parse(
                timestampString,
                AirbyteValueDeepCoercingMapper.DATE_TIME_FORMATTER
            )
            .toOffsetDateTime()
    }

    private fun toOffsetDateTimeWithoutTimezone(timestampString: String): OffsetDateTime {
        return LocalDateTime.parse(
                timestampString,
                AirbyteValueDeepCoercingMapper.DATE_TIME_FORMATTER
            )
            .atOffset(ZoneOffset.UTC)
    }
}
