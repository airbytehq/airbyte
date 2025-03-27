/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.WithBatchState
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.BatchAccumulator
import io.airbyte.cdk.load.pipeline.BatchEndOfStream
import io.airbyte.cdk.load.pipeline.BatchStateUpdate
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.pipeline.OutputPartitioner
import io.airbyte.cdk.load.pipeline.PipelineFlushStrategy
import io.airbyte.cdk.load.pipeline.RecordCountFlushStrategy
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.task.OnEndOfSync
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.write.LoadStrategy
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.fold

/**
 * Accumulator state with the checkpoint counts (Checkpoint Id -> Records Seen) seen since the state
 * was created.
 *
 * Includes a count of the inputs seen since the state was created.
 */
data class StateWithCounts<S : AutoCloseable>(
    val accumulatorState: S,
    val checkpointCounts: MutableMap<CheckpointId, Long> = mutableMapOf(),
    val inputCount: Long = 0,
) : AutoCloseable {
    override fun close() {
        accumulatorState.close()
    }
}

/** A long-running task that actually implements a load pipeline step. */
class LoadPipelineStepTask<S : AutoCloseable, K1 : WithStream, T, K2 : WithStream, U : Any>(
    private val batchAccumulator: BatchAccumulator<S, K1, T, U>,
    private val inputFlow: Flow<PipelineEvent<K1, T>>,
    private val batchUpdateQueue: QueueWriter<BatchUpdate>,
    private val outputPartitioner: OutputPartitioner<K1, T, K2, U>?,
    private val outputQueue: PartitionedQueue<PipelineEvent<K2, U>>?,
    private val flushStrategy: PipelineFlushStrategy?,
    private val part: Int,
    private val numWorkers: Int,
    private val taskIndex: Int,
    private val streamCompletions:
        ConcurrentHashMap<Pair<Int, DestinationStream.Descriptor>, AtomicInteger>
) : Task {
    private val log = KotlinLogging.logger {}

    private val taskName = batchAccumulator::class.java.simpleName

    override val terminalCondition: TerminalCondition = OnEndOfSync

    /**
     * Task-global state. A map of all the keys seen with associated accumulator state and
     * bookkeeping info. Also includes a global count of inputs seen per stream and fact of stream
     * end (it is a critical error to receive input for a stream that has ended, as it means that
     * something is likely wrong with our bookkeeping.)
     */
    data class StateStore<K1, S : AutoCloseable>(
        val stateWithCounts: MutableMap<K1, StateWithCounts<S>> = mutableMapOf(),
        val streamCounts: MutableMap<DestinationStream.Descriptor, Long> = mutableMapOf(),
        val streamsEnded: MutableSet<DestinationStream.Descriptor> = mutableSetOf(),
    )

    override suspend fun execute() {
        inputFlow.fold(StateStore<K1, S>()) { stateStore, input ->
            try {
                when (input) {
                    is PipelineMessage -> {
                        if (stateStore.streamsEnded.contains(input.key.stream)) {
                            throw IllegalStateException(
                                "$taskName[$part] received input for complete stream ${input.key.stream}. This indicates data was processed out of order and future bookkeeping might be corrupt. Failing hard."
                            )
                        }
                        // Get or create the accumulator state associated w/ the input key.
                        val stateWithCounts =
                            stateStore.stateWithCounts
                                .getOrPut(input.key) {
                                    StateWithCounts(
                                        accumulatorState = batchAccumulator.start(input.key, part),
                                    )
                                }
                                .let { it.copy(inputCount = it.inputCount + 1) }

                        // Accumulate the input and get the new state and output.
                        val result =
                            batchAccumulator.accept(
                                input.value,
                                stateWithCounts.accumulatorState,
                            )

                        // Update bookkeeping metadata
                        input
                            .postProcessingCallback() // TODO: Accumulate and release when persisted
                        input.checkpointCounts.forEach {
                            stateWithCounts.checkpointCounts.merge(it.key, it.value) { old, new ->
                                old + new
                            }
                        }

                        // Finalize the state and output
                        val (finalAccState, finalAccOutput) =
                            if (result.output == null) {
                                // Possibly force an output (and if so, discard the state)
                                if (
                                    flushStrategy?.shouldFlush(stateWithCounts.inputCount) == true
                                ) {
                                    val finalResult = batchAccumulator.finish(result.nextState!!)
                                    Pair(null, finalResult.output)
                                } else {
                                    Pair(result.nextState, null)
                                }
                            } else {
                                // Otherwise, just use what we were given
                                Pair(result.nextState, result.output)
                            }

                        // Publish the output if there is one & reset the input count
                        val inputCount =
                            if (finalAccOutput != null) {
                                // Publish the emitted output w/ bookkeeping counts & clear.
                                handleOutput(
                                    input.key,
                                    stateWithCounts.checkpointCounts,
                                    finalAccOutput,
                                    stateWithCounts.inputCount
                                )
                                stateWithCounts.checkpointCounts.clear()
                                0
                            } else {
                                stateWithCounts.inputCount
                            }

                        // Update the state if `accept` returned a new state, otherwise evict.
                        if (finalAccState != null) {
                            // If accept returned a new state, update the state store.
                            stateStore.stateWithCounts[input.key] =
                                stateWithCounts.copy(
                                    accumulatorState = finalAccState,
                                    inputCount = inputCount
                                )
                        } else {
                            stateStore.stateWithCounts.remove(input.key)?.let {
                                check(inputCount == 0L || it.checkpointCounts.isEmpty()) {
                                    "State evicted with unhandled input ($inputCount) or checkpoint counts(${it.checkpointCounts})"
                                }
                                stateWithCounts.close()
                            }
                        }
                        stateStore.streamCounts.merge(input.key.stream, 1) { old, new -> old + new }
                        stateStore
                    }
                    is PipelineEndOfStream -> {
                        val numWorkersSeenEos =
                            streamCompletions
                                .getOrPut(Pair(taskIndex, input.stream)) { AtomicInteger(0) }
                                .incrementAndGet()
                        val inputCountEos = stateStore.streamCounts[input.stream] ?: 0

                        val keysToRemove =
                            stateStore.stateWithCounts.keys.filter { it.stream == input.stream }

                        keysToRemove.forEach { key ->
                            log.info { "Finishing state for $key remaining at end-of-stream" }
                            stateStore.stateWithCounts.remove(key)?.let { stateWithCounts ->
                                val output =
                                    batchAccumulator.finish(stateWithCounts.accumulatorState).output
                                handleOutput(
                                    key,
                                    stateWithCounts.checkpointCounts,
                                    output,
                                    stateWithCounts.inputCount
                                )
                                stateWithCounts.close()
                            }
                        }

                        // Only forward end-of-stream if ALL workers have seen end-of-stream.
                        if (numWorkersSeenEos == numWorkers) {
                            log.info {
                                "$this saw end-of-stream for ${input.stream} after $inputCountEos inputs, all workers complete"
                            }
                            outputQueue?.broadcast(PipelineEndOfStream(input.stream))
                        } else {
                            log.info {
                                "$this saw end-of-stream for ${input.stream} after $inputCountEos inputs, ${numWorkers - numWorkersSeenEos} workers remaining"
                            }
                        }

                        // Track which tasks are complete
                        stateStore.streamsEnded.add(input.stream)
                        batchUpdateQueue.publish(
                            BatchEndOfStream(input.stream, taskName, part, inputCountEos)
                        )

                        stateStore
                    }
                }
            } catch (t: Throwable) {
                // Close the local state associated with the current batch.
                stateStore.stateWithCounts.values
                    .map { runCatching { it.accumulatorState.close() } }
                    .forEach { it.getOrThrow() }
                throw t
            }
        }
    }

    private suspend fun handleOutput(
        inputKey: K1,
        checkpointCounts: Map<CheckpointId, Long>,
        output: U,
        inputCount: Long
    ) {

        // Only publish the output if there's a next step.
        outputQueue?.let {
            val outputKey = outputPartitioner!!.getOutputKey(inputKey, output)
            val message = PipelineMessage(checkpointCounts.toMap(), outputKey, output)
            val outputPart = outputPartitioner.getPart(outputKey, it.partitions)
            it.publish(message, outputPart)
        }

        // If the output contained a global batch state, publish an update.
        if (output is WithBatchState) {
            val update =
                BatchStateUpdate(
                    stream = inputKey.stream,
                    checkpointCounts = checkpointCounts.toMap(),
                    state = output.state,
                    taskName = taskName,
                    part = part,
                    inputCount = inputCount
                )
            batchUpdateQueue.publish(update)
        }
    }

    override fun toString(): String {
        return "LoadPipelineStepTask(${batchAccumulator::class.simpleName}, part=$part)"
    }
}

