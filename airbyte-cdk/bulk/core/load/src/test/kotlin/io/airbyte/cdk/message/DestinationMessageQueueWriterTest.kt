/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.message

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.command.DestinationConfiguration
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.command.MockDestinationCatalogFactory.Companion.stream1
import io.airbyte.cdk.command.MockDestinationCatalogFactory.Companion.stream2
import io.airbyte.cdk.data.NullValue
import io.airbyte.cdk.state.Reserved
import io.airbyte.cdk.state.SyncManager
import io.airbyte.cdk.util.takeUntilInclusive
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import kotlinx.coroutines.flow.take
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(
    rebuildContext = true,
    environments =
        [
            "DestinationMessageQueueWriterTest",
            "MockDestinationConfiguration",
            "MockDestinationCatalog",
        ]
)
class DestinationMessageQueueWriterTest {
    @Inject lateinit var config: DestinationConfiguration
    @Inject lateinit var writer: DestinationMessageQueueWriter
    @Inject
    lateinit var recordQueueSupplier:
        MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationRecordWrapped>>
    @Inject lateinit var checkpointQueue: MessageQueue<Reserved<CheckpointMessageWrapped>>
    @Inject lateinit var syncManager: SyncManager

    private fun makeRecord(stream: DestinationStream, record: String): DestinationRecord {
        return DestinationRecord(
            stream = stream.descriptor,
            data = NullValue,
            emittedAtMs = 0,
            meta = null,
            serialized = record
        )
    }

    private fun makeStreamComplete(stream: DestinationStream): DestinationStreamComplete {
        return DestinationStreamComplete(stream = stream.descriptor, emittedAtMs = 0)
    }

    private fun makeStreamState(stream: DestinationStream, recordCount: Long): CheckpointMessage {
        return StreamCheckpoint(
            checkpoint =
                CheckpointMessage.Checkpoint(
                    stream.descriptor,
                    JsonNodeFactory.instance.objectNode()
                ),
            sourceStats = CheckpointMessage.Stats(recordCount),
            additionalProperties = emptyMap()
        )
    }

    private fun makeGlobalState(recordCount: Long): CheckpointMessage {
        return GlobalCheckpoint(
            state = JsonNodeFactory.instance.objectNode(),
            sourceStats = CheckpointMessage.Stats(recordCount),
            checkpoints = emptyList()
        )
    }

    private fun Sized.bytesReserved(): Long {
        return (sizeBytes * config.estimatedRecordMemoryOverheadRatio).toLong()
    }

    @Test
    fun testSendRecords() = runTest {
        val queue1 = recordQueueSupplier.get(stream1.descriptor)
        val queue2 = recordQueueSupplier.get(stream2.descriptor)

        val manager1 = syncManager.getStreamManager(stream1.descriptor)
        val manager2 = syncManager.getStreamManager(stream2.descriptor)

        (0 until 10).forEach { writer.publish(makeRecord(stream1, "test${it}"), it * 2L) }

        val messages1 =
            queue1
                .consume()
                .takeUntilInclusive {
                    (it.value as StreamRecordWrapped).record.serialized == "test9"
                }
                .toList()

        Assertions.assertEquals(10, messages1.size)
        val expectedRecords =
            (0 until 10).map {
                StreamRecordWrapped(it.toLong(), it * 2L, makeRecord(stream1, "test${it}"))
            }

        Assertions.assertEquals(expectedRecords, messages1.map { it.value })
        Assertions.assertEquals(
            expectedRecords.map { it.bytesReserved() },
            messages1.map { it.bytesReserved }
        )
        Assertions.assertEquals(10L, manager1.recordCount())
        queue1.close()
        Assertions.assertEquals(emptyList<DestinationRecordWrapped>(), queue1.consume().toList())

        queue2.close()
        Assertions.assertEquals(emptyList<DestinationRecordWrapped>(), queue2.consume().toList())
        Assertions.assertEquals(0L, manager2.recordCount())
    }

    @Test
    fun testSendEndOfStream() = runTest {
        val queue1 = recordQueueSupplier.get(stream1.descriptor)
        val queue2 = recordQueueSupplier.get(stream2.descriptor)

        val manager1 = syncManager.getStreamManager(stream1.descriptor)
        val manager2 = syncManager.getStreamManager(stream2.descriptor)

        (0 until 10).forEach { _ -> writer.publish(makeRecord(stream1, "whatever"), 0L) }

        writer.publish(makeRecord(stream2, "test"), 1L)
        writer.publish(makeStreamComplete(stream1), 0L)
        queue2.close()
        Assertions.assertEquals(
            listOf(StreamRecordWrapped(0, 1L, makeRecord(stream2, "test"))),
            queue2.consume().toList().map { it.value }
        )
        Assertions.assertEquals(1L, manager2.recordCount())

        Assertions.assertEquals(manager2.endOfStreamRead(), false)
        Assertions.assertEquals(manager1.endOfStreamRead(), true)

        queue1.close()
        val messages1 = queue1.consume().toList()
        Assertions.assertEquals(11, messages1.size)
        Assertions.assertEquals(messages1[10].value, StreamCompleteWrapped(10))
    }

    @Test
    fun testSendStreamState() = runTest {
        data class TestEvent(
            val stream: DestinationStream,
            val count: Int,
            val expectedStateIndex: Long
        )

        val batches =
            listOf(
                TestEvent(stream1, 10, 10),
                TestEvent(stream1, 5, 15),
                TestEvent(stream2, 4, 4),
                TestEvent(stream1, 3, 18),
            )

        batches.forEach { (stream, count, expectedCount) ->
            repeat(count) { writer.publish(makeRecord(stream, "test"), 1L) }
            writer.publish(makeStreamState(stream, count.toLong()), 0L)
            val state =
                checkpointQueue.consume().take(1).toList().first().value as StreamCheckpointWrapped
            Assertions.assertEquals(expectedCount, state.index)
            Assertions.assertEquals(count.toLong(), state.checkpoint.destinationStats?.recordCount)
        }
    }

    @Test
    fun testSendGlobalState() = runTest {
        open class TestEvent
        data class AddRecords(val stream: DestinationStream, val count: Int) : TestEvent()
        data class SendState(
            val expectedStream1Count: Long,
            val expectedStream2Count: Long,
            val expectedStats: Long = 0
        ) : TestEvent()

        val batches =
            listOf(
                AddRecords(stream1, 10),
                SendState(10, 0, 10),
                AddRecords(stream2, 5),
                AddRecords(stream1, 4),
                SendState(14, 5, 9),
                AddRecords(stream2, 3),
                SendState(14, 8, 3),
                SendState(14, 8, 0),
            )

        batches.forEach { event ->
            when (event) {
                is AddRecords -> {
                    repeat(event.count) { writer.publish(makeRecord(event.stream, "test"), 1L) }
                }
                is SendState -> {
                    writer.publish(makeGlobalState(event.expectedStream1Count), 0L)
                    val state =
                        checkpointQueue.consume().take(1).toList().first().value
                            as GlobalCheckpointWrapped
                    val stream1State = state.streamIndexes.find { it.first == stream1.descriptor }!!
                    val stream2State = state.streamIndexes.find { it.first == stream2.descriptor }!!
                    Assertions.assertEquals(event.expectedStream1Count, stream1State.second)
                    Assertions.assertEquals(event.expectedStream2Count, stream2State.second)
                    Assertions.assertEquals(
                        event.expectedStats,
                        state.checkpoint.destinationStats?.recordCount
                    )
                }
            }
        }
    }
}
