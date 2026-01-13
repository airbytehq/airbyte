/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.DestinationStreamAffinedMessage
import io.airbyte.cdk.load.message.Ignored
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.ProbeMessage
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.Undefined
import io.airbyte.cdk.load.pipeline.InputPartitioner
import io.airbyte.cdk.load.state.PipelineEventBookkeepingRouter
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.task.OnSyncFailureOnly
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.util.use
import io.github.oshai.kotlinlogging.KotlinLogging

private val log = KotlinLogging.logger {}

/**
 * Routes @[DestinationStreamAffinedMessage]s by stream to the appropriate channel and @
 * [CheckpointMessage]s to the state manager.
 *
 * TODO: Handle other message types.
 */
@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "message is guaranteed to be non-null by Kotlin's type system"
)
class InputConsumerTask(
    private val inputFlow: ReservingDeserializingInputFlow,
    private val pipelineInputQueue:
        PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    private val partitioner: InputPartitioner,
    private val pipelineEventBookkeepingRouter: PipelineEventBookkeepingRouter
) : Task {

    override val terminalCondition: TerminalCondition = OnSyncFailureOnly

    private suspend fun handleRecordForPipeline(
        reserved: Reserved<DestinationStreamAffinedMessage>,
    ) {
        val pipelineEvent =
            pipelineEventBookkeepingRouter.handleStreamMessage(
                reserved.value,
                postProcessingCallback = { reserved.release() },
            )
        when (pipelineEvent) {
            is PipelineMessage -> {
                val partition =
                    partitioner.getPartition(pipelineEvent.value, pipelineInputQueue.partitions)
                pipelineInputQueue.publish(pipelineEvent, partition)
            }
            is PipelineEndOfStream -> {
                reserved.release()
                pipelineInputQueue.broadcast(pipelineEvent)
            }
            else -> reserved.release()
        }
    }

    /**
     * Deserialize and route the message to the appropriate channel.
     *
     * NOTE: Not thread-safe! Only a single writer should publish to the queue.
     */
    override suspend fun execute() {
        log.info { "Starting consuming messages from the input flow" }
        pipelineInputQueue.use {
            pipelineEventBookkeepingRouter.use {
                inputFlow.collect { (_, reserved) ->
                    when (val message = reserved.value) {
                        is DestinationStreamAffinedMessage ->
                            handleRecordForPipeline(reserved.replace(message))
                        is CheckpointMessage ->
                            pipelineEventBookkeepingRouter.handleCheckpoint(
                                reserved.replace(message)
                            )
                        Undefined -> log.warn { "Unhandled message: $message" }
                        ProbeMessage,
                        Ignored -> {
                            /* do nothing */
                        }
                    }
                }
            }
        }
    }
}
