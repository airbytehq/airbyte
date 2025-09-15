/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage.file

import io.airbyte.cdk.load.factory.object_storage.IsFileTransferCondition
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleter
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Requires(condition = IsFileTransferCondition::class)
class ForwardFileRecordStep<T>(
    @Named("fileCompletedQueue")
    private val inputQueue:
        PartitionedQueue<PipelineEvent<StreamKey, ObjectLoaderUploadCompleter.UploadResult<T>>>,
    @Named("recordQueue")
    private val outputQueue: PartitionedQueue<PipelineEvent<StreamKey, DestinationRecordRaw>>,
) : LoadPipelineStep {
    override val numWorkers: Int = 1

    override fun taskForPartition(partition: Int) =
        ForwardFileRecordTask(
            inputQueue,
            outputQueue,
            partition,
        )
}
