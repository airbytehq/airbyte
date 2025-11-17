/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.formatter

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.message.DestinationRecordJsonSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
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
}
