/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.postgres.cdc

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.DataOrMetaField
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.ArrayFieldType
import io.airbyte.cdk.jdbc.BigDecimalFieldType
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.FieldValueChange
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.cdc.DebeziumRecordKey
import io.airbyte.cdk.read.cdc.DebeziumRecordValue
import io.airbyte.cdk.read.cdc.DeserializedRecord
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.postgres.PostgresSourceJdbcConnectionFactory
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfiguration
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.mockk.mockk
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneOffset
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertNull
import kotlin.test.assertTrue
import org.junit.jupiter.api.Test

/**
 * testing `deserializeRecord` for socket/protobuf output path: every field of the stream
 * schema ends up in the payload, including the ones whose value is NULL, whose key is missing from
 * the Debezium image, or whose mapping failed.
 *
 * The protobuf record consumer reuses one builder for the whole sync and only overwrites the slots of
 * the fields present in the payload, so a field left out of the payload keeps the previous record's
 * value on the wire (oncall 13042).
 */
class PostgresSourceDebeziumOperationsDeserializeRecordTest {

    companion object {
        private const val TRANSACTION_MILLIS: Long = 1_762_000_000_000L
        private const val LSN: Long = 3_575_761_602_216L

        private val ID = EmittedField("id", IntFieldType)
        private val NAME = EmittedField("name", StringFieldType)
        private val AMOUNT = EmittedField("amount", BigDecimalFieldType)
        private val TAGS = EmittedField("tags", ArrayFieldType(StringFieldType))
        private val NOTES = EmittedField("notes", ArrayFieldType(StringFieldType))

        private val SCHEMA: Set<DataOrMetaField> =
            setOf(
                ID,
                NAME,
                AMOUNT,
                TAGS,
                NOTES,
                PostgresSourceCdcMetaFields.CDC_LSN,
                CommonMetaField.CDC_UPDATED_AT,
                CommonMetaField.CDC_DELETED_AT,
            )
    }

    private val ops =
        PostgresSourceDebeziumOperations(
            config = mockk<PostgresSourceConfiguration>(relaxed = true),
            connectionFactory = mockk<PostgresSourceJdbcConnectionFactory>(relaxed = true),
            replicationSlotManager = mockk<ReplicationSlotManager>(relaxed = true),
            startupState = null,
        )

    private val stream =
        Stream(
            id =
                StreamIdentifier.from(
                    StreamDescriptor().withName("test_table").withNamespace("public")
                ),
            schema = SCHEMA,
            configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
            configuredPrimaryKey = listOf(ID),
            configuredCursor = null,
        )

    @Test
    fun `a NULL array is written as an explicit null`() {
        val record = deserialize("""{"id": 1, "name": "null first", "tags": null}""")

        assertExplicitNull(record, "tags")
        assertTrue(record.changes.isEmpty(), "a NULL value is not a change: ${record.changes}")
        assertAllSchemaFieldsPresent(record)
    }

    @Test
    fun `absent column from the image is written as an explicit null`() {
        val record = deserialize("""{"id": 1, "name": "no tags key"}""")

        assertExplicitNull(record, "tags")
        assertTrue(record.changes.isEmpty(), "an absent key is not a change: ${record.changes}")
        assertAllSchemaFieldsPresent(record)
    }

    @Test
    fun `an empty array stays an empty array`() {
        val record = deserialize("""{"id": 1, "tags": []}""")

        val tags = assertNotNull(record.data["tags"])
        assertEquals(emptyList<String>(), tags.fieldValue)
        assertTrue(record.changes.isEmpty())
    }

    @Test
    fun `a populated array is decoded element by element`() {
        val record = deserialize("""{"id": 1, "tags": ["Other", "previously-resolved"]}""")

        val tags = assertNotNull(record.data["tags"])
        assertEquals(listOf("Other", "previously-resolved"), tags.fieldValue)
        assertTrue(record.changes.isEmpty())
    }

    @Test
    fun `array columns are independent of each other within a record`() {
        val record = deserialize("""{"id": 1, "tags": null, "notes": ["kept"]}""")

        assertExplicitNull(record, "tags")
        assertEquals(listOf("kept"), assertNotNull(record.data["notes"]).fieldValue)
    }

