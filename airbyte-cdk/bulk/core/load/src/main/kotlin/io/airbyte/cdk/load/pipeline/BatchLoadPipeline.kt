package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.write.BatchLoadStrategy
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/**
 * Implements BatchLoadStrategy as a single-step pipline that
 * accumulates batches and loads them with BatchLoadStrategy::loadBatch.
 */
@Singleton
@Requires(bean = BatchLoadStrategy::class)
class BatchLoadPipeline(
    createBatchStep: BatchLoaderCreateBatchStep<*>,
): LoadPipeline(
    listOf(createBatchStep)
)
