package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.message.BatchState
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.write.BatchLoadStrategy
import io.github.oshai.kotlinlogging.KotlinLogging
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.fold

class BatchLoaderCreateBatchTask<K: WithStream>(
    val inputFlow: Flow<PipelineEvent<K, DestinationRecordRaw>>,
    val flushStrategy: PipelineFlushStrategy,
    val loadStrategy: BatchLoadStrategy,
    val partition: Int,
    val batchStateUpdateQueue: ChannelMessageQueue<BatchUpdate>
): Task {
    private val log = KotlinLogging.logger {}

    override val terminalCondition = SelfTerminating

    val taskName = "BatchLoaderCreateBatchTask"

    data class Batch(
        var inputCount: Long = 0L,
        var inputSizeBytes: Long = 0L,
        val startTimeMs: Long = System.currentTimeMillis(),
        val data: MutableList<DestinationRecordRaw> = mutableListOf(),
        val checkpointCounts: MutableMap<CheckpointId, Long> = mutableMapOf(),
        var reservation: Reserved<DestinationRecordRaw>? = null
    )

    inner class Batches(
        val byKey: MutableMap<K, Batch> = mutableMapOf()
    )

    override suspend fun execute() {
        inputFlow.fold(Batches()) { batches, event ->
            when (event) {
                is PipelineMessage -> {
                    val batch = batches.byKey.getOrPut(event.key) { Batch() }
                    batch.data.add(event.value)
                    event.checkpointCounts.forEach { (checkpointId, count) ->
                        batch.checkpointCounts.merge(checkpointId, count) { oldCount, newCount ->
                            oldCount + newCount
                        }
                    }
                    batch.inputCount ++
                    batch.inputSizeBytes += event.value.serializedSizeBytes
                    // Merge the underlying memory reservation.
                    // The next step will free it when done with the batch.
                    if (event.reservation != null) {
                        if (batch.reservation == null) {
                            batch.reservation = event.reservation
                        } else {
                            batch.reservation = batch.reservation?.merge(event.reservation)
                        }
                    }
                }
                is PipelineHeartbeat -> {
                    maybeFlush(batches)
                }
                is PipelineEndOfStream -> {
                    log.info { "Received end-of-stream for ${event.stream}" }
                    val batchesToEvict = batches.byKey.filter { (key, _) ->
                        key.stream == event.stream
                    }
                    batchesToEvict.forEach { (key, batch) ->
                        log.info { "End-of-stream ${event.stream}: finishing batch for $key" }
                        removeAndProcess(batches.byKey, key, batch)
                    }
                }
            }
            batches
        }
    }

    private suspend fun maybeFlush(batches: Batches) {
        val now = System.currentTimeMillis()
        val batchesByFlushStrategy = batches.byKey.entries.filter { (_, batch) ->
            flushStrategy.shouldFlush(batch.inputCount, now - batch.startTimeMs)
        }
        batchesByFlushStrategy.forEach { (key, batch) ->
            log.info { "Forced flushing batches for $key" }
            removeAndProcess(batches.byKey, key, batch)
        }
        val batchesByDataSize = batches.byKey.entries.filter { (_, batch) ->
            batch.inputSizeBytes >= loadStrategy.targetBatchSizeBytes
        }
        batchesByDataSize.forEach { (key, batch) ->
            log.info { "Flushing data-sufficient batches for $key" }
            removeAndProcess(batches.byKey, key, batch)
        }
    }

    private suspend fun removeAndProcess(batchesByKey: MutableMap<K, Batch>, key: K, batch: Batch) {
        batchesByKey.remove(key)
        loadStrategy.loadBatch(key.stream, partition, batch.data)
        batch.reservation?.release()

        batchStateUpdateQueue.publish(
            BatchStateUpdate(
                key.stream,
                batch.checkpointCounts,
                BatchState.COMPLETE,
                taskName,
                partition,
                batch.inputCount
            )
        )
    }
}
