/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import io.airbyte.cdk.load.write.db.InsertLoader
import io.airbyte.cdk.load.write.db.InsertLoaderRequest
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Requires(bean = InsertLoader::class)
class InsertLoaderRequestExecutorStep<Q : InsertLoaderRequest>(
    loader: InsertLoader<Q>,
    private val requestExecutor: InsertLoaderRequestExecutor<Q>,
    @Named("insertLoaderRequestQueue")
    private val inputQueue:
        PartitionedQueue<PipelineEvent<StreamKey, InsertLoaderRequestBuilder.Result<Q>>>,
    private val taskFactory: LoadPipelineStepTaskFactory
) : LoadPipelineStep {
    override val numWorkers: Int = loader.numRequestExecutors

    override fun taskForPartition(
        partition: Int
    ): io.airbyte.cdk.load.task.internal.LoadPipelineStepTask<*, *, *, *, *> {
        return taskFactory.createFinalStep(requestExecutor, inputQueue, partition, numWorkers)
    }
}
