/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage.file

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineContext
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.task.OnEndOfSync
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import kotlinx.coroutines.flow.Flow

class RouteEventTask(
    private val catalog: DestinationCatalog,
    private val inputFlow: Flow<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    private val fileQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    private val recordQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    private val partition: Int,
) : Task {

    override val terminalCondition: TerminalCondition = OnEndOfSync

    override suspend fun execute() = inputFlow.collect(this::handleEvent)

    @VisibleForTesting
    suspend fun handleEvent(event: PipelineEvent<StreamKey, DestinationRecordRaw>) =
        when (event) {
            is PipelineHeartbeat -> {
                recordQueue.broadcast(event)
            }
            is PipelineMessage -> {
                val streamDesc = event.key.stream
                val stream = catalog.getStream(streamDesc)

                if (stream.includeFiles) {
                    event.context =
                        PipelineContext(
                            event.checkpointCounts,
                            event.value,
                        )

                    fileQueue.publish(event, partition)
                } else {
                    recordQueue.publish(event, partition)
                }

                // TODO: Forward this all the way through to the record stage or change memory
                // "release" mechanism on the input queue.
                // Forwarding all the way through is not currently possible because the first
                // PipelineStep in the file pipe (the formatter) will immediately call this.
                // NOTE: though generically named, the post-processing callback is specifically what
                // "releases" memory on the input queue.
                event.postProcessingCallback?.let { it() }
            }
            is PipelineEndOfStream -> {
                val streamDesc = event.stream
                val stream = catalog.getStream(streamDesc)

                if (stream.includeFiles) {
                    fileQueue.publish(event, partition)
                } else {
                    recordQueue.publish(event, partition)
                }
            }
        }
}
