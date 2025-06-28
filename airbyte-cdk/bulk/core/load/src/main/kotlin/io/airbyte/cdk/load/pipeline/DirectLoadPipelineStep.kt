/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTask
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Requires(bean = DirectLoaderFactory::class)
class DirectLoadPipelineStep<S : DirectLoader>(
    val directLoaderFactory: DirectLoaderFactory<S>,
    val accumulator: DirectLoadRecordAccumulator<S, StreamKey>,
    val taskFactory: LoadPipelineStepTaskFactory,
    @Named("numInputPartitions") numInputPartitions: Int,
) : LoadPipelineStep {
    private val log = KotlinLogging.logger {}
    override val numWorkers: Int = numInputPartitions

    /**
     * Enforce that each worker can hold at least one open loader. (TODO: Maybe clamp the number of
     * input partitions instead?)
     */
    val maxNumConcurrentKeys =
        directLoaderFactory.maxNumOpenLoaders?.div(numInputPartitions)?.also {
            check(it > 0) {
                "maxNumOpenLoaders=${directLoaderFactory.maxNumOpenLoaders} over numWorkers=$numInputPartitions would result in < 1 open loader per worker."
            }
        }

    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        log.info { "Creating DirectLoad pipeline step task for partition $partition" }
        return taskFactory.createOnlyStep<S, StreamKey, DirectLoadAccResult>(
            accumulator,
            partition,
            numWorkers,
            maxNumConcurrentKeys = maxNumConcurrentKeys
        )
    }
}
