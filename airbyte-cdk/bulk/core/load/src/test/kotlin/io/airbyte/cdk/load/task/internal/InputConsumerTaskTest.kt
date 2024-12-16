/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.airbyte.cdk.load.message.CheckpointMessageWrapped
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationStreamEvent
import io.airbyte.cdk.load.message.GlobalCheckpointWrapped
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.MessageQueueSupplier
import io.airbyte.cdk.load.message.StreamCheckpointWrapped
import io.airbyte.cdk.load.message.StreamEndEvent
import io.airbyte.cdk.load.message.StreamRecordEvent
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.test.util.CoroutineTestUtils
import io.airbyte.cdk.load.test.util.StubDestinationMessageFactory
import io.airbyte.cdk.load.util.takeUntilInclusive
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import io.mockk.mockk
import jakarta.inject.Inject
import jakarta.inject.Named
import jakarta.inject.Singleton
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.FlowCollector
import kotlinx.coroutines.flow.take
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(
    rebuildContext = true,
    environments =
        [
            "InputConsumerTaskTest",
            "MockDestinationConfiguration",
            "MockDestinationCatalog",
        ]
)
class InputConsumerTaskTest {
    @Inject lateinit var config: DestinationConfiguration
    @Inject lateinit var taskFactory: InputConsumerTaskFactory
    @Inject
    lateinit var recordQueueSupplier:
        MessageQueueSupplier<DestinationStream.Descriptor, Reserved<DestinationStreamEvent>>
    @Inject lateinit var checkpointQueue: MessageQueue<Reserved<CheckpointMessageWrapped>>
    @Inject lateinit var syncManager: SyncManager
    @Inject lateinit var mockInputFlow: MockInputFlow
    @Inject lateinit var mockCatalogFactory: MockDestinationCatalogFactory

    @Singleton
    @Primary
    @Requires(env = ["InputConsumerTaskTest"])
    class MockInputFlow(@Named("memoryManager") val memoryManager: ReservationManager) :
        SizedInputFlow<Reserved<DestinationMessage>> {
        private val messages = Channel<Pair<Long, Reserved<DestinationMessage>>>(Channel.UNLIMITED)
        val initialMemory = memoryManager.remainingCapacityBytes

        override suspend fun collect(
            collector: FlowCollector<Pair<Long, Reserved<DestinationMessage>>>
        ) {
            for (message in messages) {
                collector.emit(message)
            }
        }

        suspend fun addMessage(message: DestinationMessage, size: Long = 0L) {
            messages.send(Pair(size, memoryManager.reserve(1, message)))
        }

        fun stop() {
            messages.close()
        }
    }

    @Test
    fun testSendRecords() = runTest {
        val queue1 = recordQueueSupplier.get(MockDestinationCatalogFactory.stream1.descriptor)
        val queue2 = recordQueueSupplier.get(MockDestinationCatalogFactory.stream2.descriptor)

        val manager1 =
            syncManager.getStreamManager(MockDestinationCatalogFactory.stream1.descriptor)
        val manager2 =
            syncManager.getStreamManager(MockDestinationCatalogFactory.stream2.descriptor)

        (0 until 10).forEach {
            mockInputFlow.addMessage(
                StubDestinationMessageFactory.makeRecord(
                    MockDestinationCatalogFactory.stream1,
                    "test${it}"
                ),
                it * 2L
            )
        }
        mockInputFlow.addMessage(
            StubDestinationMessageFactory.makeStreamComplete(MockDestinationCatalogFactory.stream1)
        )
        mockInputFlow.addMessage(
            StubDestinationMessageFactory.makeStreamComplete(MockDestinationCatalogFactory.stream2)
        )

        val task =
            taskFactory.make(
                mockCatalogFactory.make(),
                mockInputFlow,
                recordQueueSupplier,
                checkpointQueue,
                mockk(),
            )
        launch { task.execute() }

        val messages1 =
            queue1
                .consume()
                .takeUntilInclusive { (it.value as StreamRecordEvent).record.serialized == "test9" }
                .toList()

        Assertions.assertEquals(10, messages1.size)
        val expectedRecords =
            (0 until 10).map {
                StreamRecordEvent(
                    it.toLong(),
                    it * 2L,
                    StubDestinationMessageFactory.makeRecord(
                        MockDestinationCatalogFactory.stream1,
                        "test${it}"
                    )
                )
            }
        val streamComplete1: Reserved<DestinationStreamEvent> =
            queue1.consume().take(1).toList().first()
        val streamComplete2: Reserved<DestinationStreamEvent> =
            queue2.consume().take(1).toList().first()

        Assertions.assertEquals(expectedRecords, messages1.map { it.value })
        Assertions.assertEquals(expectedRecords.map { _ -> 1L }, messages1.map { it.bytesReserved })
        Assertions.assertEquals(StreamEndEvent(10), streamComplete1.value)
        Assertions.assertEquals(1, streamComplete1.bytesReserved)
        Assertions.assertEquals(10L, manager1.recordCount())
        Assertions.assertEquals(emptyList<DestinationStreamEvent>(), queue1.consume().toList())
        Assertions.assertEquals(StreamEndEvent(0), streamComplete2.value)
        Assertions.assertEquals(emptyList<DestinationStreamEvent>(), queue2.consume().toList())
        Assertions.assertEquals(0L, manager2.recordCount())
        mockInputFlow.stop()
    }

