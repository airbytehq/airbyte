/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import com.fasterxml.jackson.databind.node.NullNode
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.ArrayFieldType
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.FieldValueChange
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.DebeziumRecordKey
import io.airbyte.cdk.read.cdc.DebeziumRecordValue
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.postgres.PostgresSourceJdbcConnectionFactory
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.mockk.mockk
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import org.junit.jupiter.api.Test

class PostgresSourceDebeziumOperationsTest {

    private val operations =
        PostgresSourceDebeziumOperations(
            mockk<PostgresSourceConfiguration>(relaxed = true),
            mockk<PostgresSourceJdbcConnectionFactory>(relaxed = true),
            mockk<ReplicationSlotManager>(relaxed = true),
            null,
        )

    private val loadTypeField = EmittedField("load_type", ArrayFieldType(StringFieldType))

    private val stream =
        Stream(
            id = StreamIdentifier.from(StreamDescriptor().withName("port").withNamespace("public")),
            schema =
                setOf(
                    EmittedField("id", IntFieldType),
                    EmittedField("name", StringFieldType),
                    loadTypeField,
                ),
            configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
            configuredPrimaryKey = listOf(EmittedField("id", IntFieldType)),
            configuredCursor = null,
        )

    private fun recordValue(loadType: com.fasterxml.jackson.databind.JsonNode) =
        DebeziumRecordValue(
            Jsons.objectNode().apply {
                set<com.fasterxml.jackson.databind.JsonNode>("before", NullNode.getInstance())
                set<com.fasterxml.jackson.databind.JsonNode>(
                    "after",
                    Jsons.objectNode().apply {
                        put("id", 1)
                        put("name", "foo")
                        set<com.fasterxml.jackson.databind.JsonNode>("load_type", loadType)
                    },
                )
                set<com.fasterxml.jackson.databind.JsonNode>(
                    "source",
                    Jsons.objectNode().apply {
                        put("ts_ms", 1758580000000L)
                        put("lsn", 12345L)
                        put("schema", "public")
                        put("table", "port")
                    },
                )
            }
        )

    private val key = DebeziumRecordKey(Jsons.objectNode().put("id", 1))

    @Test
    fun `array field with textual debezium value is recorded as total deserialization failure`() {
        val result =
            operations.deserializeRecord(
                key,
                recordValue(Jsons.textNode("__debezium_unavailable_value")),
                stream,
            )
        assertEquals(
            FieldValueChange.DESERIALIZATION_FAILURE_TOTAL,
            result.changes[loadTypeField],
        )
        assertTrue(result.data.containsKey("id"))
        assertTrue(result.data.containsKey("name"))
        assertTrue(result.data.containsKey(CommonMetaField.CDC_UPDATED_AT.id))
    }

    @Test
    fun `array field with json array debezium value is deserialized`() {
        val result =
            operations.deserializeRecord(
                key,
                recordValue(Jsons.arrayNode().add("a").add("b")),
                stream,
            )
        assertTrue(result.changes.isEmpty())
        assertTrue(result.data.containsKey("load_type"))
    }

    @Test
    fun `array field with null debezium value is skipped`() {
        val result = operations.deserializeRecord(key, recordValue(NullNode.getInstance()), stream)
        assertTrue(result.changes.isEmpty())
    }
}
