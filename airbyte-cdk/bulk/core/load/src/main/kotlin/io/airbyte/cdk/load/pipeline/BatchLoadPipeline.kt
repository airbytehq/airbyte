package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.write.BatchLoadStrategy
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/**
 * Implements BatchLoadStrategy. A pipleine that
 *  * accumulates records into configurably sized batches
 *  * flushes the batches downstream to the batch loader
 */
@Singleton
@Requires(bean = BatchLoadStrategy::class)
class BatchLoadPipeline(
    createBatchStep: BatchLoaderCreateBatchStep<*>,
    loadBatchStep: BatchLoaderLoadBatchStep<*,*>,
): LoadPipeline(
    listOf(
        createBatchStep,
        loadBatchStep
    )
)
