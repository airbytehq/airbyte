/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats

import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.message.CheckpointMessage

/** enriches state messages with stats necessary for bookkeeping */
interface StateStatsEnricher {
    fun enrich(msg: CheckpointMessage, ps: List<PartitionKey>): CheckpointMessage
}
