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
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.pipeline.RecordCountFlushStrategy
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTask
import io.airbyte.cdk.load.write.object_storage.FileLoader
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Requires(bean = FileLoader::class)
@Replaces(ObjectLoaderPartStep::class)
class FileLoaderPartStep(
    private val catalog: DestinationCatalog,
    private val fileLoader: FileLoader,
    @Named("fileQueue")
    val inputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationFile>>,
    @Named("batchStateUpdateQueue") val batchQueue: QueueWriter<BatchUpdate>,
    @Named("objectLoaderPartQueue") val partQueue: PartitionedQueue<PipelineEvent<ObjectKey, Part>>,
    val pathFactory: ObjectStoragePathFactory,
) : LoadPipelineStep {
    override val numWorkers: Int = fileLoader.numPartWorkers

    override fun taskForPartition(partition: Int): Task {
        return FileLoaderProcessFileTask(
            catalog,
            pathFactory,
            fileLoader,
            inputQueue,
            batchQueue,
            partQueue,
            partition
        )
    }
}
