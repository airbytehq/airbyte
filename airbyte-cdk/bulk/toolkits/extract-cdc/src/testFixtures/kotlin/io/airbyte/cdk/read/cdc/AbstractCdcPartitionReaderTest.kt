/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ClockFactory
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.IntFieldType
import io.airbyte.cdk.discover.TestMetaFieldDecorator
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.FieldValueChange
import io.airbyte.cdk.read.Global
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamRecordConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.debezium.document.DocumentReader
import io.debezium.document.DocumentWriter
import io.debezium.relational.history.HistoryRecord
import java.time.Duration
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withTimeout
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * This test class verifies that the [CdcPartitionReader] is able to correctly start and stop the
 * Debezium Engine. As there is no useful way to mock the Debezium Engine, the test is actually an
 * integration test and this class is subclassed for multiple Debezium implementations which connect
 * to a corresponding testcontainer data source.
 */
abstract class AbstractCdcPartitionReaderTest<T : Comparable<T>, C : AutoCloseable>(
    namespace: String?,
    val heartbeat: Duration = Duration.ofMillis(100),
    val timeout: Duration = Duration.ofSeconds(10),
) : CdcPartitionReaderDebeziumOperations<T> {

    val stream =
        Stream(
            id = StreamIdentifier.from(StreamDescriptor().withName("tbl").withNamespace(namespace)),
            schema = setOf(Field("v", IntFieldType), TestMetaFieldDecorator.GlobalCursor),
            configuredSyncMode = ConfiguredSyncMode.INCREMENTAL,
            configuredPrimaryKey = null,
            configuredCursor = TestMetaFieldDecorator.GlobalCursor,
        )

    val global: Global
        get() = Global(listOf(stream))

    abstract fun createContainer(): C
    abstract fun C.createStream()
    abstract fun C.insert12345()
    abstract fun C.update135()
    abstract fun C.delete24()

    abstract fun C.currentPosition(): T
    abstract fun C.syntheticInput(): DebeziumInput
    abstract fun C.debeziumProperties(): Map<String, String>

    @Test
    /**
     * The [integrationTest] method sets up (and tears down) a testcontainer for the data source
     * using [createContainer] and provisions it using [createStream], [insert12345], [update135]
     * and [delete24].
     *
     * While doing so, it creates several [CdcPartitionReader] instances using [currentPosition],
     * [syntheticInput] and [debeziumProperties], and exercises all [PartitionReader] methods.
     */
    fun integrationTest() {
        createContainer().use { container: C ->
            container.createStream()
            val p0: T = container.currentPosition()
            val r0: ReadResult = read(container.syntheticInput(), p0)
            Assertions.assertEquals(emptyList<Record>(), r0.records)
            Assertions.assertNotEquals(
                CdcPartitionReader.CloseReason.RECORD_REACHED_TARGET_POSITION,
                r0.closeReason,
            )

            container.insert12345()
            val insert =
                listOf<Record>(
                    Insert(1, 1),
                    Insert(2, 2),
                    Insert(3, 3),
                    Insert(4, 4),
                    Insert(5, 5),
                )
            container.update135()
            val update =
                listOf<Record>(
                    Update(1, 6),
                    Update(3, 7),
                    Update(5, 8),
                )
            val p1: T = container.currentPosition()
            container.delete24()
            val delete =
                listOf<Record>(
                    Delete(2),
                    Delete(4),
                )
            val p2: T = container.currentPosition()

            val input = DebeziumInput(container.debeziumProperties(), r0.state, isSynthetic = false)
            val r1: ReadResult = read(input, p1)
            Assertions.assertEquals(insert + update, r1.records.take(insert.size + update.size))
            Assertions.assertNotNull(r1.closeReason)

            val r2: ReadResult = read(input, p2)
            Assertions.assertEquals(
                insert + update + delete,
                r2.records.take(insert.size + update.size + delete.size),
            )
            Assertions.assertNotNull(r2.closeReason)
            Assertions.assertNotEquals(
                CdcPartitionReader.CloseReason.RECORD_REACHED_TARGET_POSITION,
                r2.closeReason
            )
        }
    }

    private fun read(
        input: DebeziumInput,
        upperBound: T,
    ): ReadResult {
        val outputConsumer = BufferingOutputConsumer(ClockFactory().fixed())
        val streamRecordConsumers: Map<StreamIdentifier, StreamRecordConsumer> =
            mapOf(
                stream.id to
                    object : StreamRecordConsumer {
                        override val stream: Stream = this@AbstractCdcPartitionReaderTest.stream

                        override fun accept(
                            recordData: ObjectNode,
                            changes: Map<Field, FieldValueChange>?
                        ) {
                            outputConsumer.accept(
                                AirbyteRecordMessage()
                                    .withStream(stream.name)
                                    .withNamespace(stream.namespace)
                                    .withData(recordData)
                            )
                        }
                    }
            )
        val reader =
            CdcPartitionReader(
                ConcurrencyResource(1),
                streamRecordConsumers,
                this,
                upperBound,
                input,
            )
        Assertions.assertEquals(
            PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN,
            reader.tryAcquireResources(),
        )
        val checkpoint: PartitionReadCheckpoint
        try {
            runBlocking {
                try {
                    withTimeout(timeout.toMillis()) { reader.run() }
                } catch (_: TimeoutCancellationException) {}
            }
            checkpoint = reader.checkpoint()
        } finally {
            reader.releaseResources()
        }
        // Sanity checks. If any of these fail, particularly after a debezium version change,
        // it's important to understand why.
        Assertions.assertEquals(checkpoint.numRecords.toInt(), outputConsumer.records().size)
        Assertions.assertEquals(checkpoint.numRecords, reader.numEmittedRecords.get())
        Assertions.assertEquals(
            reader.numEvents.get(),
            reader.numEmittedRecords.get() +
                reader.numDiscardedRecords.get() +
                reader.numHeartbeats.get() +
                reader.numTombstones.get()
        )
        Assertions.assertEquals(0, reader.numDiscardedRecords.get())
        Assertions.assertEquals(0, reader.numEventsWithoutSourceRecord.get())
        Assertions.assertEquals(0, reader.numSourceRecordsWithoutPosition.get())
        Assertions.assertEquals(0, reader.numEventValuesWithoutPosition.get())
        return ReadResult(
            outputConsumer.records().map { Jsons.treeToValue(it.data, Record::class.java) },
            deserialize(checkpoint.opaqueStateValue),
            reader.closeReasonReference.get(),
        )
    }

    data class ReadResult(
        val records: List<Record>,
        val state: DebeziumState,
        val closeReason: CdcPartitionReader.CloseReason?,
    )

    @JsonTypeInfo(use = JsonTypeInfo.Id.MINIMAL_CLASS)
    @JsonSubTypes(
        JsonSubTypes.Type(value = Insert::class),
        JsonSubTypes.Type(value = Update::class),
        JsonSubTypes.Type(value = Delete::class),
    )
    sealed interface Record {
        val id: Int
    }
    data class Insert(override val id: Int, val v: Int) : Record
    data class Update(override val id: Int, val v: Int) : Record
    data class Delete(override val id: Int) : Record

    override fun deserialize(
        key: DebeziumRecordKey,
        value: DebeziumRecordValue,
        stream: Stream,
    ): DeserializedRecord {
        val id: Int = key.element("id").asInt()
        val after: Int? = value.after["v"]?.asInt()
        val record: Record =
            if (after == null) {
                Delete(id)
            } else if (value.before["v"] == null) {
                Insert(id, after)
            } else {
                Update(id, after)
            }
        return DeserializedRecord(
            data = Jsons.valueToTree(record) as ObjectNode,
            changes = emptyMap(),
        )
    }

    override fun findStreamNamespace(key: DebeziumRecordKey, value: DebeziumRecordValue): String? =
        stream.id.namespace

    override fun findStreamName(key: DebeziumRecordKey, value: DebeziumRecordValue): String? =
        stream.id.name

    override fun serialize(debeziumState: DebeziumState): OpaqueStateValue =
        Jsons.valueToTree(
            mapOf(
                "offset" to
                    debeziumState.offset.wrapped
                        .map {
                            Jsons.writeValueAsString(it.key) to Jsons.writeValueAsString(it.value)
                        }
                        .toMap(),
                "schemaHistory" to
                    debeziumState.schemaHistory?.wrapped?.map {
                        DocumentWriter.defaultWriter().write(it.document())
                    },
            ),
        )

    private fun deserialize(opaqueStateValue: OpaqueStateValue): DebeziumState {
        val offsetNode: ObjectNode = opaqueStateValue["offset"] as ObjectNode
        val offset =
            DebeziumOffset(
                offsetNode
                    .fields()
                    .asSequence()
                    .map { Jsons.readTree(it.key) to Jsons.readTree(it.value.asText()) }
                    .toMap(),
            )
        val historyNode: ArrayNode =
            opaqueStateValue["schemaHistory"] as? ArrayNode
                ?: return DebeziumState(offset, schemaHistory = null)
        val schemaHistory =
            DebeziumSchemaHistory(
                historyNode.elements().asSequence().toList().map {
                    HistoryRecord(DocumentReader.defaultReader().read(it.asText()))
                },
            )
        return DebeziumState(offset, schemaHistory)
    }
}
