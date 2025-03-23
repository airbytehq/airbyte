/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
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
import io.airbyte.cdk.load.write.db.InsertLoaderAccumulator
import io.airbyte.cdk.load.write.db.InsertLoaderRequest
import io.micronaut.context.annotation.Requires
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
@Requires(bean = InsertLoader::class)
class InsertLoaderRequestBuilder<Q : InsertLoaderRequest>(
    private val loaderFactory: InsertLoader<Q>,
    @Named("insertLoaderClampedRequestSizeBytes") private val maxRequestSizeBytes: Long
) :
    BatchAccumulator<
        InsertLoaderAccumulator<Q>,
        StreamKey,
        DestinationRecordRaw,
        InsertLoaderRequestBuilder.Result<Q>
    > {

    data class Result<Q>(val request: Q) : WithBatchState {
        override val state: BatchState = BatchState.PROCESSED
    }

    override suspend fun start(key: StreamKey, part: Int): InsertLoaderAccumulator<Q> {
        return loaderFactory.createAccumulator(key.stream, part)
    }

    override suspend fun accept(
        input: DestinationRecordRaw,
        state: InsertLoaderAccumulator<Q>
    ): BatchAccumulatorResult<InsertLoaderAccumulator<Q>, Result<Q>> {
        return when (val output = state.accept(input, maxRequestSizeBytes)) {
            is InsertLoaderAccumulator.NoOutput<Q> -> NoOutput(state)
            is InsertLoaderAccumulator.Request<Q> -> {
                FinalOutput(Result(output.request))
            }
        }
    }

    override suspend fun finish(
        state: InsertLoaderAccumulator<Q>
    ): FinalOutput<InsertLoaderAccumulator<Q>, Result<Q>> {
        return FinalOutput(Result(state.finish().request))
    }
}
