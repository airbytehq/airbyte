/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.databricks

import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeParseException

/**
 * Custom field type for Databricks TIMESTAMP types.
 *
 * Databricks returns timestamp values as strings, so we need to parse them into OffsetDateTime
 * objects for proper handling.
 */
data object DatabricksOffsetDateTimeFieldType :
    LosslessJdbcFieldType<OffsetDateTime, OffsetDateTime>(
        LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
        // Custom getter that handles string timestamps from Databricks
        { rs, colIdx ->
            val value = rs.getString(colIdx)
            if (value == null) {
                null
            } else {
                try {
                    // Try to parse as ISO-8601 timestamp
                    OffsetDateTime.parse(value)
                } catch (e: DateTimeParseException) {
                    try {
                        // Try to parse as timestamp without timezone and assume UTC
                        val formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
                        val localDateTime = java.time.LocalDateTime.parse(value, formatter)
                        localDateTime.atOffset(java.time.ZoneOffset.UTC)
                    } catch (e2: DateTimeParseException) {
                        // If all else fails, try to parse as timestamp with microseconds
                        val formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSSSSS")
                        val localDateTime = java.time.LocalDateTime.parse(value, formatter)
                        localDateTime.atOffset(java.time.ZoneOffset.UTC)
                    }
                }
            }
        },
        OffsetDateTimeCodec,
        OffsetDateTimeCodec,
        // Convert OffsetDateTime to Timestamp for Databricks JDBC compatibility
        { stmt, paramIdx, value ->
            val instant = value.toInstant()
            val timestamp = java.sql.Timestamp.from(instant)
            timestamp.nanos = instant.nano
            stmt.setTimestamp(paramIdx, timestamp)
        }
    )