    @Test
    fun `a NULL scalar is written as an explicit null`() {
        val record = deserialize("""{"id": 1, "name": null}""")

        assertExplicitNull(record, "name")
        assertTrue(record.changes.isEmpty())
    }

    @Test
    fun `a scalar whose key is absent from the image is written as an explicit null`() {
        val record = deserialize("""{"id": 1}""")

        assertExplicitNull(record, "name")
        assertTrue(record.changes.isEmpty(), "an absent key is not a change: ${record.changes}")
        assertAllSchemaFieldsPresent(record)
    }

    @Test
    fun `a bigDecimal whose mapping fails is written as an explicit null and flagged`() {
        // mapValue() should return a failure and the mapped value is a Kotlin null.
        val record = deserialize("""{"id": 1, "amount": "not-a-number"}""")

        assertExplicitNull(record, "amount")
        assertEquals(
            FieldValueChange.DESERIALIZATION_FAILURE_TOTAL,
            record.changes[AMOUNT],
            "a failed mapping must be flagged in _airbyte_meta.changes",
        )
    }

    @Test
    fun `a delete image carrying only the primary key writes explicit nulls for the rest`() {
        // With REPLICA IDENTITY DEFAULT the `before` image of a delete holds the primary key -
        // every other column has to be nulled out rather than left to the reused
        // protobuf builder.
        val record = deserialize(before = """{"id": 42}""", after = "null")

        assertEquals(42, assertNotNull(record.data["id"]).fieldValue)
        assertExplicitNull(record, "name")
        assertExplicitNull(record, "amount")
        assertExplicitNull(record, "tags")
        assertExplicitNull(record, "notes")
        assertAllSchemaFieldsPresent(record)

        assertEquals(
            transactionTimestamp,
            assertNotNull(record.data[CommonMetaField.CDC_DELETED_AT.id]).fieldValue,
        )
    }

    @Test
    fun `cdc meta fields survive the schema loop`() {
        val record = deserialize("""{"id": 1, "tags": null}""")

        assertEquals(
            transactionTimestamp,
            assertNotNull(record.data[CommonMetaField.CDC_UPDATED_AT.id]).fieldValue,
        )
        assertEquals(
            LSN.toBigDecimal(),
            assertNotNull(record.data[PostgresSourceCdcMetaFields.CDC_LSN.id]).fieldValue,
        )
        // Not a delete, so the deletion timestamp is an explicit null.
        assertExplicitNull(record, CommonMetaField.CDC_DELETED_AT.id)
    }

    private val transactionTimestamp: OffsetDateTime
        get() = OffsetDateTime.ofInstant(Instant.ofEpochMilli(TRANSACTION_MILLIS), ZoneOffset.UTC)

    /**
     * A [before] of `"null"` is an insert. An [after] of `"null"` is a delete, which is how
     * `deserializeRecord` tells them apart (`isDelete = after.isNull`).
     */
    private fun deserialize(after: String, before: String = "null"): DeserializedRecord {
        val value =
            DebeziumRecordValue(
                Jsons.readTree(
                    """
                    {
                      "before": $before,
                      "after": $after,
                      "source": {
                        "schema": "public",
                        "table": "test_table",
                        "ts_ms": $TRANSACTION_MILLIS,
                        "lsn": $LSN
                      }
                    }
                    """.trimIndent()
                )
            )
        return ops.deserializeRecord(DebeziumRecordKey(Jsons.objectNode()), value, stream)
    }

    private fun assertExplicitNull(record: DeserializedRecord, column: String) {
        val fve = assertNotNull(record.data[column], "$column is missing from the record payload")
        assertNull(fve.fieldValue, "$column should hold a null value")
        assertEquals(NullCodec, fve.jsonEncoder, "$column should be encoded with NullCodec")
    }

    private fun assertAllSchemaFieldsPresent(record: DeserializedRecord) {
        assertEquals(
            SCHEMA.map { it.id }.toSet(),
            record.data.keys,
            "every schema field must be written, otherwise its protobuf slot keeps the previous " +
                "record's value",
        )
    }
}
