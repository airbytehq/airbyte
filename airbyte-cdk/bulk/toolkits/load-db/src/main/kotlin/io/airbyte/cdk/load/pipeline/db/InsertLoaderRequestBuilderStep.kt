/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTask
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import io.airbyte.cdk.load.write.db.InsertLoader
import io.airbyte.cdk.load.write.db.InsertLoaderRequest
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Requires(bean = InsertLoader::class)
class InsertLoaderRequestBuilderStep<Q : InsertLoaderRequest>(
    val loader: InsertLoader<Q>,
    val requestBuilder: InsertLoaderRequestBuilder<Q>,
    val taskFactory: LoadPipelineStepTaskFactory,
    @Named("insertLoaderRequestQueue")
    val outputQueue:
        PartitionedQueue<PipelineEvent<StreamKey, InsertLoaderRequestBuilder.Result<Q>>>,
    val outputPartitioner: InsertLoaderRequestPartitioner<Q>,
) : LoadPipelineStep {
    override val numWorkers: Int = loader.numRequestBuilders

    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        return taskFactory.createFirstStep(
            requestBuilder,
            outputPartitioner,
            outputQueue,
            partition,
            numWorkers,
        )
    }
}
