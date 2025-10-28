/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import java.time.temporal.ChronoUnit

private val log = KotlinLogging.logger {}

/**
 * Utility class to calculate cutoff time for "Exclude Today's Data" feature. This ensures that
 * incremental syncs using temporal cursor fields only include data up until midnight of the current
 * day.
 */
object MsSqlServerCursorCutoffTimeProvider {

    private val ISO_LOCAL_DATE: DateTimeFormatter = DateTimeFormatter.ISO_LOCAL_DATE
    private val ISO_OFFSET_DATE_TIME: DateTimeFormatter = DateTimeFormatter.ISO_OFFSET_DATE_TIME
    private val TIMESTAMPTZ_FORMATTER: DateTimeFormatter =
        DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSSSSS xxx")
    private val SQL_SERVER_DATETIME_FORMATTER: DateTimeFormatter =
        MsSqlServerJdbcPartitionFactory.outputDateFormatter

    /**
     * Calculates the cutoff time for a cursor field based on its type.
     *
     * @param cursorField The cursor field
     * @param nowInstant The current instant (for testing)
     * @return The cutoff time as JsonNode, or null if not applicable
     */
    fun getCutoffTime(cursorField: Field, nowInstant: Instant = Instant.now()): JsonNode? {

        return when (cursorField.type.airbyteSchemaType) {
            is LeafAirbyteSchemaType -> {
                when (cursorField.type.airbyteSchemaType as LeafAirbyteSchemaType) {
                    LeafAirbyteSchemaType.DATE -> {
                        // For DATE fields, exclude today by setting cutoff to today's date
                        // This means we include records < today's date (i.e., yesterday and before)
                        val today = nowInstant.atOffset(ZoneOffset.UTC).toLocalDate()
                        val cutoffValue = Jsons.valueToTree<JsonNode>(ISO_LOCAL_DATE.format(today))
                        log.info {
                            "DATE cutoff for field '${cursorField.id}': ${cutoffValue.asText()}"
                        }
                        cutoffValue
                    }
                    LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE -> {
                        // For TIMESTAMP fields, set cutoff to start of today (00:00:00)
                        // Use local datetime without timezone for SQL Server DATETIME
                        val startOfToday =
                            nowInstant
                                .atOffset(ZoneOffset.UTC)
                                .truncatedTo(ChronoUnit.DAYS)
                                .toLocalDateTime()
                        val cutoffValue =
                            Jsons.valueToTree<JsonNode>(
                                SQL_SERVER_DATETIME_FORMATTER.format(startOfToday)
                            )
                        log.info {
                            "TIMESTAMP_WITHOUT_TIMEZONE cutoff for field '${cursorField.id}': ${cutoffValue.asText()}"
                        }
                        cutoffValue
                    }
                    LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE -> {
                        // For TIME fields, set cutoff to start of today (00:00:00)
                        val startOfToday =
                            nowInstant.atOffset(ZoneOffset.UTC).truncatedTo(ChronoUnit.DAYS)
                        Jsons.valueToTree(ISO_OFFSET_DATE_TIME.format(startOfToday))
                    }
                    LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE -> {
                        // For TIMESTAMP WITH TIMEZONE fields, set cutoff to start of today
                        // (00:00:00)
                        val startOfToday =
                            nowInstant.atOffset(ZoneOffset.UTC).truncatedTo(ChronoUnit.DAYS)
                        Jsons.valueToTree(TIMESTAMPTZ_FORMATTER.format(startOfToday))
                    }
                    else -> {
                        log.warn {
                            "Only temporal cursors can exclude today's data. " +
                                "Field '${cursorField.id}' has type '${cursorField.type}' which is not supported."
                        }
                        null
                    }
                }
            }
            else -> {
                log.warn {
                    "Only temporal cursors can exclude today's data. " +
                        "Field '${cursorField.id}' has non-leaf type '${cursorField.type}' which is not supported."
                }
                null
            }
        }
    }

    /** Checks if a cursor field type supports the "Exclude Today's Data" feature. */
    fun isTemporalType(cursorField: Field): Boolean {
        val schemaType = cursorField.type.airbyteSchemaType
        return schemaType is LeafAirbyteSchemaType &&
            schemaType in
                listOf(
                    LeafAirbyteSchemaType.DATE,
                    LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
                    LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
                    LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
                )
    }
}
