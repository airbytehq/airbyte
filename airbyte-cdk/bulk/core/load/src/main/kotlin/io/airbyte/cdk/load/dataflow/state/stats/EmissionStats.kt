/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state.stats

/** Simple record level stat data. Used for committed and emitted stats. */
data class EmissionStats(var count: Long = 0, var bytes: Long = 0) {
    fun merge(other: EmissionStats) =
        this.apply {
            count += other.count
            bytes += other.bytes
        }
}
