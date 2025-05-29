/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.message

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.command.MockCatalogFactory.Companion.stream1
import io.airbyte.cdk.command.MockCatalogFactory.Companion.stream2
import io.airbyte.cdk.data.NullValue
import io.airbyte.cdk.state.CheckpointManager
import io.micronaut.context.annotation.Prototype
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Named
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["MockStreamsManager"])
class DestinationMessageQueueWriterTest {
    @Inject lateinit var queueWriterFactory: TestDestinationMessageQueueWriterFactory

    @Prototype
    class TestDestinationMessageQueueWriterFactory(
        @Named("mockCatalog") private val catalog: DestinationCatalog,
        val messageQueue: MockMessageQueue,
        val streamsManager: MockStreamsManager,
        val checkpointManager: MockCheckpointManager
    ) {
        fun make(): DestinationMessageQueueWriter {
            return DestinationMessageQueueWriter(
                catalog,
                messageQueue,
                streamsManager,
                checkpointManager
            )
        }
    }

    class MockQueueChannel : QueueChannel<DestinationRecordWrapped> {
        val messages = mutableListOf<DestinationRecordWrapped>()
        var closed = false

        override suspend fun close() {
            closed = true
        }

        override suspend fun isClosed(): Boolean {
            return closed
        }

        override suspend fun send(message: DestinationRecordWrapped) {
            messages.add(message)
        }

        override suspend fun receive(): DestinationRecordWrapped {
            return messages.removeAt(0)
        }
    }

    @Prototype
    class MockMessageQueue : MessageQueue<DestinationStream, DestinationRecordWrapped> {
        private val channels =
            mutableMapOf<DestinationStream, QueueChannel<DestinationRecordWrapped>>()

        override suspend fun getChannel(
            key: DestinationStream
        ): QueueChannel<DestinationRecordWrapped> {
            return channels.getOrPut(key) { MockQueueChannel() }
        }

        override suspend fun acquireQueueBytesBlocking(bytes: Long) {
            TODO("Not yet implemented")
        }

        override suspend fun releaseQueueBytes(bytes: Long) {
            TODO("Not yet implemented")
        }
    }

    @Prototype
    class MockCheckpointManager : CheckpointManager<DestinationStream, CheckpointMessage> {
        val streamStates =
            mutableMapOf<DestinationStream, MutableList<Pair<Long, CheckpointMessage>>>()
        val globalStates =
            mutableListOf<Pair<List<Pair<DestinationStream, Long>>, CheckpointMessage>>()

        override fun addStreamCheckpoint(
            key: DestinationStream,
            index: Long,
            checkpointMessage: CheckpointMessage
        ) {
            streamStates.getOrPut(key) { mutableListOf() }.add(index to checkpointMessage)
        }

        override fun addGlobalCheckpoint(
            keyIndexes: List<Pair<DestinationStream, Long>>,
            checkpointMessage: CheckpointMessage
        ) {
            globalStates.add(keyIndexes to checkpointMessage)
        }

        override suspend fun flushReadyCheckpointMessages() {
            TODO("Not yet implemented")
        }
    }

    private fun makeRecord(stream: DestinationStream, record: String): DestinationRecord {
        return DestinationRecord(
            stream = stream,
            data = NullValue,
            emittedAtMs = 0,
            meta = null,
            serialized = record
        )
    }

    private fun makeStreamComplete(stream: DestinationStream): DestinationStreamComplete {
        return DestinationStreamComplete(stream = stream, emittedAtMs = 0)
    }

    private fun makeStreamState(stream: DestinationStream, recordCount: Long): CheckpointMessage {
        return StreamCheckpoint(
            checkpoint =
                CheckpointMessage.Checkpoint(stream, JsonNodeFactory.instance.objectNode()),
            sourceStats = CheckpointMessage.Stats(recordCount)
        )
    }

    private fun makeGlobalState(recordCount: Long): CheckpointMessage {
        return GlobalCheckpoint(
            state = JsonNodeFactory.instance.objectNode(),
            sourceStats = CheckpointMessage.Stats(recordCount),
            checkpoints = emptyList()
        )
    }

