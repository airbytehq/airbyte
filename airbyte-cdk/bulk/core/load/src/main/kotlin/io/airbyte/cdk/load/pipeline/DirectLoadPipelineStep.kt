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
import jakarta.inject.Singleton

@Singleton
@Requires(bean = DirectLoaderFactory::class)
class DirectLoadPipelineStep<S : DirectLoader>(
    val directLoaderFactory: DirectLoaderFactory<S>,
    val accumulator: DirectLoadRecordAccumulator<S, StreamKey>,
    val taskFactory: LoadPipelineStepTaskFactory,
) : LoadPipelineStep {
    private val log = KotlinLogging.logger {}
    override val numWorkers: Int = directLoaderFactory.inputPartitions

    override fun taskForPartition(partition: Int): LoadPipelineStepTask<*, *, *, *, *> {
        log.info { "Creating DirectLoad pipeline step task for partition $partition" }
        return taskFactory.createOnlyStep<S, StreamKey, DirectLoadAccResult>(
            accumulator,
            partition,
            numWorkers
        )
    }
}
