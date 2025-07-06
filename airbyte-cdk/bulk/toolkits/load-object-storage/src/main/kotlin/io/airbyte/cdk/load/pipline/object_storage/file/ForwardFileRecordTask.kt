/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage.file

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleter
import io.airbyte.cdk.load.task.OnEndOfSync
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.github.oshai.kotlinlogging.KotlinLogging

class ForwardFileRecordTask<T>(
    private val inputQueue:
        PartitionedQueue<PipelineEvent<StreamKey, ObjectLoaderUploadCompleter.UploadResult<T>>>,
    private val outputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    private val partition: Int,
) : Task {
    override val terminalCondition: TerminalCondition = OnEndOfSync

    val log = KotlinLogging.logger {}

    override suspend fun execute() = inputQueue.consume(partition).collect(this::handleEvent)

    @VisibleForTesting
    suspend fun handleEvent(
        event: PipelineEvent<StreamKey, ObjectLoaderUploadCompleter.UploadResult<T>>
    ) {
        val toPublish: PipelineEvent<StreamKey, DestinationRecordRaw>? =
            when (event) {
                is PipelineMessage -> {
                    // the uploader emits a "dummy" empty object on `finish()`
                    // we are safe to ignore as it serves no direct function
                    if (event.value.remoteObject == null) {
                        null
                    } else {
                        PipelineMessage(
                            event.context!!.parentCheckpointCounts!!,
                            event.key,
                            event.context!!.parentRecord!!,
                        )
                    }
                }
                is PipelineEndOfStream<*, *> -> PipelineEndOfStream(event.stream)
                is PipelineHeartbeat<*, *> -> null
            }

        toPublish?.let { outputQueue.publish(it, 0) }
    }
}
