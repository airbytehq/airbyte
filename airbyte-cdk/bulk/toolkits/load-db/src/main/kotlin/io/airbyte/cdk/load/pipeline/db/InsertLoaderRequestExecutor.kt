/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import io.airbyte.cdk.load.message.BatchState
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.WithBatchState
import io.airbyte.cdk.load.pipeline.BatchAccumulator
import io.airbyte.cdk.load.pipeline.BatchAccumulatorResult
import io.airbyte.cdk.load.pipeline.FinalOutput
import io.airbyte.cdk.load.pipeline.IntermediateOutput
import io.airbyte.cdk.load.write.db.InsertLoader
import io.airbyte.cdk.load.write.db.InsertLoaderRequest
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.io.Closeable

@Singleton
@Requires(bean = InsertLoader::class)
class InsertLoaderRequestExecutor<Q : InsertLoaderRequest>(
    private val insertLoader: InsertLoader<Q>
) :
    BatchAccumulator<
        Closeable,
        StreamKey,
        InsertLoaderRequestBuilder.Result<Q>,
        InsertLoaderRequestExecutor.Result
    > {

    data object Result : WithBatchState {
        override val state: BatchState = BatchState.COMPLETE
    }

    override suspend fun start(key: StreamKey, part: Int): Closeable {
        return Closeable { /* do nothing */}
    }

    override suspend fun accept(
        input: InsertLoaderRequestBuilder.Result<Q>,
        state: Closeable
    ): BatchAccumulatorResult<Closeable, Result> {
        input.request.submit()
        // This could be final or intermediate, might as well avoid churn on the state.
        return IntermediateOutput(state, Result)
    }

    override suspend fun finish(state: Closeable): FinalOutput<Closeable, Result> {
        return FinalOutput(Result)
    }
}
