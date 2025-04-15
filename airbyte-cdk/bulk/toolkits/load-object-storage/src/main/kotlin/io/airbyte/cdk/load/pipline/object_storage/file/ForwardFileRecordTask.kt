package io.airbyte.cdk.load.pipline.object_storage.file

import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleter
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition

class ForwardFileRecordTask<T>(
    private val inputQueue: PartitionedQueue<PipelineEvent<StreamKey, ObjectLoaderUploadCompleter.UploadResult<T>>>,
    private val outputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    private val partition: Int,
) : Task {
    override val terminalCondition: TerminalCondition = SelfTerminating

    override suspend fun execute() {
        inputQueue.consume(partition).collect { event ->
            val toPublish: PipelineEvent<StreamKey, DestinationRecordRaw>? = when (event) {
                is PipelineMessage -> PipelineMessage(
                    event.context!!.parentCheckpointCounts!!,
                    event.key,
                    event.context!!.parentRecord!!,
                )
                is PipelineEndOfStream<*, *> -> PipelineEndOfStream(event.stream)
                is PipelineHeartbeat<*, *> -> null
            }

            toPublish?.let { outputQueue.publish(it, 1) }
        }
    }
}
