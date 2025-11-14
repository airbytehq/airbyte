/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats.stdio

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.state.stats.EmittedStatsStore
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/** STDIO doesn't need to store emitted stats specially */
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "STDIO")
@Singleton
class NoopEmittedStatsStore : EmittedStatsStore {
    override fun increment(s: DestinationStream.Descriptor, count: Long, bytes: Long) = Unit

    override fun getStats() = null
}
