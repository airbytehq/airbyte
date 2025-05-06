package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.file.SpillFileProvider
import io.airbyte.cdk.load.message.BatchState
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.ProtocolMessageDeserializer
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.task.OnEndOfSync
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.implementor.toRecordIterator
import io.airbyte.cdk.load.util.write
import io.airbyte.cdk.load.write.BatchLoadStrategy
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import java.io.File
import java.io.OutputStream
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.fold

class BatchLoaderCreateBatchTask<K: WithStream>(
    val inputFlow: Flow<PipelineEvent<K, DestinationRecordRaw>>,
    val flushStrategy: PipelineFlushStrategy,
    val loadStrategy: BatchLoadStrategy,
    val partition: Int,
    val batchStateUpdateQueue: ChannelMessageQueue<BatchUpdate>,
    val spillFileProvider: SpillFileProvider,
    val diskManager: ReservationManager,
    private val deserializer: ProtocolMessageDeserializer,
): Task {
    private val log = KotlinLogging.logger {}

    override val terminalCondition = OnEndOfSync

    val taskName = "BatchLoaderCreateBatchTask-$partition"

    inner class Batch(
        var inputCount: Long = 0L,
        var inputSizeBytes: Long = 0L,
        val startTimeMs: Long = System.currentTimeMillis(),
        val fileSink: File = spillFileProvider.createTempFile().toFile(),
        val fileSinkOutputStream: OutputStream = fileSink.outputStream(),
        val checkpointCounts: MutableMap<CheckpointId, Long> = mutableMapOf(),
        var reservation: Reserved<String>? = null
    )

    inner class Batches(
        val byKey: MutableMap<K, Batch> = mutableMapOf()
    )

    override suspend fun execute() {
        inputFlow.fold(Batches()) { batches, event ->
            when (event) {
                is PipelineMessage -> {
                    val batch = batches.byKey.getOrPut(event.key) { Batch() }

                    // Write the record to disk.
                    val rawRecord = event.value.asSerializedString()
                    val diskReservation = diskManager.reserve(event.value.serializedSizeBytes, rawRecord)
                    if (batch.reservation == null) {
                        batch.reservation = diskReservation
                    } else {
                        batch.reservation = batch.reservation?.merge(diskReservation)
                    }
                    batch.fileSinkOutputStream.write(rawRecord)
                    batch.fileSinkOutputStream.write('\n'.code)

                    // Aggregate bookkeeping metadata.
                    event.checkpointCounts.forEach { (checkpointId, count) ->
                        batch.checkpointCounts.merge(checkpointId, count) { oldCount, newCount ->
                            oldCount + newCount
                        }
                    }
                    batch.inputCount ++
                    batch.inputSizeBytes += event.value.serializedSizeBytes

                    // Test whether we should flush.
                    val now = System.currentTimeMillis()
                    if (flushStrategy.shouldFlush(batch.inputCount, now - batch.startTimeMs)) {
                        log.info { "Force flush by flush strategy ${flushStrategy::class.simpleName} for ${event.key}" }
                        removeAndProcess(batches.byKey, event.key, batch)
                    } else if(batch.inputSizeBytes >= loadStrategy.targetBatchSizeBytes) {
                        log.info { "Batch size ${batch.inputSizeBytes}b is data-sufficient for ${event.key}, flushing" }
                        removeAndProcess(batches.byKey, event.key, batch)
                    }
                    event.reservation?.release()
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
                    batchStateUpdateQueue.publish(
                        BatchEndOfStream(
                            event.stream,
                            taskName,
                            partition,
                            batchesToEvict.values.sumOf { it.inputCount }
                        )
                    )
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
        // Finish the file
        batchesByKey.remove(key)
        batch.fileSinkOutputStream.flush()
        batch.fileSinkOutputStream.close()

        // Hand the batch to the client code.
        batch.fileSink.inputStream().use {
            loadStrategy.loadBatch(key.stream, partition, it.toRecordIterator(deserializer))
        }
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
