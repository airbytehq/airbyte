/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.airbyte.cdk.load.message.CheckpointMessageWrapped
import io.airbyte.cdk.load.message.DestinationMessage
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.GlobalCheckpointWrapped
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.StreamCheckpointWrapped
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.CheckpointIndex
import io.airbyte.cdk.load.state.CheckpointKey
import io.airbyte.cdk.load.state.PipelineEventBookkeepingRouter
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.StreamManager
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.test.util.StubDestinationMessageFactory
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.coVerifySequence
import io.mockk.impl.annotations.MockK
import io.mockk.mockk
import java.util.concurrent.ConcurrentLinkedQueue
import kotlinx.coroutines.flow.FlowCollector
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class InputConsumerTaskTest {
    companion object {
        val STREAM1 = DestinationStream.Descriptor("test", "stream1")
        val STREAM2 = DestinationStream.Descriptor("test", "stream2")
    }

    @MockK(relaxed = true)
    lateinit var checkpointQueue: MessageQueue<Reserved<CheckpointMessageWrapped>>
    @MockK(relaxed = true) lateinit var syncManager: SyncManager
    @MockK(relaxed = true) lateinit var memoryManager: ReservationManager
    @MockK(relaxed = true) lateinit var inputFlow: ReservingDeserializingInputFlow
    @MockK(relaxed = true) lateinit var catalog: DestinationCatalog
    @MockK(relaxed = true) lateinit var stream1: DestinationStream
    @MockK(relaxed = true) lateinit var stream2: DestinationStream
    @MockK(relaxed = true)
    lateinit var pipelineInputQueue:
        PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>
    @MockK(relaxed = true)
    lateinit var pipelineEventBookkeepingRouter: PipelineEventBookkeepingRouter

    @BeforeEach
    fun setup() {
        coEvery { stream1.descriptor } returns STREAM1
        coEvery { stream2.descriptor } returns STREAM2

        coEvery { catalog.streams } returns listOf(stream1, stream2)

        coEvery { syncManager.getStreamManager(STREAM1) } returns StreamManager(stream1)
        coEvery { syncManager.getStreamManager(STREAM2) } returns StreamManager(stream2)
    }

    private fun DestinationMessage.wrap(bytesReserved: Long) =
        bytesReserved to Reserved(memoryManager, bytesReserved, this)

    @Test
    fun testSendRecords() = runTest {
        coEvery { inputFlow.collect(any()) } coAnswers
            {
                val collector = firstArg<FlowCollector<Pair<Long, Reserved<DestinationMessage>>>>()
                collector.emit(
                    StubDestinationMessageFactory.makeRecord(
                            MockDestinationCatalogFactory.stream1,
                        )
                        .wrap(1L)
                )
                repeat(2) {
                    collector.emit(
                        StubDestinationMessageFactory.makeRecord(
                                MockDestinationCatalogFactory.stream2,
                            )
                            .wrap(it + 2L)
                    )
                }
            }

        val bookkeeper =
            PipelineEventBookkeepingRouter(
                catalog = catalog,
                syncManager = syncManager,
                checkpointQueue = checkpointQueue,
                openStreamQueue = mockk(relaxed = true),
                fileTransferQueue = mockk(relaxed = true),
                batchStateUpdateQueue = mockk(relaxed = true),
                1,
                false
            )
        val task =
            InputConsumerTask(
                catalog = catalog,
                inputFlow = inputFlow,
                pipelineInputQueue = pipelineInputQueue,
                partitioner = mockk(relaxed = true),
                pipelineEventBookkeepingRouter = bookkeeper,
            )
        task.execute()

        coVerify(exactly = 3) { pipelineInputQueue.publish(any(), any()) }
        assert(syncManager.getStreamManager(stream1.descriptor).readCount() == 1L)
        assert(syncManager.getStreamManager(stream2.descriptor).readCount() == 2L)
    }

    @Test
    fun testSendEndOfStream() = runTest {
        coEvery { inputFlow.collect(any()) } coAnswers
            {
                val collector = firstArg<FlowCollector<Pair<Long, Reserved<DestinationMessage>>>>()
                collector.emit(
                    StubDestinationMessageFactory.makeRecord(
                            MockDestinationCatalogFactory.stream1,
                        )
                        .wrap(1L)
                )
                collector.emit(
                    StubDestinationMessageFactory.makeStreamComplete(
                            MockDestinationCatalogFactory.stream1,
                        )
                        .wrap(2L)
                )
                collector.emit(
                    StubDestinationMessageFactory.makeStreamComplete(
                            MockDestinationCatalogFactory.stream2,
                        )
                        .wrap(3L)
                )
            }

        val bookkeeper =
            PipelineEventBookkeepingRouter(
                catalog = catalog,
                syncManager = syncManager,
                checkpointQueue = checkpointQueue,
                openStreamQueue = mockk(relaxed = true),
                fileTransferQueue = mockk(relaxed = true),
                batchStateUpdateQueue = mockk(relaxed = true),
                1,
                false
            )
        val task =
            InputConsumerTask(
                catalog = catalog,
                inputFlow = inputFlow,
                pipelineInputQueue = mockk(relaxed = true),
                partitioner = mockk(relaxed = true),
                pipelineEventBookkeepingRouter = bookkeeper,
            )
        task.execute()
        coVerifySequence {
            memoryManager.release(2L)
            memoryManager.release(3L)
        }

        assert(syncManager.getStreamManager(stream1.descriptor).readCount() == 1L)
        assert(syncManager.getStreamManager(stream1.descriptor).endOfStreamRead())
        assert(syncManager.getStreamManager(stream2.descriptor).readCount() == 0L)
        assert(syncManager.getStreamManager(stream2.descriptor).endOfStreamRead())
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
            InputConsumerTask(
                catalog = catalog,
                inputFlow = inputFlow,
                pipelineInputQueue = mockk(relaxed = true),
                partitioner = mockk(relaxed = true),
                pipelineEventBookkeepingRouter = pipelineEventBookkeepingRouter,
            )
        coEvery { inputFlow.collect(any()) } coAnswers
            {
                val collector = firstArg<FlowCollector<Pair<Long, Reserved<DestinationMessage>>>>()
                batches.forEach { (stream, count, _) ->
                    repeat(count) {
                        collector.emit(StubDestinationMessageFactory.makeRecord(stream).wrap(1L))
                    }
                    collector.emit(
                        StubDestinationMessageFactory.makeStreamState(stream, count.toLong())
                            .wrap(0L)
                    )
                }
            }
        task.execute()

        val published = ConcurrentLinkedQueue<Reserved<StreamCheckpointWrapped>>()
        coEvery { checkpointQueue.publish(any()) } coAnswers { published.add(firstArg()) }
        published.toList().zip(batches).forEach { (checkpoint, event) ->
            val wrapped = checkpoint.value
            Assertions.assertEquals(event.expectedStateIndex, wrapped.checkpointKey.checkpointIndex)
            Assertions.assertEquals(event.stream.descriptor, wrapped.stream)
        }
    }

    @Test
    fun testSendGlobalState() = runTest {
        open class TestEvent
        data class AddRecords(val stream: DestinationStream, val count: Int) : TestEvent()
        data class SendState(val expectedCheckpointIndex: Int, val expectedStats: Long = 0) :
            TestEvent()

        val batches =
            listOf(
                AddRecords(MockDestinationCatalogFactory.stream1, 10),
                SendState(0, 10),
                AddRecords(MockDestinationCatalogFactory.stream2, 5),
                AddRecords(MockDestinationCatalogFactory.stream1, 4),
                SendState(1, 9),
                AddRecords(MockDestinationCatalogFactory.stream2, 3),
                SendState(2, 3),
                SendState(3, 0),
            )

        val task =
            InputConsumerTask(
                catalog = catalog,
                inputFlow = inputFlow,
                pipelineInputQueue = mockk(relaxed = true),
                partitioner = mockk(relaxed = true),
                pipelineEventBookkeepingRouter = pipelineEventBookkeepingRouter,
            )

        coEvery { inputFlow.collect(any()) } coAnswers
            {
                val collector = firstArg<FlowCollector<Pair<Long, Reserved<DestinationMessage>>>>()
                batches.forEach { event ->
                    when (event) {
                        is AddRecords -> {
                            repeat(event.count) {
                                collector.emit(
                                    StubDestinationMessageFactory.makeRecord(event.stream).wrap(1L)
                                )
                            }
                        }
                        is SendState -> {
                            collector.emit(
                                StubDestinationMessageFactory.makeGlobalState(event.expectedStats)
                                    .wrap(0L)
                            )
                        }
                    }
                }
            }
        val checkpoints = ConcurrentLinkedQueue<Reserved<GlobalCheckpointWrapped>>()
        coEvery { checkpointQueue.publish(any()) } coAnswers { checkpoints.add(firstArg()) }

        task.execute()

        checkpoints.toList().zip(batches.filterIsInstance<SendState>()).forEach {
            (checkpoint, event) ->
            val wrapped = checkpoint.value
            val expectedKey =
                CheckpointKey(
                    checkpointIndex = CheckpointIndex(event.expectedCheckpointIndex),
                    checkpointId = CheckpointId(event.expectedCheckpointIndex.toString())
                )
            Assertions.assertEquals(expectedKey, wrapped.checkpointKey)
            Assertions.assertEquals(
                event.expectedStats,
                wrapped.checkpoint.destinationStats?.recordCount
            )
        }
    }
}
