/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/**
 * Used internally by the CDK to implement the DirectLoader.
 *
 * Creates a single pipeline step reading from a (possibly partitioned) record stream. Batch updates
 * are written to the batchStateUpdateQueue whenever the loader returns
 */
@Singleton
@Requires(property = "airbyte.destination.connector.load-strategy", value = "direct")
class DirectLoadPipeline(val pipelineStep: DirectLoadPipelineStep<*>) :
    LoadPipeline(listOf(pipelineStep))