@Singleton
@Requires(bean = LoadStrategy::class)
class LoadPipelineStepTaskFactory(
    @Named("batchStateUpdateQueue") val batchUpdateQueue: QueueWriter<BatchUpdate>,
    @Named("recordQueue")
    val recordQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    @Value("\${airbyte.destination.core.record-batch-size-override:null}")
    val batchSizeOverride: Long? = null,
) {
    // A map of (TaskIndex, Stream) ->  streams to ensure eos is not forwarded from
    // task N to N+1 until all workers have seen eos.
    private val streamCompletions =
        ConcurrentHashMap<Pair<Int, DestinationStream.Descriptor>, AtomicInteger>()

    fun <S : AutoCloseable, K1 : WithStream, T, K2 : WithStream, U : Any> create(
        batchAccumulator: BatchAccumulator<S, K1, T, U>,
        inputFlow: Flow<PipelineEvent<K1, T>>,
        outputPartitioner: OutputPartitioner<K1, T, K2, U>?,
        outputQueue: PartitionedQueue<PipelineEvent<K2, U>>?,
        flushStrategy: PipelineFlushStrategy?,
        part: Int,
        numWorkers: Int,
        taskIndex: Int,
    ): LoadPipelineStepTask<S, K1, T, K2, U> {
        return LoadPipelineStepTask(
            batchAccumulator,
            inputFlow,
            batchUpdateQueue,
            outputPartitioner,
            outputQueue,
            flushStrategy,
            part,
            numWorkers,
            taskIndex,
            streamCompletions
        )
    }

    fun <S : AutoCloseable, K2 : WithStream, U : Any> createFirstStep(
        batchAccumulator: BatchAccumulator<S, StreamKey, DestinationRecordRaw, U>,
        outputPartitioner: OutputPartitioner<StreamKey, DestinationRecordRaw, K2, U>?,
        outputQueue: PartitionedQueue<PipelineEvent<K2, U>>?,
        part: Int,
        numWorkers: Int,
    ): LoadPipelineStepTask<S, StreamKey, DestinationRecordRaw, K2, U> {
        return create(
            batchAccumulator,
            recordQueue.consume(part),
            outputPartitioner,
            outputQueue,
            batchSizeOverride?.let { RecordCountFlushStrategy(it) },
            part,
            numWorkers,
            taskIndex = 0
        )
    }

    fun <S : AutoCloseable, K1 : WithStream, T, U : Any> createFinalStep(
        batchAccumulator: BatchAccumulator<S, K1, T, U>,
        inputQueue: PartitionedQueue<PipelineEvent<K1, T>>,
        part: Int,
        numWorkers: Int,
    ): LoadPipelineStepTask<S, K1, T, K1, U> {
        return create(
            batchAccumulator,
            inputQueue.consume(part),
            null,
            null,
            null,
            part,
            numWorkers,
            taskIndex = -1
        )
    }

    fun <S : AutoCloseable, K2 : WithStream, U : Any> createOnlyStep(
        batchAccumulator: BatchAccumulator<S, StreamKey, DestinationRecordRaw, U>,
        part: Int,
        numWorkers: Int,
    ): LoadPipelineStepTask<S, StreamKey, DestinationRecordRaw, K2, U> {
        return createFirstStep(batchAccumulator, null, null, part, numWorkers)
    }

    fun <S : AutoCloseable, K1 : WithStream, T, K2 : WithStream, U : Any> createIntermediateStep(
        batchAccumulator: BatchAccumulator<S, K1, T, U>,
        inputQueue: PartitionedQueue<PipelineEvent<K1, T>>,
        outputPartitioner: OutputPartitioner<K1, T, K2, U>?,
        outputQueue: PartitionedQueue<PipelineEvent<K2, U>>?,
        part: Int,
        numWorkers: Int,
        taskIndex: Int,
    ): LoadPipelineStepTask<S, K1, T, K2, U> {
        return create(
            batchAccumulator,
            inputQueue.consume(part),
            outputPartitioner,
            outputQueue,
            null,
            part,
            numWorkers,
            taskIndex
        )
    }
}
