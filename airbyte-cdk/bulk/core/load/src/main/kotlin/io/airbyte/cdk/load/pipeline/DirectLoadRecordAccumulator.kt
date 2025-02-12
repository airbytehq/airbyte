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
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

data class DirectLoadAccResult(override val state: Batch.State) : WithBatchState

/**
 * Used internally by the CDK to wrap the client-provided DirectLoader in a generic
 * BatchAccumulator, so that it can be used as a pipeline step. At this stage, the loader's public
 * interface is mapped to the internal interface, hiding internal mechanics.
 */
@Singleton
@Requires(property = "airbyte.destination.connector.load-strategy", value = "direct")
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
                is Complete -> Pair(state, DirectLoadAccResult(Batch.State.COMPLETE))
            }
        }
    }

    override fun finish(state: DirectLoader): DirectLoadAccResult {
        state.finish()
        return DirectLoadAccResult(Batch.State.COMPLETE)
    }
}
