/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import com.fasterxml.jackson.databind.JsonNode
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
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class PostgresSourceDebeziumOperationsDeserializeRecordTest {

    private val config = mockk<PostgresSourceConfiguration>(relaxed = true)
    private val connectionFactory = mockk<PostgresSourceJdbcConnectionFactory>(relaxed = true)
    private val replicationSlotManager = mockk<ReplicationSlotManager>(relaxed = true)

    private val operations =
        PostgresSourceDebeziumOperations(config, connectionFactory, replicationSlotManager, null)

    private fun buildStream(
        fields: Set<EmittedField>,
    ): Stream =
        Stream(
            id =
                StreamIdentifier.from(
                    io.airbyte.protocol.models.v0
                        .StreamDescriptor()
                        .withName("test_table")
                        .withNamespace("public")
                ),
            schema =
                fields +
                    setOf(
                        CommonMetaField.CDC_UPDATED_AT,
                        CommonMetaField.CDC_DELETED_AT,
                        PostgresSourceCdcMetaFields.CDC_LSN,
                    ),
            configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
            configuredPrimaryKey = null,
            configuredCursor = null,
        )

    private fun buildDebeziumValue(after: JsonNode): DebeziumRecordValue {
        val wrapped =
            Jsons.objectNode().apply {
                set<JsonNode>("before", Jsons.nullNode())
                set<JsonNode>("after", after)
                set<JsonNode>(
                    "source",
                    Jsons.objectNode().apply {
                        put("ts_ms", 1700000000000L)
                        put("lsn", 12345L)
                        put("schema", "public")
                        put("table", "test_table")
                    },
                )
                put("op", "c")
            }
        return DebeziumRecordValue(wrapped)
    }

    private fun buildDebeziumKey(): DebeziumRecordKey =
        DebeziumRecordKey(Jsons.objectNode().put("id", 1))

    @Test
    fun `array field with proper ArrayNode is deserialized correctly`() {
        val stream =
            buildStream(
                setOf(
                    EmittedField("id", IntFieldType),
                    EmittedField("tags", ArrayFieldType(StringFieldType)),
                ),
            )
        val after =
            Jsons.objectNode().apply {
                put("id", 1)
                set<JsonNode>("tags", Jsons.arrayNode().add("a").add("b"))
            }
        val record =
            operations.deserializeRecord(buildDebeziumKey(), buildDebeziumValue(after), stream)
        assertTrue(
            record.changes.isEmpty(),
            "Expected no deserialization failures for proper ArrayNode"
        )
    }

    @Test
    fun `array field with TextNode containing valid JSON array is recovered`() {
        val stream =
            buildStream(
                setOf(
                    EmittedField("id", IntFieldType),
                    EmittedField("tags", ArrayFieldType(StringFieldType)),
                ),
            )
        // Debezium may emit array columns as a text node containing a JSON array string
        val after =
            Jsons.objectNode().apply {
                put("id", 1)
                put("tags", "[\"x\",\"y\"]")
            }
        val record =
            operations.deserializeRecord(buildDebeziumKey(), buildDebeziumValue(after), stream)
        // The text should be parsed into a JSON array successfully
        assertTrue(
            record.changes.none { it.value == FieldValueChange.DESERIALIZATION_FAILURE_TOTAL },
            "Expected TextNode with valid JSON array to be recovered without total failure",
        )
    }

    @Test
    fun `array field with TextNode containing non-JSON text results in deserialization failure`() {
        val stream =
            buildStream(
                setOf(
                    EmittedField("id", IntFieldType),
                    EmittedField("tags", ArrayFieldType(StringFieldType)),
                ),
            )
        // Postgres-style array literal that is not valid JSON
        val after =
            Jsons.objectNode().apply {
                put("id", 1)
                put("tags", "{hello,world}")
            }
        val record =
            operations.deserializeRecord(buildDebeziumKey(), buildDebeziumValue(after), stream)
        val arrayField = EmittedField("tags", ArrayFieldType(StringFieldType))
        assertEquals(
            FieldValueChange.DESERIALIZATION_FAILURE_TOTAL,
            record.changes[arrayField],
            "Expected DESERIALIZATION_FAILURE_TOTAL for unparseable text array value",
        )
    }

    @Test
    fun `array field with numeric TextNode results in deserialization failure`() {
        val stream =
            buildStream(
                setOf(
                    EmittedField("id", IntFieldType),
                    EmittedField("vals", ArrayFieldType(IntFieldType)),
                ),
            )
        // A plain number TextNode, not an array at all
        val after =
            Jsons.objectNode().apply {
                put("id", 1)
                put("vals", "42")
            }
        val record =
            operations.deserializeRecord(buildDebeziumKey(), buildDebeziumValue(after), stream)
        val arrayField = EmittedField("vals", ArrayFieldType(IntFieldType))
        assertEquals(
            FieldValueChange.DESERIALIZATION_FAILURE_TOTAL,
            record.changes[arrayField],
            "Expected DESERIALIZATION_FAILURE_TOTAL for scalar text in array field",
        )
    }

    @Test
    fun `array field with null value is handled`() {
        val stream =
            buildStream(
                setOf(
                    EmittedField("id", IntFieldType),
                    EmittedField("tags", ArrayFieldType(StringFieldType)),
                ),
            )
        val after =
            Jsons.objectNode().apply {
                put("id", 1)
                putNull("tags")
            }
        val record =
            operations.deserializeRecord(buildDebeziumKey(), buildDebeziumValue(after), stream)
        assertTrue(
            record.changes.isEmpty(),
            "Expected no deserialization failures for null array value"
        )
    }

    @Test
    fun `array field missing from data is handled`() {
        val stream =
            buildStream(
                setOf(
                    EmittedField("id", IntFieldType),
                    EmittedField("tags", ArrayFieldType(StringFieldType)),
                ),
            )
        val after =
            Jsons.objectNode().apply {
                put("id", 1)
                // "tags" field is absent
            }
        val record =
            operations.deserializeRecord(buildDebeziumKey(), buildDebeziumValue(after), stream)
        assertTrue(
            record.changes.isEmpty(),
            "Expected no deserialization failures for missing array field"
        )
    }

    @Test
    fun `non-array fields still work correctly alongside array fix`() {
        val stream =
            buildStream(
                setOf(
                    EmittedField("id", IntFieldType),
                    EmittedField("name", StringFieldType),
                ),
            )
        val after =
            Jsons.objectNode().apply {
                put("id", 1)
                put("name", "test")
            }
        val record =
            operations.deserializeRecord(buildDebeziumKey(), buildDebeziumValue(after), stream)
        assertTrue(
            record.changes.isEmpty(),
            "Expected no deserialization failures for non-array fields"
        )
    }
}
