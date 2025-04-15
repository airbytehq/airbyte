package io.airbyte.cdk.load.pipline.object_storage.file

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEndOfStream
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineHeartbeat
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition

class RouteEventTask(
    private val catalog: DestinationCatalog,
    private val inputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    private val fileQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    private val recordQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    private val partition: Int,
) : Task {
    override val terminalCondition: TerminalCondition = SelfTerminating

    override suspend fun execute() {
        inputQueue.consume(partition).collect { event ->
            val streamDesc = when (event) {
                is PipelineMessage -> event.key.stream
                is PipelineEndOfStream<*, *> -> event.stream
                is PipelineHeartbeat<*, *> -> null
            }
            val stream = streamDesc?.let { catalog.getStream(it) }

            if (stream?.includeFiles == true) {
                fileQueue.publish(event, partition)
            } else {
                recordQueue.publish(event, partition)
            }
        }
    }
}
