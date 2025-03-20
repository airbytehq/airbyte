/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.WithBatchState
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.BatchAccumulator
import io.airbyte.cdk.load.pipeline.BatchStateUpdate
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.pipeline.FinalOutput
import io.airbyte.cdk.load.pipeline.NoOutput
import io.airbyte.cdk.load.pipeline.OutputPartitioner
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.util.setOnce
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.impl.annotations.MockK
import io.mockk.mockk
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.FlowCollector
import kotlinx.coroutines.joinAll
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class LoadPipelineStepTaskUTest {
    @MockK
    lateinit var batchAccumulatorNoUpdate:
        BatchAccumulator<AutoCloseable, StreamKey, String, Boolean>
    @MockK
    lateinit var batchAccumulatorWithUpdate:
        BatchAccumulator<AutoCloseable, StreamKey, String, MyBatch>
    @MockK lateinit var inputFlow: Flow<PipelineEvent<StreamKey, String>>
    @MockK lateinit var batchUpdateQueue: QueueWriter<BatchUpdate>

    data class Closeable(val id: Int = 0) : AutoCloseable {
        override fun close() {}
    }

    data class MyBatch(override val state: Batch.State) : WithBatchState

    @BeforeEach
    fun setup() {
        coEvery { batchAccumulatorNoUpdate.finish(any()) } returns FinalOutput(true)
    }

    private fun <T : Any> createTask(
        part: Int,
        batchAccumulator: BatchAccumulator<AutoCloseable, StreamKey, String, T>,
    ): LoadPipelineStepTask<AutoCloseable, StreamKey, String, StreamKey, T> =
        LoadPipelineStepTask(
            batchAccumulator,
            inputFlow,
            batchUpdateQueue,
            // TODO: test output partitioner, queue, and flush strategy when actually used
            null,
            null,
            null,
            part,
            part,
            1,
            ConcurrentHashMap()
        )

    private fun messageEvent(
        key: StreamKey,
        value: String,
        counts: Map<Int, Long> = emptyMap()
    ): PipelineEvent<StreamKey, String> =
        PipelineMessage(counts.mapKeys { CheckpointId(it.key) }, key, value)
    private fun endOfStreamEvent(key: StreamKey): PipelineEvent<StreamKey, String> =
        PipelineEndOfStream(key.stream)

    @Test
    fun `start only called on first message if state returned by accept is null`() = runTest {
        val key = StreamKey(DestinationStream.Descriptor("namespace", "stream"))
        val part = 7
        val task = createTask(part, batchAccumulatorNoUpdate)

        // No call to accept will finish the batch, but state will be threaded through.
        val state1 = Closeable(1)
        val state2 = Closeable(2)
        coEvery { batchAccumulatorNoUpdate.start(any(), any()) } returns state1
        coEvery { batchAccumulatorNoUpdate.accept("value_0", state1) } returns NoOutput(state2)
        coEvery { batchAccumulatorNoUpdate.accept("value_1", state2) } returns NoOutput(Closeable())

        coEvery { inputFlow.collect(any()) } coAnswers
            {
                val collector = firstArg<FlowCollector<PipelineEvent<StreamKey, String>>>()
                repeat(2) { collector.emit(messageEvent(key, "value_$it")) }
            }

        task.execute()

        coVerify(exactly = 1) { batchAccumulatorNoUpdate.start(key, part) }
        repeat(2) { coVerify(exactly = 1) { batchAccumulatorNoUpdate.accept("value_$it", any()) } }
        coVerify(exactly = 0) { batchAccumulatorNoUpdate.finish(any()) }
    }

    @Test
    fun `start called again only after null state returned, even if accept yields output`() =
        runTest {
            val key = StreamKey(DestinationStream.Descriptor("namespace", "stream"))
            val part = 6
            val task = createTask(part, batchAccumulatorNoUpdate)
            val stateA1 = Closeable(1)
            val stateA2 = Closeable(2)
            val stateB1 = Closeable(4)
            val stateB2 = Closeable(5)
            val startHasBeenCalled = AtomicBoolean(false)

            coEvery { batchAccumulatorNoUpdate.start(any(), any()) } answers
                {
                    if (startHasBeenCalled.setOnce()) stateA1 else stateB1
                }
            coEvery { batchAccumulatorNoUpdate.accept("value_0", stateA1) } returns
                NoOutput(stateA2)
            coEvery { batchAccumulatorNoUpdate.accept("value_1", stateA2) } returns
                FinalOutput(true)
            coEvery { batchAccumulatorNoUpdate.accept("value_2", stateB1) } returns
                NoOutput(stateB2)

            coEvery { inputFlow.collect(any()) } coAnswers
                {
                    val collector = firstArg<FlowCollector<PipelineEvent<StreamKey, String>>>()
                    repeat(3) { collector.emit(messageEvent(key, "value_$it")) }
                }

            task.execute()
            coVerify(exactly = 2) { batchAccumulatorNoUpdate.start(key, part) }
            repeat(3) {
                coVerify(exactly = 1) { batchAccumulatorNoUpdate.accept("value_$it", any()) }
            }
        }

    @Test
    fun `finish and update called on end-of-stream iff last accept returned a non-null state`() =
        runTest {
            val key = StreamKey(DestinationStream.Descriptor("namespace", "stream"))
            val part = 5
            val task = createTask(part, batchAccumulatorNoUpdate)

            val stateToClose = mockk<Closeable>()
            coEvery { stateToClose.close() } returns Unit

            coEvery { batchAccumulatorNoUpdate.start(any(), any()) } returns Closeable()
            coEvery { batchAccumulatorNoUpdate.accept(any(), any()) } returns NoOutput(stateToClose)
            coEvery { batchAccumulatorNoUpdate.finish(any()) } returns FinalOutput(true)
            coEvery { batchUpdateQueue.publish(any()) } returns Unit

            coEvery { inputFlow.collect(any()) } coAnswers
                {
                    val collector = firstArg<FlowCollector<PipelineEvent<StreamKey, String>>>()
                    repeat(10) { // arbitrary number of messages
                        collector.emit(messageEvent(key, "value"))
                    }
                    collector.emit(endOfStreamEvent(key))
                }

            task.execute()

            coVerify(exactly = 1) { batchAccumulatorNoUpdate.start(key, part) }
            coVerify(exactly = 10) { batchAccumulatorNoUpdate.accept(any(), any()) }
            coVerify(exactly = 1) { batchAccumulatorNoUpdate.finish(any()) }
            coVerify(exactly = 1) { batchUpdateQueue.publish(any()) }
            coVerify(exactly = 1) { stateToClose.close() }
        }

    @Test
    fun `update but not finish called on end-of-stream when last accept returned null state`() =
        runTest {
            val key = StreamKey(DestinationStream.Descriptor("namespace", "stream"))
            val part = 4
            val task = createTask(part, batchAccumulatorNoUpdate)

            var acceptCalls = 0
            coEvery { batchAccumulatorNoUpdate.start(any(), any()) } returns Closeable()
            coEvery { batchAccumulatorNoUpdate.accept(any(), any()) } answers
                {
                    if (++acceptCalls == 10) FinalOutput(true) else NoOutput(Closeable())
                }
            coEvery { batchAccumulatorNoUpdate.finish(any()) } returns FinalOutput(true)
            coEvery { batchUpdateQueue.publish(any()) } returns Unit

            coEvery { inputFlow.collect(any()) } coAnswers
                {
                    val collector = firstArg<FlowCollector<PipelineEvent<StreamKey, String>>>()
                    repeat(10) { // arbitrary number of messages
                        collector.emit(messageEvent(key, "value"))
                    }
                    collector.emit(endOfStreamEvent(key))
                }

            task.execute()

            coVerify(exactly = 1) { batchAccumulatorNoUpdate.start(key, part) }
            coVerify(exactly = 10) { batchAccumulatorNoUpdate.accept(any(), any()) }
            coVerify(exactly = 0) { batchAccumulatorNoUpdate.finish(any()) }
            coVerify(exactly = 1) { batchUpdateQueue.publish(any()) }
        }

    @Test
    fun `update at end-of-batch when output provides persisted batch state`() = runTest {
        val key = StreamKey(DestinationStream.Descriptor("namespace", "stream"))
        val part = 99
        val task = createTask(part, batchAccumulator = batchAccumulatorWithUpdate)
        var acceptCalls = 0

        coEvery { batchAccumulatorWithUpdate.start(any(), any()) } returns Closeable()
        coEvery { batchAccumulatorWithUpdate.accept(any(), any()) } answers
            {
                when (acceptCalls++ % 4) {
                    0 -> NoOutput(Closeable())
                    1 -> FinalOutput(MyBatch(Batch.State.PROCESSED))
                    2 -> FinalOutput(MyBatch(Batch.State.PERSISTED))
                    3 -> FinalOutput(MyBatch(Batch.State.COMPLETE))
                    else -> error("unreachable")
                }
            }
        coEvery { batchUpdateQueue.publish(any()) } returns Unit
        coEvery { inputFlow.collect(any()) } coAnswers
            {
                val collector = firstArg<FlowCollector<PipelineEvent<StreamKey, String>>>()
                repeat(12) { // arbitrary number of messages
                    collector.emit(messageEvent(key, "value"))
                }
            }

        task.execute()

        coVerify(exactly = 9) {
            batchAccumulatorWithUpdate.start(key, part)
        } // only 1/4 are no output
        coVerify(exactly = 12) { batchAccumulatorWithUpdate.accept(any(), any()) } // all have data
        coVerify(exactly = 0) { batchAccumulatorWithUpdate.finish(any()) } // never end-of-stream
        coVerify(exactly = 6) { batchUpdateQueue.publish(any()) } // half are PERSISTED/COMPLETE
    }

    @Test
    fun `manage state separately by stream`() = runTest {
        val key1 = StreamKey(DestinationStream.Descriptor("namespace", "stream1"))
        val key2 = StreamKey(DestinationStream.Descriptor("namespace", "stream2"))
        val part = 89

        val task = createTask(part, batchAccumulatorWithUpdate)

        // Make stream1 finish with a persisted output coEvery 3 calls (otherwise null)
        // Make stream2 finish with a persisted output coEvery 2 calls (otherwise null)
        val stream1States = (0 until 11).map { Closeable(it) }
        val stream2States = (0 until 11).map { Closeable(it + 100) }
        var stream1StartCalls = 0
        var stream2StartCalls = 0
        coEvery { batchAccumulatorWithUpdate.start(key1, any()) } answers
            {
                // Stream 1 will finish on 0, 3, 6, 9
                // (so the last finish is right before end-of-stream, leaving no input to finish)
                when (stream1StartCalls++) {
                    0 -> stream1States.first()
                    1 -> stream1States[1]
                    2 -> stream1States[4]
                    3 -> stream1States[7]
                    else -> error("unreachable stream1 start call")
                }
            }
        coEvery { batchAccumulatorWithUpdate.start(key2, any()) } answers
            {
                // Stream 2 will finish on 0, 2, 4, 6, 8
                // (so the last finish is one record before end-of-stream, leaving input to finish)
                when (stream2StartCalls++) {
                    0 -> stream2States.first()
                    1 -> stream2States[1]
                    2 -> stream2States[3]
                    3 -> stream2States[5]
                    4 -> stream2States[7]
                    5 -> stream2States[9]
                    else -> error("unreachable stream2 start call")
                }
            }
        repeat(10) {
            coEvery { batchAccumulatorWithUpdate.accept(any(), stream1States[it]) } returns
                if (it % 3 == 0) {
                    FinalOutput(MyBatch(Batch.State.PERSISTED))
                } else {
                    NoOutput(stream1States[it + 1])
                }
            coEvery { batchAccumulatorWithUpdate.accept(any(), stream2States[it]) } returns
                if (it % 2 == 0) {
                    FinalOutput(MyBatch(Batch.State.PERSISTED))
                } else {
                    NoOutput(stream2States[it + 1])
                }
        }

        coEvery { inputFlow.collect(any()) } coAnswers
            {
                val collector = firstArg<FlowCollector<PipelineEvent<StreamKey, String>>>()
                repeat(10) { // arbitrary number of messages
                    collector.emit(messageEvent(key1, "stream1_value"))
                    collector.emit(messageEvent(key2, "stream2_value"))
                    // Include an end-of-stream for each stream, as only the even-numbered
                    // emitter (stream2) will have just finished a batch.
                }
                collector.emit(endOfStreamEvent(key1))
                collector.emit(endOfStreamEvent(key2))
            }

        coEvery { batchAccumulatorWithUpdate.finish(any()) } returns
            FinalOutput(MyBatch(Batch.State.COMPLETE))
        coEvery { batchUpdateQueue.publish(any()) } returns Unit

        task.execute()

        coVerify(exactly = 4) { batchAccumulatorWithUpdate.start(key1, part) }
        coVerify(exactly = 6) { batchAccumulatorWithUpdate.start(key2, part) }
        coVerify(exactly = 10) {
            batchAccumulatorWithUpdate.accept("stream1_value", match { it in stream1States })
        }
        coVerify(exactly = 10) {
            batchAccumulatorWithUpdate.accept("stream2_value", match { it in stream2States })
        }
        coVerify(exactly = 1) { batchAccumulatorWithUpdate.finish(stream2States[10]) }
    }

    @Test
    fun `checkpoint counts are merged`() = runTest {
        val key1 = StreamKey(DestinationStream.Descriptor("namespace", "stream1"))
        val key2 = StreamKey(DestinationStream.Descriptor("namespace", "stream2"))
        val part = 66666

        val task = createTask(part, batchAccumulatorWithUpdate)

        coEvery { batchAccumulatorWithUpdate.start(key1, part) } returns Closeable(1)
        coEvery { batchAccumulatorWithUpdate.start(key2, part) } returns Closeable(2)
        coEvery { batchAccumulatorWithUpdate.accept("stream1_value", any()) } returns
            NoOutput(Closeable(1))
        coEvery { batchAccumulatorWithUpdate.accept("stream2_value", any()) } returns
            NoOutput(Closeable(2))
        coEvery { batchAccumulatorWithUpdate.finish(Closeable(1)) } returns
            FinalOutput(MyBatch(Batch.State.COMPLETE))
        coEvery { batchAccumulatorWithUpdate.finish(Closeable(2)) } returns
            FinalOutput(MyBatch(Batch.State.PERSISTED))

        coEvery { inputFlow.collect(any()) } coAnswers
            {
                val collector = firstArg<FlowCollector<PipelineEvent<StreamKey, String>>>()

                // Emit 10 messages for stream1, 10 messages for stream2
                repeat(12) {
                    collector.emit(
                        messageEvent(key1, "stream1_value", mapOf(it / 6 to it.toLong()))
                    ) // 0 -> 15, 1 -> 51
                    collector.emit(
                        messageEvent(key2, "stream2_value", mapOf((it / 4) + 1 to it.toLong()))
                    ) // 1 -> 6, 2 -> 22, 3 -> 38
                }

                // Emit end-of-stream for stream1, end-of-stream for stream2
                collector.emit(endOfStreamEvent(key1))
                collector.emit(endOfStreamEvent(key2))
            }

        coEvery { batchUpdateQueue.publish(any()) } returns Unit

        task.execute()

        val expectedBatchUpdateStream1 =
            BatchStateUpdate(
                key1.stream,
                mapOf(CheckpointId(0) to 15L, CheckpointId(1) to 51L),
                Batch.State.COMPLETE
            )
        val expectedBatchUpdateStream2 =
            BatchStateUpdate(
                key2.stream,
                mapOf(CheckpointId(1) to 6L, CheckpointId(2) to 22L, CheckpointId(3) to 38L),
                Batch.State.PERSISTED
            )
        coVerify(exactly = 1) { batchUpdateQueue.publish(expectedBatchUpdateStream1) }
        coVerify(exactly = 1) { batchUpdateQueue.publish(expectedBatchUpdateStream2) }
    }

    private fun runEndOfStreamTest(sendBoth: Boolean) = runTest {
        data class TestKey(val output: Boolean, override val stream: DestinationStream.Descriptor) :
            WithStream
        val outputQueue = mockk<PartitionedQueue<PipelineEvent<TestKey, Boolean>>>()
        val completionMap =
            ConcurrentHashMap<Pair<Int, DestinationStream.Descriptor>, AtomicInteger>()
        val inputFlows =
            arrayOf<Flow<PipelineEvent<StreamKey, String>>>(
                mockk(relaxed = true),
                mockk(relaxed = true)
            )
        val tasks =
            (0 until 2).map {
                LoadPipelineStepTask(
                    batchAccumulatorNoUpdate,
                    inputFlows[it],
                    batchUpdateQueue,
                    object : OutputPartitioner<StreamKey, String, TestKey, Boolean> {
                        override fun getOutputKey(inputKey: StreamKey, output: Boolean): TestKey {
                            return TestKey(output, inputKey.stream)
                        }

                        override fun getPart(outputKey: TestKey, numParts: Int): Int {
                            if (outputKey.output) return 1
                            return 0
                        }
                    },
                    outputQueue,
                    null,
                    it,
                    2,
                    1,
                    completionMap
                )
            }

        coEvery { batchAccumulatorNoUpdate.start(any(), any()) } returns Closeable()
        coEvery { batchAccumulatorNoUpdate.accept(any(), any()) } returns NoOutput(Closeable())
        coEvery { batchAccumulatorNoUpdate.finish(any()) } returns FinalOutput(true)
        coEvery { batchUpdateQueue.publish(any()) } returns Unit
        coEvery { outputQueue.partitions } returns 2
        coEvery { outputQueue.publish(any(), any()) } returns Unit
        coEvery { outputQueue.broadcast(any()) } returns Unit

        val eosSignals = if (sendBoth) 0 until 2 else listOf(0)
        eosSignals.forEach {
            coEvery { inputFlows[it].collect(any()) } coAnswers
                {
                    val collector = firstArg<FlowCollector<PipelineEvent<StreamKey, String>>>()
                    collector.emit(
                        endOfStreamEvent(
                            StreamKey(DestinationStream.Descriptor("namespace", "stream"))
                        )
                    )
                }
        }

        listOf(launch { tasks[0].execute() }, launch { tasks[1].execute() }).joinAll()

        coVerify(exactly = eosSignals.sum()) { outputQueue.broadcast(any()) }
    }

    @Test
    fun `end-of-stream not forwarded if all tasks do not receive it`() = runEndOfStreamTest(false)

    @Test fun `end-of-stream forwarded to all tasks if all receive it`() = runEndOfStreamTest(true)
}
