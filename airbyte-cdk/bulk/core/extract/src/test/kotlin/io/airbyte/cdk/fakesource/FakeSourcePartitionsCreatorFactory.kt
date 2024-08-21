/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.fakesource

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.CreateNoPartitions
import io.airbyte.cdk.read.Feed
import io.airbyte.cdk.read.Global
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreatorFactory
import io.airbyte.cdk.read.StateQuerier
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamPartitionReader
import io.airbyte.cdk.read.StreamPartitionsCreator
import io.airbyte.cdk.read.StreamReadContext
import io.airbyte.cdk.read.StreamReadContextManager
import io.airbyte.cdk.read.streamPartitionsCreatorInput
import jakarta.inject.Singleton

@Singleton
class FakeSourcePartitionsCreatorFactory(
    val streamReadContextManager: StreamReadContextManager,
) : PartitionsCreatorFactory {
    override fun make(
        stateQuerier: StateQuerier,
        feed: Feed,
    ): PartitionsCreator {
        val opaqueStateValue: OpaqueStateValue? = stateQuerier.current(feed)
        return when (feed) {
            is Global -> CreateNoPartitions
            is Stream -> {
                val ctx: StreamReadContext = streamReadContextManager[feed]
                StreamPartitionsCreator(
                    ctx,
                    opaqueStateValue.streamPartitionsCreatorInput(ctx),
                    StreamPartitionsCreator.Parameters(preferParallelized = false),
                    StreamPartitionReader.Parameters(preferResumable = false),
                )
            }
        }
    }
}
