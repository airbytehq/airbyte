/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.config.PipelineInputEvent
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineContext
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineHeartbeat
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
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.CheckpointValue
import io.airbyte.cdk.load.task.OnEndOfSync
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.write.LoadStrategy
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
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
    val checkpointCounts: MutableMap<CheckpointId, CheckpointValue> = mutableMapOf(),
    val inputCount: Long = 0,
    val createdAtMs: Long = System.currentTimeMillis()
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
    private val stepId: String,
    private val streamCompletions:
        ConcurrentHashMap<Pair<String, DestinationStream.Descriptor>, AtomicInteger>,
    private val maxNumConcurrentKeys: Int? = null,
) : Task {
    private val log = KotlinLogging.logger {}

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
                                "$stepId[$part] received input for complete stream ${input.key.stream}. This indicates data was processed out of order and future bookkeeping might be corrupt. Failing hard."
                            )
                        }

                        /**
                         * Enforce the specified maximum number of concurrent keys. If this is a new
                         * key, AND we are already at the max, force a call to finish on the key
                         * whose state contains the most data, then evict it.
                         */
                        maxNumConcurrentKeys?.let { maxKeys ->
                            if (
                                !stateStore.stateWithCounts.contains(input.key) &&
                                    stateStore.stateWithCounts.size >= maxKeys
                            ) {
                                // Pick the key with the highest input count
                                val (key, state) =
                                    stateStore.stateWithCounts.maxByOrNull { it.value.inputCount }!!
                                stateStore.stateWithCounts.remove(key)
                                log.info {
                                    "Saw greater than $maxNumConcurrentKeys keys, evicting highest accumulating $key (inputs=${state.inputCount})"
                                }

                                val output = batchAccumulator.finish(state.accumulatorState)
                                handleOutput(
                                    key,
                                    state.checkpointCounts,
                                    output.output,
                                    state.inputCount
                                )

                                state.close()
                            }
                        }

                        // Get or create the accumulator state associated w/ the input key.
                        val stateWithCounts =
                            stateStore.stateWithCounts
                                .getOrPut(input.key) {
                                    StateWithCounts(
                                        accumulatorState = batchAccumulator.start(input.key, part)
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
                        input.postProcessingCallback?.let {
                            it()
                        } // TODO: Accumulate and release when persisted
                        input.checkpointCounts.forEach {
                            stateWithCounts.checkpointCounts.merge(it.key, it.value) { old, new ->
                                old.plus(new)
                            }
                        }

                        // Finalize the state and output
                        val (finalAccState, finalAccOutput) =
                            if (result.output == null) {
                                // Possibly force an output (and if so, discard the state)
                                if (
                                    flushStrategy?.shouldFlush(
                                        stateWithCounts.inputCount,
                                        System.currentTimeMillis() - stateWithCounts.createdAtMs
                                    ) == true
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
                                    stateWithCounts.inputCount,
                                    input.context,
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
                        val inputCountEos = stateStore.streamCounts[input.stream] ?: 0

                        val keysToRemove =
                            stateStore.stateWithCounts.keys.filter { it.stream == input.stream }

                        finishKeys(stateStore, keysToRemove, "end-of-stream")

                        // Only forward end-of-stream if ALL workers have seen end-of-stream.
                        val numWorkersSeenEos =
                            streamCompletions
                                .getOrPut(Pair(stepId, input.stream)) { AtomicInteger(0) }
                                .incrementAndGet()
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
                            BatchEndOfStream(input.stream, stepId, part, inputCountEos)
                        )

                        stateStore
                    }
                    is PipelineHeartbeat -> {
                        flushStrategy?.let { strategy ->
                            val now = System.currentTimeMillis()
                            val keysToRemove =
                                stateStore.stateWithCounts
                                    .filter { (_, v) ->
                                        strategy.shouldFlush(v.inputCount, now - v.createdAtMs)
                                    }
                                    .keys
                            finishKeys(stateStore, keysToRemove, "flush strategy")
                        }

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

    private suspend fun finishKeys(
        stateStore: StateStore<K1, S>,
        keys: Iterable<K1>,
        reason: String
    ) {
        keys.forEach { key ->
            log.info { "Finishing state for $key due to $reason" }
            stateStore.stateWithCounts.remove(key)?.let { stateWithCounts ->
                val output = batchAccumulator.finish(stateWithCounts.accumulatorState).output
                handleOutput(
                    key,
                    stateWithCounts.checkpointCounts,
                    output,
                    stateWithCounts.inputCount,
                )
                stateWithCounts.close()
            }
        }
    }

    @VisibleForTesting
    suspend fun handleOutput(
        inputKey: K1,
        checkpointCounts: Map<CheckpointId, CheckpointValue>,
        output: U,
        inputCount: Long,
        context: PipelineContext? = null,
    ) {

        // Only publish the output if there's a next step.
        outputQueue?.let {
            val outputKey = outputPartitioner!!.getOutputKey(inputKey, output)
            val message =
                PipelineMessage(checkpointCounts.toMap(), outputKey, output, context = context)
            val outputPart = outputPartitioner.getPart(outputKey, part, it.partitions)
            it.publish(message, outputPart)
        }

        // If the output contained a global batch state, publish an update.
        if (output is WithBatchState) {
            val update =
                BatchStateUpdate(
                    stream = inputKey.stream,
                    checkpointCounts = checkpointCounts.toMap(),
                    state = output.state,
                    taskName = stepId,
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
    @Named("dataChannelInputFlows") val inputFlows: Array<Flow<PipelineInputEvent>>,
    private val flushStrategy: PipelineFlushStrategy,
) {
    // A map of (TaskId, Stream) ->  streams to ensure eos is not forwarded from
    // task N to N+1 until all workers have seen eos.
    private val streamCompletions =
        ConcurrentHashMap<Pair<String, DestinationStream.Descriptor>, AtomicInteger>()

    fun <S : AutoCloseable, K1 : WithStream, T, K2 : WithStream, U : Any> create(
        batchAccumulator: BatchAccumulator<S, K1, T, U>,
        inputFlow: Flow<PipelineEvent<K1, T>>,
        outputPartitioner: OutputPartitioner<K1, T, K2, U>?,
        outputQueue: PartitionedQueue<PipelineEvent<K2, U>>?,
        flushStrategy: PipelineFlushStrategy?,
        part: Int,
        numWorkers: Int,
        stepId: String,
        maxNumConcurrentKeys: Int? = null,
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
            stepId,
            streamCompletions,
            maxNumConcurrentKeys
        )
    }

    fun <S : AutoCloseable, K2 : WithStream, U : Any> createFirstStep(
        batchAccumulator: BatchAccumulator<S, StreamKey, DestinationRecordRaw, U>,
        outputPartitioner: OutputPartitioner<StreamKey, DestinationRecordRaw, K2, U>?,
        outputQueue: PartitionedQueue<PipelineEvent<K2, U>>?,
        part: Int,
        numWorkers: Int,
        maxNumConcurrentKeys: Int? = null,
    ): LoadPipelineStepTask<S, StreamKey, DestinationRecordRaw, K2, U> {
        return create(
            batchAccumulator,
            inputFlows[part],
            outputPartitioner,
            outputQueue,
            flushStrategy,
            part,
            numWorkers,
            stepId = "first-step",
            maxNumConcurrentKeys = maxNumConcurrentKeys
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
            stepId = "final-step"
        )
    }

    fun <S : AutoCloseable, K2 : WithStream, U : Any> createOnlyStep(
        batchAccumulator: BatchAccumulator<S, StreamKey, DestinationRecordRaw, U>,
        part: Int,
        numWorkers: Int,
        maxNumConcurrentKeys: Int? = null,
    ): LoadPipelineStepTask<S, StreamKey, DestinationRecordRaw, K2, U> {
        return createFirstStep(batchAccumulator, null, null, part, numWorkers, maxNumConcurrentKeys)
    }

    fun <S : AutoCloseable, K1 : WithStream, T, K2 : WithStream, U : Any> createIntermediateStep(
        batchAccumulator: BatchAccumulator<S, K1, T, U>,
        inputFlow: Flow<PipelineEvent<K1, T>>,
        outputPartitioner: OutputPartitioner<K1, T, K2, U>?,
        outputQueue: PartitionedQueue<PipelineEvent<K2, U>>?,
        part: Int,
        numWorkers: Int,
        stepId: String,
    ): LoadPipelineStepTask<S, K1, T, K2, U> {
        return create(
            batchAccumulator,
            inputFlow,
            outputPartitioner,
            outputQueue,
            null,
            part,
            numWorkers,
            stepId,
        )
    }
}
