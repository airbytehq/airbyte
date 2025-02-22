/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/**
 * Used internally by the CDK to implement the DirectLoader.
 *
 * Creates a single pipeline step reading from a (possibly partitioned) record stream. Batch updates
 * are written to the batchStateUpdateQueue whenever the loader returns
 */
@Singleton
@Requires(bean = DirectLoaderFactory::class)
class DirectLoadPipeline(val pipelineStep: DirectLoadPipelineStep<*>) :
    LoadPipeline(listOf(pipelineStep))
