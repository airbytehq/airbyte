/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.DataTypeUtils
import java.sql.*
import java.time.*
import java.time.format.DateTimeFormatter
import java.util.concurrent.*
import kotlin.math.abs
import kotlin.math.min
import org.slf4j.Logger
import org.slf4j.LoggerFactory

object DateTimeConverter {
    private val LOGGER: Logger = LoggerFactory.getLogger(DateTimeConverter::class.java)
    val TIME_WITH_TIMEZONE_FORMATTER: DateTimeFormatter =
        DateTimeFormatter.ofPattern(
            "HH:mm:ss[.][SSSSSSSSS][SSSSSSS][SSSSSS][SSSSS][SSSS][SSS][SS][S][''][XXX][XX][X]"
        )
    private var loggedUnknownTimeWithTimeZoneClass = false
    private var loggedUnknownTimeClass = false
    private var loggedUnknownTimestampWithTimeZoneClass = false
    private var loggedUnknownTimestampClass = false
    private var loggedUnknownDateClass = false

    @JvmStatic
    fun convertToTimeWithTimezone(time: Any): String {
        if (time is OffsetTime) {
            return if (hasZeroSecondsAndNanos(time.toLocalTime()))
                time.format(DataTypeUtils.TIMETZ_FORMATTER)
            else time.toString()
        } else {
            if (!loggedUnknownTimeWithTimeZoneClass) {
                LOGGER.info("Unknown class for Time with timezone data type" + time.javaClass)
                loggedUnknownTimeWithTimeZoneClass = true
            }
            val timetz = OffsetTime.parse(time.toString(), TIME_WITH_TIMEZONE_FORMATTER)
            return if (hasZeroSecondsAndNanos(timetz.toLocalTime()))
                timetz.format(DataTypeUtils.TIMETZ_FORMATTER)
            else timetz.toString()
        }
    }

    @JvmStatic
    fun convertToTimestampWithTimezone(timestamp: Any): String {
        if (timestamp is Timestamp) {
            // In snapshot mode, debezium produces a java.sql.Timestamp object for the TIMESTAMPTZ
            // type.
            // Conceptually, a timestamp with timezone is an Instant. But t.toInstant() actually
            // mangles the
            // value for ancient dates, because leap years weren't applied consistently in ye olden
            // days.
            // Additionally, toInstant() (and toLocalDateTime()) actually lose the era indicator, so
            // we can't
            // rely on their getEra() methods.
            // So we have special handling for this case, which sidesteps the toInstant conversion.
            val timestamptz: ZonedDateTime = timestamp.toLocalDateTime().atZone(ZoneOffset.UTC)
            val value = timestamptz.format(DataTypeUtils.TIMESTAMPTZ_FORMATTER)
            return AbstractJdbcCompatibleSourceOperations.Companion.resolveEra(timestamp, value)
        } else if (timestamp is OffsetDateTime) {
            return AbstractJdbcCompatibleSourceOperations.Companion.resolveEra(
                timestamp.toLocalDate(),
                timestamp.format(DataTypeUtils.TIMESTAMPTZ_FORMATTER)
            )
        } else if (timestamp is ZonedDateTime) {
            return AbstractJdbcCompatibleSourceOperations.Companion.resolveEra(
                timestamp.toLocalDate(),
                timestamp.format(DataTypeUtils.TIMESTAMPTZ_FORMATTER)
            )
        } else if (timestamp is Instant) {
            val offsetDateTime = OffsetDateTime.ofInstant(timestamp, ZoneOffset.UTC)
            val timestamptz = ZonedDateTime.from(offsetDateTime)
            val localDate = timestamptz.toLocalDate()
            val value = timestamptz.format(DataTypeUtils.TIMESTAMPTZ_FORMATTER)
            return AbstractJdbcCompatibleSourceOperations.Companion.resolveEra(localDate, value)
        } else {
            if (!loggedUnknownTimestampWithTimeZoneClass) {
                LOGGER.info(
                    "Unknown class for Timestamp with time zone data type" + timestamp.javaClass
                )
                loggedUnknownTimestampWithTimeZoneClass = true
            }
            val instant = Instant.parse(timestamp.toString())
            val offsetDateTime = OffsetDateTime.ofInstant(instant, ZoneOffset.UTC)
            val timestamptz = ZonedDateTime.from(offsetDateTime)
            val localDate = timestamptz.toLocalDate()
            val value = timestamptz.format(DataTypeUtils.TIMESTAMPTZ_FORMATTER)
            return AbstractJdbcCompatibleSourceOperations.Companion.resolveEra(localDate, value)
        }
    }

