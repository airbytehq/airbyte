/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
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
import kotlinx.coroutines.flow.fold

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
    private val catalog: DestinationCatalog,
    private val inputFlow: ReservingDeserializingInputFlow,
    private val pipelineInputQueue:
        PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    private val partitioner: InputPartitioner,
    private val pipelineEventBookkeepingRouter: PipelineEventBookkeepingRouter
) : Task {

    override val terminalCondition: TerminalCondition = OnSyncFailureOnly

    private suspend fun handleRecordForPipeline(
        reserved: Reserved<DestinationStreamAffinedMessage>,
        unopenedStreams: MutableSet<DestinationStream.Descriptor>,
    ) {
        val pipelineEvent =
            pipelineEventBookkeepingRouter.handleStreamMessage(
                reserved.value,
                postProcessingCallback = { reserved.release() },
                unopenedStreams
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
        val unopenedStreams = catalog.streams.map { it.descriptor }.toMutableSet()
        pipelineInputQueue.use {
            var processingThrowable: Throwable? = null
            try {
                inputFlow.fold(unopenedStreams) { unopenedStreams, (_, reserved) ->
                    when (val message = reserved.value) {
                        is DestinationStreamAffinedMessage ->
                            handleRecordForPipeline(reserved.replace(message), unopenedStreams)
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
                    unopenedStreams
                }
            } catch (t: Throwable) {
                log.warn(t) {
                    "Encountered exception in input loop. Capturing exception and proceeding with sync shutdown."
                }
                processingThrowable = t
                // intentionally don't throw here.
                // we'll throw an appropriate exception in the `finally` block.
            } finally {
                closePipelineEventBookkeepingRouter(
                    pipelineEventBookkeepingRouter,
                    processingThrowable
                )
            }
        }
    }

    companion object {
        /**
         * pipelineEventBookkeepingRouter.use {...} will swallow baseException. so instead, we'll
         * use a plain try-catch-finally, and actually prioritize the original exception over
         * anything thrown in this `try` block.
         */
        internal suspend fun closePipelineEventBookkeepingRouter(
            pipelineEventBookkeepingRouter: PipelineEventBookkeepingRouter,
            processingThrowable: Throwable?,
        ) {
            try {
                // this is likely to throw a "no stream status message" error,
                // if there's an error during input handling.
                // That's quite misleading (b/c the actual error is that we crashed before we
                // could handle the stream status message),
                // so we would prefer to rethrow the original exception.
                // but we can't just skip this close() call if baseException != null,
                // because that would cause the sync to hang.
                pipelineEventBookkeepingRouter.close()
            } catch (t: Throwable) {
                if (processingThrowable == null) {
                    throw t
                } else {
                    log.warn(t) {
                        "Encountered exception when closing PipelineEventBookkeepingRouter, but we're already handling another exception ($processingThrowable). Swallowing this exception."
                    }
                    throw processingThrowable
                }
            }
            // if the `pipelineEventBookkeepingRouter.close()` ran successfully,
            // we should rethrow the original exception.
            if (processingThrowable != null) {
                log.warn { "Throwing captured exception after triggering sync shutdown." }
                throw processingThrowable
            }
        }
    }
}
