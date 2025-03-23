/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import io.airbyte.cdk.load.pipeline.LoadPipeline
import io.airbyte.cdk.load.write.db.InsertLoader
import io.airbyte.cdk.load.write.db.InsertLoaderRequest
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(bean = InsertLoader::class)
class InsertLoaderPipeline<Q : InsertLoaderRequest>(
    requestBuilderStep: InsertLoaderRequestBuilderStep<Q>,
    requestExecutorStep: InsertLoaderRequestExecutorStep<Q>,
) : LoadPipeline(steps = listOf(requestBuilderStep, requestExecutorStep))
