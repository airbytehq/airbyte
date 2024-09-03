/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.message

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.command.MockCatalogFactory.Companion.stream1
import io.airbyte.cdk.command.MockCatalogFactory.Companion.stream2
import io.airbyte.cdk.state.StateManager
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
        val stateManager: MockStateManager
    ) {
        fun make(): DestinationMessageQueueWriter {
            return DestinationMessageQueueWriter(
                catalog,
                messageQueue,
                streamsManager,
                stateManager
            )
        }
    }

    @Prototype
    class MockStateManager : StateManager<DestinationStream, DestinationStateMessage> {
        val streamStates =
            mutableMapOf<DestinationStream, MutableList<Pair<Long, DestinationStateMessage>>>()
        val globalStates =
            mutableListOf<Pair<List<Pair<DestinationStream, Long>>, DestinationStateMessage>>()

        override fun addStreamState(
            key: DestinationStream,
            index: Long,
            stateMessage: DestinationStateMessage
        ) {
            streamStates.getOrPut(key) { mutableListOf() }.add(index to stateMessage)
        }

        override fun addGlobalState(
            keyIndexes: List<Pair<DestinationStream, Long>>,
            stateMessage: DestinationStateMessage
        ) {
            globalStates.add(keyIndexes to stateMessage)
        }

        override fun flushStates() {
            TODO("Not yet implemented")
        }
    }

    private fun makeRecord(stream: DestinationStream, record: String): DestinationRecord {
        return DestinationRecord(stream = stream, data = null, emittedAtMs = 0, serialized = record)
    }

    private fun makeStreamComplete(stream: DestinationStream): DestinationStreamComplete {
        return DestinationStreamComplete(stream = stream, emittedAtMs = 0)
    }

    private fun makeStreamState(
        stream: DestinationStream,
        recordCount: Long
    ): DestinationStateMessage {
        return DestinationStreamState(
            streamState =
                DestinationStateMessage.StreamState(stream, JsonNodeFactory.instance.objectNode()),
            sourceStats = DestinationStateMessage.Stats(recordCount)
        )
    }

    private fun makeGlobalState(recordCount: Long): DestinationStateMessage {
        return DestinationGlobalState(
            state = JsonNodeFactory.instance.objectNode(),
            sourceStats = DestinationStateMessage.Stats(recordCount),
            streamStates = emptyList()
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
        val messages1 = channel1.getMessages()
        Assertions.assertEquals(10, messages1.size)
        val expectedRecords =
            (0 until 10).map {
                StreamRecordWrapped(it.toLong(), it * 2L, makeRecord(stream1, "test${it}"))
            }

        Assertions.assertEquals(expectedRecords, messages1)
        Assertions.assertEquals(10, manager1.countedRecords)

        val messages2 = channel2.getMessages()
        Assertions.assertEquals(emptyList<DestinationRecordWrapped>(), messages2)
        Assertions.assertEquals(0, manager2.countedRecords)

        writer.publish(makeRecord(stream2, "test"), 1L)
        writer.publish(makeStreamComplete(stream1), 0L)
        Assertions.assertEquals(
            listOf(StreamRecordWrapped(0, 1L, makeRecord(stream2, "test"))),
            channel2.getMessages()
        )
        Assertions.assertEquals(1, manager2.countedRecords)

        val nextMessages1 = channel1.getMessages()
        Assertions.assertFalse(manager2.countedEndOfStream)
        Assertions.assertTrue(manager1.countedEndOfStream)
        Assertions.assertEquals(1, nextMessages1.size)
        Assertions.assertEquals(nextMessages1.first(), StreamCompleteWrapped(10))
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
            val state = queueWriterFactory.stateManager.streamStates[stream]!![stateLookupIndex]
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
                    val state = queueWriterFactory.stateManager.globalStates[event.stateLookupIndex]
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
