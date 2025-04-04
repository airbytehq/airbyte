/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.BatchState
import io.airbyte.cdk.load.message.WithBatchState
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.BatchAccumulator
import io.airbyte.cdk.load.pipeline.BatchAccumulatorResult
import io.airbyte.cdk.load.pipeline.FinalOutput
import io.airbyte.cdk.load.pipeline.IntermediateOutput
import io.airbyte.cdk.load.pipeline.NoOutput
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleter
import io.airbyte.cdk.load.write.db.BulkLoader
import io.airbyte.cdk.load.write.db.BulkLoaderFactory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(bean = BulkLoaderFactory::class)
@SuppressFBWarnings(value = ["NP_NONNULL_PARAM_VIOLATION"], justification = "Kotlin coroutines")
class BulkLoaderTableLoader<K : WithStream, T : RemoteObject<*>>(
    val bulkLoader: BulkLoaderFactory<K, T>
) :
    BatchAccumulator<
        BulkLoader<T>,
        K,
        ObjectLoaderUploadCompleter.UploadResult<T>,
        BulkLoaderTableLoader.LoadResult
    > {
    data object LoadResult : WithBatchState {
        override val state: BatchState = BatchState.COMPLETE
    }

    override suspend fun start(key: K, part: Int): BulkLoader<T> {
        return bulkLoader.create(key, part)
    }

    override suspend fun accept(
        input: ObjectLoaderUploadCompleter.UploadResult<T>,
        state: BulkLoader<T>
    ): BatchAccumulatorResult<BulkLoader<T>, LoadResult> {
        if (input.remoteObject == null) {
            return NoOutput(state)
        }

        state.load(input.remoteObject!!)
        return IntermediateOutput(state, LoadResult)
    }

    override suspend fun finish(state: BulkLoader<T>): FinalOutput<BulkLoader<T>, LoadResult> {
        return FinalOutput(LoadResult)
    }
}
