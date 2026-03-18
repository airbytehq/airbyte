/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.message.DestinationRecordJsonSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.util.UUID
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class BigQueryRecordFormatterTest {
    @Test
    fun testNulledTimestamp() {
        val formatter =
            BigQueryRecordFormatter(
                ColumnNameMapping(mapOf("test" to "test")),
                legacyRawTablesOnly = false,
            )
        val formatted =
            formatter.formatRecord(
                DestinationRecordRaw(
                    DestinationStream(
                        unmappedNamespace = "namespace",
                        unmappedName = "name",
                        Append,
                        ObjectType(
                            linkedMapOf("test" to FieldType(TimestampTypeWithTimezone, true))
                        ),
                        generationId = 42,
                        minimumGenerationId = 0,
                        syncId = 42,
                        namespaceMapper = NamespaceMapper(),
                    ),
                    DestinationRecordJsonSource(
                        AirbyteMessage()
                            .withRecord(
                                AirbyteRecordMessage()
                                    .withEmittedAt(1234)
                                    .withData(
                                        Jsons.readTree(
                                            // Somewhat ridiculous test setup.
                                            // Our timestamp parser only recognizes years between
                                            // 0001 - 9999,
                                            // and bigquery supports anything in that range.
                                            // So we set our offset to a negative number, because
                                            // bigquery translates everything to UTC >.>
                                            """{"test": "9999-12-31T23:59:59.999999-08"}"""
                                        )
                                    )
                            )
                    ),
                    serializedSizeBytes = 42,
                    airbyteRawId = UUID.fromString("129b0dc6-826a-4e86-a50f-33250cbf63c2"),
                )
            )
        assertEquals(
            """{"_airbyte_raw_id":"129b0dc6-826a-4e86-a50f-33250cbf63c2","_airbyte_extracted_at":"1970-01-01 00:00:01.234000+00:00","_airbyte_generation_id":42,"_airbyte_meta":{"sync_id":42,"changes":[{"field":"test","change":"NULLED","reason":"DESTINATION_FIELD_SIZE_LIMITATION"}]}}""",
            formatted
        )
    }

    @Test
    fun `timestamps with nanosecond precision are truncated to microseconds`() {
        // 7 fractional digits (100-nanosecond precision from SQL Server DATETIME2(7))
        // should be truncated to 6 digits (microsecond precision) for BigQuery compatibility

        val tsWithTz = EnrichedAirbyteValue(
            abValue = TimestampWithTimezoneValue(
                OffsetDateTime.parse("2026-03-03T14:59:33.4902601Z")
            ),
            type = TimestampTypeWithTimezone,
            name = "test_ts_tz",
            airbyteMetaField = null,
        )
        val formattedTsWithTz = BigQueryRecordFormatter.formatTimestampWithTimezone(tsWithTz)
        // Should have at most 6 fractional digits
        assertFalse(
            formattedTsWithTz.contains(".4902601"),
            "Expected 7-digit nanoseconds to be truncated, got: $formattedTsWithTz"
        )
        assertTrue(
            formattedTsWithTz.contains(".490260"),
            "Expected truncation to 6 digits (microseconds), got: $formattedTsWithTz"
        )

        val tsWithoutTz = EnrichedAirbyteValue(
            abValue = TimestampWithoutTimezoneValue(
                LocalDateTime.parse("2026-03-03T14:59:33.4902601")
            ),
            type = TimestampTypeWithoutTimezone,
            name = "test_ts_no_tz",
            airbyteMetaField = null,
        )
        val formattedTsWithoutTz = BigQueryRecordFormatter.formatTimestampWithoutTimezone(tsWithoutTz)
        assertFalse(
            formattedTsWithoutTz.contains(".4902601"),
            "Expected 7-digit nanoseconds to be truncated, got: $formattedTsWithoutTz"
        )
        assertTrue(
            formattedTsWithoutTz.contains(".490260"),
            "Expected truncation to 6 digits (microseconds), got: $formattedTsWithoutTz"
        )

        val timeWithoutTz = EnrichedAirbyteValue(
            abValue = TimeWithoutTimezoneValue(
                LocalTime.parse("14:59:33.4902601")
            ),
            type = TimeTypeWithoutTimezone,
            name = "test_time_no_tz",
            airbyteMetaField = null,
        )
        val formattedTimeWithoutTz = BigQueryRecordFormatter.formatTimeWithoutTimezone(timeWithoutTz)
        assertFalse(
            formattedTimeWithoutTz.contains(".4902601"),
            "Expected 7-digit nanoseconds to be truncated, got: $formattedTimeWithoutTz"
        )

        val timeWithTz = EnrichedAirbyteValue(
            abValue = TimeWithTimezoneValue(
                OffsetTime.parse("14:59:33.4902601+02:00")
            ),
            type = TimeTypeWithTimezone,
            name = "test_time_tz",
            airbyteMetaField = null,
        )
        val formattedTimeWithTz = BigQueryRecordFormatter.formatTimeWithTimezone(timeWithTz)
        assertFalse(
            formattedTimeWithTz.contains(".4902601"),
            "Expected 7-digit nanoseconds to be truncated, got: $formattedTimeWithTz"
        )
    }
}
