/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage.file

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.factory.object_storage.IsFileTransferCondition
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.pipline.object_storage.ObjectKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderFormattedPartPartitioner
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatter
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Requires(condition = IsFileTransferCondition::class)
class FileChunkStep<T : RemoteObject<*>>(
    private val catalog: DestinationCatalog,
    private val fileLoader: ObjectLoader,
    @Named("fileQueue")
    private val inputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
    @Named("filePartQueue")
    private val partQueue:
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
    private val pathFactory: ObjectStoragePathFactory,
    private val uploadIdGenerator: UploadIdGenerator,
) : LoadPipelineStep {
    override val numWorkers: Int = 1

    override fun taskForPartition(partition: Int): Task =
        FileChunkTask<T>(
            fileLoader,
            catalog,
            pathFactory,
            FileHandleFactory(),
            uploadIdGenerator,
            inputQueue,
            partQueue,
            ObjectLoaderFormattedPartPartitioner(),
            partition,
        )
}
