package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.QueueWriter
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.task.SelfTerminating
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.TerminalCondition
import io.airbyte.cdk.load.write.object_storage.FileLoader
import jakarta.inject.Named

class FileLoaderMemoryMapFileTask(
    private val catalog: DestinationCatalog,
    private val fileLoader: FileLoader,
    @Named("fileQueue")
    val inputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationFile>>,
    @Named("batchStateUpdateQueue") val batchQueue: QueueWriter<BatchUpdate>,
    @Named("objectLoaderPartQueue") val partQueue: PartitionedQueue<PipelineEvent<ObjectKey, Part>>,
    val pathFactory: ObjectStoragePathFactory,
): Task {
    override val terminalCondition: TerminalCondition = SelfTerminating

    override suspend fun execute() {

    }
}
