/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.dlq

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.message.BatchState
import io.airbyte.cdk.load.message.DestinationRecordJsonSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineContext
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.CheckpointValue
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.util.UUID
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class FlattenQueueAdapterTest {

    class TestQueue : PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>> {
        val broadcasted: MutableList<PipelineEvent<StreamKey, DestinationRecordRaw>> =
            mutableListOf()
        val published: MutableList<PipelineEvent<StreamKey, DestinationRecordRaw>> = mutableListOf()
        override val partitions: Int = 0

        override fun consume(partition: Int): Flow<PipelineEvent<StreamKey, DestinationRecordRaw>> {
            TODO("Not yet implemented")
        }

        override suspend fun publish(
            value: PipelineEvent<StreamKey, DestinationRecordRaw>,
            partition: Int
        ) {
            published.add(value)
        }

        override suspend fun broadcast(value: PipelineEvent<StreamKey, DestinationRecordRaw>) {
            broadcasted.add(value)
        }

        override suspend fun close() {
            TODO("Not yet implemented")
        }
    }

    lateinit var finalQueue: TestQueue
    lateinit var queue: FlattenQueueAdapter<StreamKey>

    @BeforeEach
    fun setup() {
        finalQueue = TestQueue()
        queue = FlattenQueueAdapter(finalQueue)
    }

    @Test
    fun `flattening lists preserve the total count while counting rejected records`() {
        val state = BatchState.COMPLETE
        val records =
            listOf(
                record(1),
                record(2),
                record(3),
            )
        val input = DlqStepOutput(state, records)
        val checkpointId = CheckpointId("checkpoint-id")
        val checkpointValue = CheckpointValue(records = 12, serializedBytes = 123)
        val pipelineContext = PipelineContext(null, null)
        val streamKey = StreamKey(STREAM.mappedDescriptor)

        runBlocking {
            queue.publish(
                PipelineMessage(
                    checkpointCounts = mapOf(checkpointId to checkpointValue),
                    key = streamKey,
                    value = input,
                    postProcessingCallback = null,
                    context = pipelineContext,
                ),
                0
            )
        }

        // We should be calling publish under the hood
        assertTrue(finalQueue.broadcasted.isEmpty())

        val messages = finalQueue.published.mapNotNull { it as? PipelineMessage }

        val actualRecords = messages.map { it.value }
        // Verifying we published all the records
        assertEquals(records, actualRecords)

        // this sums all the counts across the emitted events by checkpointId
        val actualCounts =
            messages
                .flatMap { it.checkpointCounts.entries }
                .groupBy({ it.key }, { it.value })
                .mapValues { it.value.reduce { acc, value -> acc.plus(value) } }

        // Verifying the aggregate counts remain the same
        // However, we're substracting the rejected records from the total records count
        val expectedCheckpointValue =
            CheckpointValue(
                records = 9,
                serializedBytes = 123,
                rejectedRecords = 3,
            )
        assertEquals(mapOf(checkpointId to expectedCheckpointValue), actualCounts)

        // All keys and context should be equal
        messages.forEach {
            assertEquals(streamKey, it.key)
            assertEquals(pipelineContext, it.context)
        }
    }

    companion object {
        val STREAM =
            DestinationStream(
                unmappedNamespace = null,
                unmappedName = "name",
                importType = Append,
                schema = ObjectTypeWithoutSchema,
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 1,
                isFileBased = false,
                includeFiles = false,
                destinationObjectName = null,
                matchingKey = null,
                namespaceMapper = NamespaceMapper(),
                tableSchema =
                    StreamTableSchema(
                        columnSchema =
                            ColumnSchema(
                                inputSchema = mapOf(),
                                inputToFinalColumnNames = mapOf(),
                                finalSchema = mapOf(),
                            ),
                        importType = Append,
                        tableNames = TableNames(finalTableName = TableName("namespace", "test")),
                    ),
            )
    }

    private fun record(id: Int): DestinationRecordRaw =
        DestinationRecordRaw(
            stream = STREAM,
            rawData =
                DestinationRecordJsonSource(
                    AirbyteMessage()
                        .withType(AirbyteMessage.Type.RECORD)
                        .withRecord(
                            AirbyteRecordMessage().withData(Jsons.deserialize("""{"id":"$id"}"""))
                        )
                ),
            serializedSizeBytes = 1,
            checkpointId = null,
            airbyteRawId = UUID.randomUUID(),
        )
}
