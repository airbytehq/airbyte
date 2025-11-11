/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import io.airbyte.cdk.load.message.BatchState
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.WithBatchState
import io.airbyte.cdk.load.pipeline.BatchAccumulator
import io.airbyte.cdk.load.pipeline.BatchAccumulatorResult
import io.airbyte.cdk.load.pipeline.FinalOutput
import io.airbyte.cdk.load.pipeline.NoOutput
import io.airbyte.cdk.load.write.db.InsertLoader
import io.airbyte.cdk.load.write.db.InsertLoaderRequest
import io.airbyte.cdk.load.write.db.InsertLoaderRequestBuilder
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Requires(bean = InsertLoader::class)
class InsertLoaderRequestBuilderAccumulator<Q : InsertLoaderRequest>(
    private val loaderFactory: InsertLoader<Q>,
    @Named("insertLoaderClampedRequestSizeBytes") private val maxRequestSizeBytes: Long
) :
    BatchAccumulator<
        InsertLoaderRequestBuilder<Q>,
        StreamKey,
        DestinationRecordRaw,
        InsertLoaderRequestBuilderAccumulator.Result<Q>
    > {

    data class Result<Q>(val request: Q) : WithBatchState {
        override val state: BatchState = BatchState.PROCESSED
    }

    override suspend fun start(key: StreamKey, part: Int): InsertLoaderRequestBuilder<Q> {
        return loaderFactory.createAccumulator(key.stream, part)
    }

    override suspend fun accept(
        input: DestinationRecordRaw,
        state: InsertLoaderRequestBuilder<Q>
    ): BatchAccumulatorResult<InsertLoaderRequestBuilder<Q>, Result<Q>> {
        return when (val output = state.accept(input, maxRequestSizeBytes)) {
            is InsertLoaderRequestBuilder.NoOutput<Q> -> NoOutput(state)
            is InsertLoaderRequestBuilder.Request<Q> -> {
                FinalOutput(Result(output.request))
            }
        }
    }

    override suspend fun finish(
        state: InsertLoaderRequestBuilder<Q>
    ): FinalOutput<InsertLoaderRequestBuilder<Q>, Result<Q>> {
        return FinalOutput(Result(state.finish().request))
    }
}