    @Test
    fun testSendEndOfStream() = runTest {
        val queue1 = recordQueueSupplier.get(MockDestinationCatalogFactory.stream1.descriptor)
        val queue2 = recordQueueSupplier.get(MockDestinationCatalogFactory.stream2.descriptor)

        val manager1 =
            syncManager.getStreamManager(MockDestinationCatalogFactory.stream1.descriptor)
        val manager2 =
            syncManager.getStreamManager(MockDestinationCatalogFactory.stream2.descriptor)

        (0 until 10).forEach { _ ->
            mockInputFlow.addMessage(
                StubDestinationMessageFactory.makeRecord(
                    MockDestinationCatalogFactory.stream1,
                    "whatever"
                ),
                0L
            )
        }

        mockInputFlow.addMessage(
            StubDestinationMessageFactory.makeRecord(MockDestinationCatalogFactory.stream2, "test"),
            1L
        )
        mockInputFlow.addMessage(
            StubDestinationMessageFactory.makeStreamComplete(MockDestinationCatalogFactory.stream1),
            0L
        )
        mockInputFlow.addMessage(
            StubDestinationMessageFactory.makeStreamComplete(MockDestinationCatalogFactory.stream2),
            0L
        )
        val task =
            taskFactory.make(
                mockCatalogFactory.make(),
                mockInputFlow,
                recordQueueSupplier,
                checkpointQueue,
                mockk(),
            )
        val job = launch { task.execute() }
        mockInputFlow.stop()
        job.join()
        queue2.close()
        Assertions.assertEquals(
            listOf(
                StreamRecordEvent(
                    0,
                    1L,
                    StubDestinationMessageFactory.makeRecord(
                        MockDestinationCatalogFactory.stream2,
                        "test"
                    )
                ),
                StreamEndEvent(1)
            ),
            queue2.consume().toList().map { it.value }
        )
        Assertions.assertEquals(1L, manager2.recordCount())

        Assertions.assertEquals(manager2.endOfStreamRead(), true)
        Assertions.assertEquals(manager1.endOfStreamRead(), true)

        queue1.close()
        val messages1 = queue1.consume().toList()
        Assertions.assertEquals(11, messages1.size)
        Assertions.assertEquals(messages1[10].value, StreamEndEvent(10))
        Assertions.assertEquals(
            mockInputFlow.initialMemory - 11,
            mockInputFlow.memoryManager.remainingCapacityBytes,
            "1 byte per message should have been reserved, but the end-of-stream should have been released"
        )
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
                TestEvent(MockDestinationCatalogFactory.stream1, 10, 10),
                TestEvent(MockDestinationCatalogFactory.stream1, 5, 15),
                TestEvent(MockDestinationCatalogFactory.stream2, 4, 4),
                TestEvent(MockDestinationCatalogFactory.stream1, 3, 18),
            )

