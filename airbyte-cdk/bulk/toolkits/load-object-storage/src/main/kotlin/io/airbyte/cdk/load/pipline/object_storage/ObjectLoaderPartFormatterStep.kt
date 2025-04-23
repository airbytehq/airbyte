/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipline.object_storage

import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.pipeline.LoadPipelineStep
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTask
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import io.airbyte.cdk.load.write.object_storage.ObjectLoader
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Requires(bean = ObjectLoader::class)
class ObjectLoaderPartFormatterStep(
    private val objectLoader: ObjectLoader,
    private val partFormatter: ObjectLoaderPartFormatter<*>,
    @Named("objectLoaderPartQueue")
    val outputQueue:
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>,
    val taskFactory: LoadPipelineStepTaskFactory
) : LoadPipelineStep {
    override val numWorkers: Int = objectLoader.numPartWorkers

    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        return taskFactory.createFirstStep(
            partFormatter,
            ObjectLoaderFormattedPartPartitioner(),
            outputQueue,
            partition,
            numWorkers
        )
    }
}
