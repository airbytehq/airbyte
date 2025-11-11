/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db

import java.sql.Date
import java.sql.SQLException
import java.text.DateFormat
import java.text.SimpleDateFormat
import java.time.*
import java.time.format.DateTimeFormatter
import java.util.function.Function
import kotlin.math.abs

/**
 * TODO : Replace all the DateTime related logic of this class with
 * [io.airbyte.cdk.db.jdbc.DateTimeConverter]
 */
object DataTypeUtils {
    const val DATE_FORMAT_PATTERN: String = "yyyy-MM-dd'T'HH:mm:ss'Z'"

    const val DATE_FORMAT_WITH_MILLISECONDS_PATTERN: String = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'"

    @JvmField val TIME_FORMATTER: DateTimeFormatter = DateTimeFormatter.ofPattern("HH:mm:ss.SSSSSS")
    @JvmField
    val TIMESTAMP_FORMATTER: DateTimeFormatter =
        DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS")
    @JvmField
    val TIMETZ_FORMATTER: DateTimeFormatter = DateTimeFormatter.ofPattern("HH:mm:ss.SSSSSSXXX")
    @JvmField
    val TIMESTAMPTZ_FORMATTER: DateTimeFormatter =
        DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSSXXX")
    @JvmField
    val OFFSETDATETIME_FORMATTER: DateTimeFormatter =
        DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSSSSSS XXX")
    @JvmField val DATE_FORMATTER: DateTimeFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd")

    @JvmStatic
    val dateFormat: DateFormat
        // wrap SimpleDateFormat in a function because SimpleDateFormat is not threadsafe as a
        // static final.
        get() =
            SimpleDateFormat(DATE_FORMAT_PATTERN) // Quoted "Z" to indicate UTC, no timezone offset;

    val dateFormatMillisPattern: DateFormat
        // wrap SimpleDateFormat in a function because SimpleDateFormat is not threadsafe as a
        // static final.
        get() = SimpleDateFormat(DATE_FORMAT_WITH_MILLISECONDS_PATTERN)

    @JvmStatic
    fun <T> returnNullIfInvalid(valueProducer: DataTypeSupplier<T>): T? {
        return returnNullIfInvalid(valueProducer, Function { _: T -> true })
    }

    @JvmStatic
    fun <T> returnNullIfInvalid(
        valueProducer: DataTypeSupplier<T>,
        isValidFn: Function<T, Boolean>
    ): T? {
        // Some edge case values (e.g: Infinity, NaN) have no java or JSON equivalent, and will
        // throw an
        // exception when parsed. We want to parse those
        // values as null.
        // This method reduces error handling boilerplate.
        try {
            val value = valueProducer.apply()
            return if (isValidFn.apply(value)) value else null
        } catch (e: SQLException) {
            return null
        }
    }

    @JvmStatic
    fun <T> throwExceptionIfInvalid(valueProducer: DataTypeSupplier<T>): T? {
        return throwExceptionIfInvalid(valueProducer, Function { _: T -> true })
    }

    @JvmStatic
    fun <T> throwExceptionIfInvalid(
        valueProducer: DataTypeSupplier<T>,
        isValidFn: Function<T, Boolean>
    ): T? {
        // Some edge case values (e.g: Infinity, NaN) have no java or JSON equivalent, and will
        // throw an
        // exception when parsed. We want to parse those
        // values as null.
        // This method reduces error handling boilerplate.
        try {
            val value = valueProducer.apply()
            return if (isValidFn.apply(value)) value
            else throw SQLException("Given value is not valid.")
        } catch (e: SQLException) {
            return null
        }
    }

    @JvmStatic
    fun toISO8601StringWithMicroseconds(instant: Instant): String {
        val dateWithMilliseconds = dateFormatMillisPattern.format(Date.from(instant))
        return dateWithMilliseconds.substring(0, 23) +
            calculateMicrosecondsString(instant.nano) +
            dateWithMilliseconds.substring(23)
    }

    private fun calculateMicrosecondsString(nano: Int): String {
        val microSeconds = (nano / 1000) % 1000
        val result =
            if (microSeconds < 10) {
                "00$microSeconds"
            } else if (microSeconds < 100) {
                "0$microSeconds"
            } else {
                "" + microSeconds
            }
        return result
    }

    @JvmStatic
    fun toISO8601StringWithMilliseconds(epochMillis: Long): String {
        return dateFormatMillisPattern.format(Date.from(Instant.ofEpochMilli(epochMillis)))
    }

    @JvmStatic
    fun toISO8601String(epochMillis: Long): String {
        return dateFormat.format(Date.from(Instant.ofEpochMilli(epochMillis)))
    }

    @JvmStatic
    fun toISO8601String(date: java.util.Date?): String {
        return dateFormat.format(date)
    }

    @JvmStatic
    fun toISOTimeString(dateTime: LocalDateTime): String {
        return DateTimeFormatter.ISO_TIME.format(dateTime.toLocalTime())
    }

    @JvmStatic
    fun toISO8601String(date: LocalDate): String {
        return toISO8601String(date.atStartOfDay())
    }

    @JvmStatic
    fun toISO8601String(date: LocalDateTime): String {
        return date.format(DateTimeFormatter.ofPattern(DATE_FORMAT_PATTERN))
    }

    @JvmStatic
    fun toISO8601String(date: OffsetDateTime): String {
        return date.format(OFFSETDATETIME_FORMATTER)
    }

    @JvmStatic
    fun toISO8601String(duration: Duration): String {
        return dateFormat.format(
            Date.from(
                Instant.ofEpochSecond(
                    abs(duration.seconds.toDouble()).toLong(),
                    abs(duration.nano.toDouble()).toLong()
                )
            )
        )
    }
}
