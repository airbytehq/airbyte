/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.jdbc.JdbcAccessor
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.jdbc.SymmetricJdbcFieldType
import io.airbyte.cdk.jdbc.TimestampAccessor
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.sql.Timestamp
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneOffset

// Snowflake timestamps can have up to 9 decimal places (nanoseconds), but destinations may only
// support 6 (microseconds). Rounded up, not down: this value is also used as a cursor bound for
// incremental sync, and flooring it can make it compare as less than the row it should include.
private fun roundUpToMicros(localDateTime: LocalDateTime): LocalDateTime {
    val remainderNanos = localDateTime.nano % 1000
    return if (remainderNanos == 0) {
        localDateTime
    } else {
        localDateTime.plusNanos((1000 - remainderNanos).toLong())
    }
}

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
        stmt.setTimestamp(paramIdx, Timestamp.valueOf(value))
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
