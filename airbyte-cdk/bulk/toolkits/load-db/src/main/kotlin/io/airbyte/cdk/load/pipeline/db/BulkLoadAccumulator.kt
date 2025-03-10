/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline.db

import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.WithBatchState
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.pipeline.BatchAccumulator
import io.airbyte.cdk.load.pipline.object_storage.LoadedObject
import io.airbyte.cdk.load.write.db.BulkLoad
import io.airbyte.cdk.load.write.db.BulkLoadFactory
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Requires(bean = BulkLoadFactory::class)
class BulkLoadAccumulator<K : WithStream, T : RemoteObject<*>>(
    val bulkLoad: BulkLoadFactory<K, T>
) :
    BatchAccumulator<
        BulkLoadAccumulator<K, T>.State, K, LoadedObject<T>, BulkLoadAccumulator.LoadResult> {
    inner class State(val bulkLoad: BulkLoad<K, T>) : AutoCloseable {
        override fun close() {
            bulkLoad.close()
        }
    }

    data object LoadResult : WithBatchState {
        override val state: Batch.State = Batch.State.COMPLETE
    }

    override suspend fun start(key: K, part: Int): State {
        return State(bulkLoad.create(key))
    }

    override suspend fun accept(input: LoadedObject<T>, state: State): Pair<State?, LoadResult> {
        state.bulkLoad.load(input.remoteObject)
        return state to LoadResult
    }

    override suspend fun finish(state: State): LoadResult = LoadResult
}
