/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.config

import kotlin.time.Duration
import kotlin.time.Duration.Companion.minutes

/**
 * This class configures the parallelism and the memory consumption for the dataflow job.
 * - maxConcurrentAggregates configures the number of ongoing aggregates.
 * - maxBufferedFlushes configures the number of aggregates being buffered if another flush is in
 * progress.
 * - maxEstBytesPerAgg configures the estimated size of each aggregate.
 * - The max memory consumption is (maxEstBytesPerAgg * maxConcurrentAggregates) +
 * (maxEstBytesPerAgg * maxBufferedAggregates). Example with default values: (50,000,000 * 5) +
 * (50,000,000 * 3) = 300,000,000 + 150,000,000 = 450,000,000 bytes (approx 0.45 GB).
 * - stalenessDeadlinePerAggMs is how long we will wait to flush an aggregate if it is not
 * fulfilling the requirement of entry count or max memory.
 * - maxRecordsPerAgg configures the max number of records in an aggregate.
 * - initConcurrentOperation configures the concurrency in the init phase
 */
data class MemoryAndParallelismConfig(
    val maxOpenAggregates: Int = 5,
    val maxBufferedAggregates: Int = 3,
    val stalenessDeadlinePerAgg: Duration = 5.minutes,
    val maxRecordsPerAgg: Long = 100_000L,
    val maxEstBytesPerAgg: Long = 50_000_000L,
    val maxConcurrentLifecycleOperations: Int = 10,
) {
    init {
        require(maxOpenAggregates > 0) { "maxOpenAggregates must be greater than 0" }
        require(maxBufferedAggregates > 0) { "maxBufferedFlushes must be greater than 0" }
        require(maxRecordsPerAgg > 0) { "maxRecordsPerAgg must be greater than 0" }
        require(maxEstBytesPerAgg > 0) { "maxEstBytesPerAgg must be greater than 0" }
        require(maxConcurrentLifecycleOperations > 0) {
            "maxConcurrentLifecycleOperations must be greater than 0"
        }
    }
}
