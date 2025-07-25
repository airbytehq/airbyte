/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.jdbc.TimestampAccessor
import java.time.OffsetDateTime
import java.time.ZoneOffset

/**
 * Custom field type for Snowflake TIMESTAMP_TZ and TIMESTAMP_LTZ types.
 *
 * The Snowflake JDBC driver does not support getObject(int, Class<OffsetDateTime>) and throws an
 * exception. This implementation works around that limitation by retrieving the timestamp as
 * LocalDateTime and converting it to OffsetDateTime with UTC timezone.
 *
 * Related Snowflake issue: SNOW-895829
 */
data object SnowflakeOffsetDateTimeFieldType :
    LosslessJdbcFieldType<OffsetDateTime, OffsetDateTime>(
        LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
        // Use a custom getter that converts LocalDateTime to OffsetDateTime
        { rs, colIdx ->
            val localDateTime = TimestampAccessor.get(rs, colIdx)
            localDateTime?.atOffset(ZoneOffset.UTC)
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
