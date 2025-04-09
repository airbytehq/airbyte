/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
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

@SuppressFBWarnings(value = ["NP_NONNULL_PARAM_VIOLATION"], justification = "Kotlin coroutines")
@Singleton
@Requires(bean = InsertLoader::class)
class InsertLoaderRequestExecutorAccumulator<Q : InsertLoaderRequest>(
    private val insertLoader: InsertLoader<Q>
) :
    BatchAccumulator<
        Closeable,
        StreamKey,
        InsertLoaderRequestBuilderAccumulator.Result<Q>,
        InsertLoaderRequestExecutorAccumulator.Result
    > {

    data object Result : WithBatchState {
        override val state: BatchState = BatchState.COMPLETE
    }

    override suspend fun start(key: StreamKey, part: Int): Closeable {
        return Closeable { /* do nothing */}
    }

    override suspend fun accept(
        input: InsertLoaderRequestBuilderAccumulator.Result<Q>,
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