    @Test
    fun testSendRecords() = runTest {
        val writer = queueWriterFactory.make()

        val channel1 = queueWriterFactory.messageQueue.getChannel(stream1) as MockQueueChannel
        val channel2 = queueWriterFactory.messageQueue.getChannel(stream2) as MockQueueChannel

        val manager1 = queueWriterFactory.streamsManager.getManager(stream1) as MockStreamManager
        val manager2 = queueWriterFactory.streamsManager.getManager(stream2) as MockStreamManager

        (0 until 10).forEach { writer.publish(makeRecord(stream1, "test${it}"), it * 2L) }
        Assertions.assertEquals(10, channel1.messages.size)
        val expectedRecords =
            (0 until 10).map {
                StreamRecordWrapped(it.toLong(), it * 2L, makeRecord(stream1, "test${it}"))
            }

        Assertions.assertEquals(expectedRecords, channel1.messages)
        Assertions.assertEquals(10, manager1.countedRecords)

        Assertions.assertEquals(emptyList<DestinationRecordWrapped>(), channel2.messages)
        Assertions.assertEquals(0, manager2.countedRecords)

        writer.publish(makeRecord(stream2, "test"), 1L)
        writer.publish(makeStreamComplete(stream1), 0L)
        Assertions.assertEquals(
            listOf(StreamRecordWrapped(0, 1L, makeRecord(stream2, "test"))),
            channel2.messages
        )
        Assertions.assertEquals(1, manager2.countedRecords)

        Assertions.assertFalse(manager2.countedEndOfStream)
        Assertions.assertTrue(manager1.countedEndOfStream)
        Assertions.assertEquals(11, channel1.messages.size)
        Assertions.assertEquals(channel1.messages[10], StreamCompleteWrapped(10))
    }

    @Test
    fun testSendStreamState() = runTest {
        val writer = queueWriterFactory.make()

        data class TestEvent(
            val stream: DestinationStream,
            val count: Int,
            val stateLookupIndex: Int,
            val expectedStateIndex: Long
        )

        val batches =
            listOf(
                TestEvent(stream1, 10, 0, 10),
                TestEvent(stream1, 5, 1, 15),
                TestEvent(stream2, 4, 0, 4),
                TestEvent(stream1, 3, 2, 18),
            )

        batches.forEach { (stream, count, stateLookupIndex, expectedCount) ->
            repeat(count) { writer.publish(makeRecord(stream, "test"), 1L) }
            writer.publish(makeStreamState(stream, count.toLong()), 0L)
            val state =
                queueWriterFactory.checkpointManager.streamStates[stream]!![stateLookupIndex]
            Assertions.assertEquals(expectedCount, state.first)
            Assertions.assertEquals(count.toLong(), state.second.destinationStats?.recordCount)
        }
    }

    @Test
    fun testSendGlobalState() = runTest {
        val writer = queueWriterFactory.make()

        open class TestEvent
        data class AddRecords(val stream: DestinationStream, val count: Int) : TestEvent()
        data class SendState(
            val stateLookupIndex: Int,
            val expectedStream1Count: Long,
            val expectedStream2Count: Long,
            val expectedStats: Long = 0
        ) : TestEvent()

        val batches =
            listOf(
                AddRecords(stream1, 10),
                SendState(0, 10, 0, 10),
                AddRecords(stream2, 5),
                AddRecords(stream1, 4),
                SendState(1, 14, 5, 9),
                AddRecords(stream2, 3),
                SendState(2, 14, 8, 3),
                SendState(3, 14, 8, 0),
            )

        batches.forEach { event ->
            when (event) {
                is AddRecords -> {
                    repeat(event.count) { writer.publish(makeRecord(event.stream, "test"), 1L) }
                }
                is SendState -> {
                    writer.publish(makeGlobalState(event.expectedStream1Count), 0L)
                    val state =
                        queueWriterFactory.checkpointManager.globalStates[event.stateLookupIndex]
                    val stream1State = state.first.find { it.first == stream1 }!!
                    val stream2State = state.first.find { it.first == stream2 }!!
                    Assertions.assertEquals(event.expectedStream1Count, stream1State.second)
                    Assertions.assertEquals(event.expectedStream2Count, stream2State.second)
                    Assertions.assertEquals(
                        event.expectedStats,
                        state.second.destinationStats?.recordCount
                    )
                }
            }
        }
    }
}
