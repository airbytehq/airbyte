/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.LocalTimeCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.jdbc.JdbcAccessor
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import io.airbyte.cdk.jdbc.TimestampAccessor
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.sql.Timestamp
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import net.snowflake.client.api.resultset.SnowflakeType

/**
 * Nanoseconds are rounded up to microsecond precision (6 decimal places). See [roundUpToMicros].
 */
object SnowflakeLocalDateTimeAccessor : JdbcAccessor<LocalDateTime> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): LocalDateTime? {
        val timestamp = rs.getTimestamp(colIdx)?.takeUnless { rs.wasNull() } ?: return null
        return roundUpToMicros(timestamp.toLocalDateTime())
    }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: LocalDateTime,
    ) {
        // Bind explicitly as TIMESTAMP_NTZ. A plain setTimestamp is interpreted in the session
        // TIMEZONE (America/Los_Angeles by default), which shifts an NTZ cursor bound by the
        // session
        // offset and makes a warm incremental sync skip rows (airbytehq/airbyte#83800).
        stmt.setObject(paramIdx, Timestamp.valueOf(value), SnowflakeType.EXTRA_TYPES_TIMESTAMP_NTZ)
    }
}

/** Custom field type for Snowflake TIMESTAMP_NTZ / DATETIME types, rounded to microseconds. */
object SnowflakeLocalDateTimeFieldType :
    SymmetricJdbcFieldType<LocalDateTime>(
        LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
        SnowflakeLocalDateTimeAccessor,
        LocalDateTimeCodec,
    )

/**
 * Custom field type for Snowflake TIMESTAMP_TZ and TIMESTAMP_LTZ types.
 *
 * The Snowflake JDBC driver does not support getObject(int, Class<OffsetDateTime>) and throws an
 * exception. This implementation works around that limitation by retrieving the timestamp as
 * LocalDateTime and converting it to OffsetDateTime with UTC timezone.
 *
 * Nanoseconds are rounded up to microsecond precision (6 decimal places), see [roundUpToMicros].
 *
 * Related Snowflake issue: SNOW-895829
 */
object SnowflakeOffsetDateTimeFieldType :
    LosslessJdbcFieldType<OffsetDateTime, OffsetDateTime>(
        LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
        // Use a custom getter that converts LocalDateTime to OffsetDateTime
        { rs, colIdx ->
            val localDateTime = TimestampAccessor.get(rs, colIdx)
            if (localDateTime != null) {
                roundUpToMicros(localDateTime).atOffset(ZoneOffset.UTC)
            } else {
                null
            }
        },
        OffsetDateTimeCodec,
        OffsetDateTimeCodec,
        // Convert OffsetDateTime to Timestamp for Snowflake JDBC compatibility
        { stmt, paramIdx, value ->
            val instant = value.toInstant()
            val timestamp = java.sql.Timestamp.from(instant)
            timestamp.nanos = instant.nano
            stmt.setTimestamp(paramIdx, timestamp)
        }
    )

/**
 * Snowflake TIME columns.
 *
 * The Snowflake JDBC driver rejects `getObject(int, LocalTime::class.java)` ("Type passed to
 * 'getObject(int columnIndex,Class<T> type)' is unsupported"), which made the CDK default
 * [io.airbyte.cdk.jdbc.LocalTimeFieldType] emit NULL for every TIME value. `getTime()` keeps only
 * milliseconds, so the value is read through `getTimestamp()`, which carries the full nanosecond
 * precision on the 1970-01-01 date.
 *
 * Nanoseconds are rounded up to microsecond precision like the timestamp types (see
 * [roundUpToMicros]); a value that would round past midnight is capped at 23:59:59.999999.
 */
object SnowflakeLocalTimeAccessor : JdbcAccessor<LocalTime> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): LocalTime? {
        val timestamp = rs.getTimestamp(colIdx)?.takeUnless { rs.wasNull() } ?: return null
        return roundUpToMicros(timestamp.toLocalDateTime().toLocalTime())
    }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: LocalTime,
    ) {
        // Bind as text: Snowflake casts a string bound against a TIME column implicitly, while
        // java.sql.Time would drop the fractional seconds.
        stmt.setString(paramIdx, value.format(LocalTimeCodec.formatter))
    }
}

/** Custom field type for Snowflake TIME, rounded to microseconds. */
object SnowflakeLocalTimeFieldType :
    SymmetricJdbcFieldType<LocalTime>(
        LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
        SnowflakeLocalTimeAccessor,
        LocalTimeCodec,
    )

// Snowflake timestamps can have up to 9 decimal places (nanoseconds), but the Airbyte
// protocol only supports 6 (microseconds). Round up, never down. This value is also used as a
// cursor bound for incremental syncs, and reducing it can make it compare as less than a row with
// higher value that we should include in the WHERE clause of the subsequent sync.
private fun roundUpToMicros(localDateTime: LocalDateTime): LocalDateTime {
    val remainderNanos = localDateTime.nano % 1000
    return when {
        remainderNanos == 0 -> localDateTime
        // 9999-12-31 23:59:59.999999999 is a common "end of time" sentinel; rounding it up would
        // produce year 10000, which destinations reject ("time zone displacement out of range").
        localDateTime > MAX_MICROS_DATE_TIME -> MAX_MICROS_DATE_TIME
        else -> localDateTime.plusNanos((1000 - remainderNanos).toLong())
    }
}

private val MAX_MICROS_DATE_TIME: LocalDateTime =
    LocalDateTime.of(9999, 12, 31, 23, 59, 59, 999_999_000)

private val MAX_MICROS_TIME: LocalTime = LocalTime.of(23, 59, 59, 999_999_000)

/** Same rounding as for timestamps, without wrapping past midnight. */
private fun roundUpToMicros(localTime: LocalTime): LocalTime {
    val remainderNanos = localTime.nano % 1000
    return when {
        remainderNanos == 0 -> localTime
        localTime > MAX_MICROS_TIME -> MAX_MICROS_TIME
        else -> localTime.plusNanos((1000 - remainderNanos).toLong())
    }
}
