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
    suspend fun handleEvent(event: PipelineEvent<StreamKey, DestinationRecordRaw>) {
        val streamDesc =
            when (event) {
                is PipelineMessage -> event.key.stream
                is PipelineEndOfStream<*, *> -> event.stream
                is PipelineHeartbeat<*, *> -> null
            }
        val stream = streamDesc?.let { catalog.getStream(it) }

        if (stream?.includeFiles == true) {
            if (event is PipelineMessage) {
                event.context =
                    PipelineContext(
                        event.checkpointCounts,
                        event.value,
                    )
            }

            fileQueue.publish(event, partition)
        } else {
            // all heartbeat events go straight to the record queue
            recordQueue.publish(event, partition)
        }
    }
}
