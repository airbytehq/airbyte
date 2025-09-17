/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats.socket

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.state.Histogram
import io.airbyte.cdk.load.dataflow.state.stats.EmissionStats
import io.airbyte.cdk.load.dataflow.state.stats.EmittedStatsStore
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/** Stores counts and bytes per stream. For stats emitter. */
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "SOCKET")
@Singleton
class EmittedStatsStoreImpl : EmittedStatsStore {
    private val readCounts = Histogram<DestinationStream.Descriptor>()

    private val readBytes = Histogram<DestinationStream.Descriptor>()

    override fun increment(
        s: DestinationStream.Descriptor,
        count: Long,
        bytes: Long,
    ) {
        readCounts.increment(s, count)
        readBytes.increment(s, bytes)
    }

    fun get(s: DestinationStream.Descriptor) =
        EmissionStats(
            count = readCounts.get(s) ?: 0,
            bytes = readBytes.get(s) ?: 0,
        )
}
