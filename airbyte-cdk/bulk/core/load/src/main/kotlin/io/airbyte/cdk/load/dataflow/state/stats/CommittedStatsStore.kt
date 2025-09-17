/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.state.PartitionHistogram

/** tallies "committed" record and byte counts from histograms on aggregate flush */
interface CommittedStatsStore {
    fun acceptStats(
        s: DestinationStream.Descriptor,
        flushed: PartitionHistogram,
        bytes: PartitionHistogram,
    )
}