    /** See [.convertToTimestampWithTimezone] for explanation of the weird things happening here. */
    @JvmStatic
    fun convertToTimestamp(timestamp: Any): String {
        if (timestamp is Timestamp) {
            // Snapshot mode
            val localDateTime: LocalDateTime = timestamp.toLocalDateTime()
            return AbstractJdbcCompatibleSourceOperations.Companion.resolveEra(
                timestamp,
                if (hasZeroSecondsAndNanos(localDateTime.toLocalTime()))
                    localDateTime.format(DataTypeUtils.TIMESTAMP_FORMATTER)
                else localDateTime.toString()
            )
        } else if (timestamp is Instant) {
            // Incremental mode
            return AbstractJdbcCompatibleSourceOperations.Companion.resolveEra(
                timestamp.atZone(ZoneOffset.UTC).toLocalDate(),
                timestamp
                    .atOffset(ZoneOffset.UTC)
                    .toLocalDateTime()
                    .format(DataTypeUtils.TIMESTAMP_FORMATTER)
            )
        } else if (timestamp is LocalDateTime) {
            val date: LocalDate = timestamp.toLocalDate()
            return AbstractJdbcCompatibleSourceOperations.Companion.resolveEra(
                date,
                if (hasZeroSecondsAndNanos(timestamp.toLocalTime()))
                    timestamp.format(DataTypeUtils.TIMESTAMP_FORMATTER)
                else timestamp.toString()
            )
        } else {
            if (!loggedUnknownTimestampClass) {
                LOGGER.info("Unknown class for Timestamp data type" + timestamp.javaClass)
                loggedUnknownTimestampClass = true
            }
            val localDateTime = LocalDateTime.parse(timestamp.toString())
            val date = localDateTime.toLocalDate()
            return AbstractJdbcCompatibleSourceOperations.Companion.resolveEra(
                date,
                if (hasZeroSecondsAndNanos(localDateTime.toLocalTime()))
                    localDateTime.format(DataTypeUtils.TIMESTAMP_FORMATTER)
                else localDateTime.toString()
            )
        }
    }

    /** See [.convertToTimestampWithTimezone] for explanation of the weird things happening here. */
    @JvmStatic
    fun convertToDate(date: Any): String {
        if (date is Date) {
            // Snapshot mode
            val localDate = date.toLocalDate()
            return AbstractJdbcCompatibleSourceOperations.Companion.resolveEra(
                date,
                localDate.format(DataTypeUtils.DATE_FORMATTER)
            )
        } else if (date is LocalDate) {
            // Incremental mode
            return AbstractJdbcCompatibleSourceOperations.Companion.resolveEra(
                date,
                date.format(DataTypeUtils.DATE_FORMATTER)
            )
        } else if (date is Integer) {
            // Incremental mode
            return LocalDate.ofEpochDay(date.toLong()).format(DataTypeUtils.DATE_FORMATTER)
        } else {
            if (!loggedUnknownDateClass) {
                LOGGER.info("Unknown class for Date data type" + date.javaClass)
                loggedUnknownDateClass = true
            }
            val localDate = LocalDate.parse(date.toString())
            return AbstractJdbcCompatibleSourceOperations.Companion.resolveEra(
                localDate,
                localDate.format(DataTypeUtils.DATE_FORMATTER)
            )
        }
    }

    @JvmStatic
    fun convertToTime(time: Any): String {
        if (time is Time) {
            return formatTime(time.toLocalTime())
        } else if (time is LocalTime) {
            return formatTime(time)
        } else if (time is Duration) {
            val value = time.toNanos()
            if (value >= 0 && value < TimeUnit.DAYS.toNanos(1)) {
                return formatTime(LocalTime.ofNanoOfDay(value))
            } else {
                val updatedValue =
                    min(abs(value.toDouble()), LocalTime.MAX.toNanoOfDay().toDouble()).toLong()
                LOGGER.debug(
                    "Time values must use number of nanoseconds greater than 0 and less than 86400000000000 but its {}, converting to {} ",
                    value,
                    updatedValue
                )
                return formatTime(LocalTime.ofNanoOfDay(updatedValue))
            }
        } else {
            if (!loggedUnknownTimeClass) {
                LOGGER.info("Unknown class for Time data type" + time.javaClass)
                loggedUnknownTimeClass = true
            }

            val valueAsString = time.toString()
            if (valueAsString.startsWith("24")) {
                LOGGER.debug("Time value {} is above range, converting to 23:59:59", valueAsString)
                return LocalTime.MAX.toString()
            }
            return formatTime(LocalTime.parse(valueAsString))
        }
    }

    @JvmStatic
    private fun formatTime(localTime: LocalTime): String {
        return if (hasZeroSecondsAndNanos(localTime)) localTime.format(DataTypeUtils.TIME_FORMATTER)
        else localTime.toString()
    }

    @JvmStatic
    fun hasZeroSecondsAndNanos(localTime: LocalTime): Boolean {
        return (localTime.second == 0 && localTime.nano == 0)
    }

    @Throws(SQLException::class)
    @JvmStatic
    fun putJavaSQLDate(node: ObjectNode, columnName: String?, resultSet: ResultSet, index: Int) {
        val date = resultSet.getDate(index)
        node.put(columnName, convertToDate(date))
    }

    @Throws(SQLException::class)
    @JvmStatic
    fun putJavaSQLTime(node: ObjectNode, columnName: String?, resultSet: ResultSet, index: Int) {
        // resultSet.getTime() will lose nanoseconds precision
        val localTime = resultSet.getTimestamp(index).toLocalDateTime().toLocalTime()
        node.put(columnName, convertToTime(localTime))
    }
}