        val task =
            taskFactory.make(
                mockCatalogFactory.make(),
                mockInputFlow,
                recordQueueSupplier,
                checkpointQueue,
                mockk(),
            )
        launch { task.execute() }
        batches.forEach { (stream, count, expectedCount) ->
            repeat(count) {
                mockInputFlow.addMessage(
                    StubDestinationMessageFactory.makeRecord(stream, "test"),
                    1L
                )
            }
            mockInputFlow.addMessage(
                StubDestinationMessageFactory.makeStreamState(stream, count.toLong()),
                0L
            )
            val state =
                checkpointQueue.consume().take(1).toList().first().value as StreamCheckpointWrapped
            Assertions.assertEquals(expectedCount, state.index)
            Assertions.assertEquals(count.toLong(), state.checkpoint.destinationStats?.recordCount)
        }
        mockInputFlow.addMessage(
            StubDestinationMessageFactory.makeStreamComplete(MockDestinationCatalogFactory.stream1)
        )
        mockInputFlow.addMessage(
            StubDestinationMessageFactory.makeStreamComplete(MockDestinationCatalogFactory.stream2)
        )
        mockInputFlow.stop()
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
                AddRecords(MockDestinationCatalogFactory.stream1, 10),
                SendState(10, 0, 10),
                AddRecords(MockDestinationCatalogFactory.stream2, 5),
                AddRecords(MockDestinationCatalogFactory.stream1, 4),
                SendState(14, 5, 9),
                AddRecords(MockDestinationCatalogFactory.stream2, 3),
                SendState(14, 8, 3),
                SendState(14, 8, 0),
            )

        val task =
            taskFactory.make(
                mockCatalogFactory.make(),
                mockInputFlow,
                recordQueueSupplier,
                checkpointQueue,
                mockk(),
            )
        launch { task.execute() }
        batches.forEach { event ->
            when (event) {
                is AddRecords -> {
                    repeat(event.count) {
                        mockInputFlow.addMessage(
                            StubDestinationMessageFactory.makeRecord(event.stream, "test"),
                            1L
                        )
                    }
                }
                is SendState -> {
                    mockInputFlow.addMessage(
                        StubDestinationMessageFactory.makeGlobalState(event.expectedStream1Count),
                        0L
                    )
                    val state =
                        checkpointQueue.consume().take(1).toList().first().value
                            as GlobalCheckpointWrapped
                    val stream1State =
                        state.streamIndexes.find {
                            it.first == MockDestinationCatalogFactory.stream1.descriptor
                        }!!
                    val stream2State =
                        state.streamIndexes.find {
                            it.first == MockDestinationCatalogFactory.stream2.descriptor
                        }!!
                    Assertions.assertEquals(event.expectedStream1Count, stream1State.second)
                    Assertions.assertEquals(event.expectedStream2Count, stream2State.second)
                    Assertions.assertEquals(
                        event.expectedStats,
                        state.checkpoint.destinationStats?.recordCount
                    )
                }
            }
        }
        mockInputFlow.addMessage(
            StubDestinationMessageFactory.makeStreamComplete(MockDestinationCatalogFactory.stream1)
        )
        mockInputFlow.addMessage(
            StubDestinationMessageFactory.makeStreamComplete(MockDestinationCatalogFactory.stream2)
        )
        mockInputFlow.stop()
    }

    @Test
    fun testFileStreamIncompleteThrows() = runTest {
        mockInputFlow.addMessage(
            StubDestinationMessageFactory.makeFile(MockDestinationCatalogFactory.stream1, "test"),
            1L
        )
        mockInputFlow.addMessage(
            StubDestinationMessageFactory.makeFileStreamIncomplete(
                MockDestinationCatalogFactory.stream1
            ),
            0L
        )
        val task =
            taskFactory.make(
                mockCatalogFactory.make(),
                mockInputFlow,
                recordQueueSupplier,
                checkpointQueue,
                mockk(relaxed = true),
            )
        CoroutineTestUtils.assertThrows(IllegalStateException::class) { task.execute() }
        mockInputFlow.stop()
    }
}
