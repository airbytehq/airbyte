/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.dlq

import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatterStep
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.runBlocking

/**
 * Queue Adapter in order to be able to reuse existing ObjectStorage steps for the DeadLetterQueue.
 *
 * Because the [DlqLoader] may batch multiple records and the [ObjectLoaderPartFormatterStep]
 * consumes record one by one, this Adapter flattens a list of [DestinationRecordRaw].
 */
class FlattenQueueAdapter<K : WithStream>(
    private val queue: PartitionedQueue<PipelineEvent<K, DestinationRecordRaw>>,
) : PartitionedQueue<PipelineEvent<K, DlqStepOutput>> {
    override val partitions = queue.partitions

    override fun consume(partition: Int): Flow<PipelineEvent<K, DlqStepOutput>> {
        throw IllegalStateException(
            "Trying to consume from the adapter instead of the underlying queue"
        )
    }

    override suspend fun close() {
        queue.close()
    }

    override suspend fun broadcast(value: PipelineEvent<K, DlqStepOutput>) {
        when (value) {
            is PipelineMessage -> value.flatten().forEach { runBlocking { queue.broadcast(it) } }
            is PipelineHeartbeat -> queue.broadcast(PipelineHeartbeat())
            is PipelineEndOfStream -> queue.broadcast(PipelineEndOfStream(value.stream))
        }
    }

    override suspend fun publish(value: PipelineEvent<K, DlqStepOutput>, partition: Int) {
        when (value) {
            is PipelineMessage ->
                value.flatten().forEach { runBlocking { queue.publish(it, partition) } }
            is PipelineHeartbeat -> queue.publish(PipelineHeartbeat(), partition)
            is PipelineEndOfStream -> queue.publish(PipelineEndOfStream(value.stream), partition)
        }
    }

    private fun PipelineMessage<K, DlqStepOutput>.flatten():
        Iterable<PipelineMessage<K, DestinationRecordRaw>> =
        value.rejectedRecords?.let { failedRecords ->
            val lastIndex = failedRecords.size - 1
            // In order to avoid duplicated counts, we push the checkpoint counts to the last
            // record of the list.
            // Same idea regarding the postProcessingCallback, to avoid having the callback called
            // prematurely, we push it to the last record.
            return failedRecords.mapIndexed { index, destinationRecordRaw ->
                if (index < lastIndex) {
                    PipelineMessage(
                        checkpointCounts = emptyMap(),
                        key = key,
                        value = destinationRecordRaw,
                        postProcessingCallback = null, // Should this be filled
                        context = context,
                    )
                } else {
                    PipelineMessage(
                        checkpointCounts = checkpointCounts,
                        key = key,
                        value = destinationRecordRaw,
                        postProcessingCallback = postProcessingCallback,
                        context = context,
                    )
                }
            }
        }
            ?: emptyList()
}
