/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.test.source

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.Feed
import io.airbyte.cdk.read.Global
import io.airbyte.cdk.read.StateQuerier
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.stream.StreamPartitionReader
import io.airbyte.cdk.read.stream.StreamPartitionsCreator
import io.airbyte.cdk.read.stream.StreamReadContext
import io.airbyte.cdk.read.stream.StreamReadContextManager
import io.airbyte.cdk.read.stream.streamPartitionsCreatorInput
import io.airbyte.cdk.source.CreateNoPartitions
import io.airbyte.cdk.source.PartitionsCreator
import io.airbyte.cdk.source.PartitionsCreatorFactory
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
