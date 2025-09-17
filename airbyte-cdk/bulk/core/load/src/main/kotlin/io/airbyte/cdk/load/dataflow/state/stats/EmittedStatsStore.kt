/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats

import io.airbyte.cdk.load.command.DestinationStream

/** tallies "emitted" record and byte counts from records on read */
interface EmittedStatsStore {
    fun increment(
        s: DestinationStream.Descriptor,
        count: Long,
        bytes: Long,
    )
}
