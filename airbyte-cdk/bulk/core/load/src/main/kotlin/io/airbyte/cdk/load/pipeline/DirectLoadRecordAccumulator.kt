/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.WithBatchState
import io.airbyte.cdk.load.message.WithStream
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.DirectLoader.*
import io.airbyte.cdk.load.write.DirectLoaderFactory
import jakarta.inject.Singleton

data class DirectLoadAccResult(override val state: Batch.State) : WithBatchState

/**
 * Used internally by the CDK to wrap the client-provided DirectLoader in a generic
 * BatchAccumulator, so that it can be used as a pipeline step. At this stage, the loader's public
 * interface is mapped to the internal interface, hiding internal mechanics.
 */
@Singleton
class DirectLoadRecordAccumulator<K : WithStream, S : DirectLoader>(
    val directLoaderFactory: DirectLoaderFactory<S>
) : BatchAccumulator<K, DirectLoader, DestinationRecordAirbyteValue, DirectLoadAccResult> {
    override fun start(key: K, part: Int): DirectLoader {
        return directLoaderFactory.create(key.stream, part)
    }

    override fun accept(
        record: DestinationRecordAirbyteValue,
        state: DirectLoader
    ): Pair<DirectLoader, DirectLoadAccResult?> {
        state.accept(record).let {
            return when (it) {
                is Incomplete -> Pair(state, null)
                is Complete -> Pair(state, DirectLoadAccResult(batchStateFor(it)))
            }
        }
    }

    override fun finish(state: DirectLoader): DirectLoadAccResult {
        val result = state.finish()
        return DirectLoadAccResult(batchStateFor(result))
    }

    private fun batchStateFor(state: Complete): Batch.State {
        return if (state.persisted) Batch.State.COMPLETE else Batch.State.PROCESSED
    }
}
