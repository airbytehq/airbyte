/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.config

import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import kotlin.time.Duration
import kotlin.time.Duration.Companion.minutes

/**
 * This class configures the parallelism and the memory consumption for the dataflow job.
 * - maxConcurrentAggregates configures the number of ongoing aggregates.
 * - maxBufferedFlushes configures the number of aggregates being buffered if another flush is in
 * progress.
 * - maxEstBytesPerAgg configures the estimated size of each aggregate.
 * - The max memory consumption is (maxEstBytesPerAgg * maxConcurrentAggregates) +
 * (maxEstBytesPerAgg * 2). Example with default values: (70,000,000 * 5) + (70,000,000 * 2) =
 * 350,000,000 + 140,000,000 = 490,000,000 bytes (approx 0.49 GB).
 * - stalenessDeadlinePerAggMs is how long we will wait to flush an aggregate if it is not
 * fulfilling the requirement of entry count or max memory.
 * - maxRecordsPerAgg configures the max number of records in an aggregate.
 * - initConcurrentOperation configures the concurrency in the init phase
 */
data class MemoryAndParallelismConfig(
    val maxOpenAggregates: Int = 5,
    val maxBufferedAggregates: Int = 5,
    val stalenessDeadlinePerAgg: Duration = 5.minutes,
    val maxRecordsPerAgg: Long = 100_000L,
    val maxEstBytesPerAgg: Long = 70_000_000L,
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

@Factory
class MemoryAndParallelismConfigFactory {
    @Singleton @Secondary fun getMemoryAndParallelismConfig() = MemoryAndParallelismConfig()
}
