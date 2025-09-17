/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats.stdio

import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.state.stats.StateStatsEnricher
import io.airbyte.cdk.load.message.CheckpointMessage
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

/** STDIO doesn't need to enrich state stats */
@Requires(property = "airbyte.destination.core.data-channel.medium", value = "STDIO")
@Singleton
class NoopStateStatsEnricher : StateStatsEnricher {
    override fun enrich(msg: CheckpointMessage, ps: List<PartitionKey>) = msg
}
