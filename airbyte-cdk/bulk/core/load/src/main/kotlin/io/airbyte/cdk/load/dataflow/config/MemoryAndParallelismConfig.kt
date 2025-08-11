package io.airbyte.cdk.load.dataflow.config

import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import jakarta.inject.Named
import kotlin.time.Duration

/**
 * This class configures the parallelism and the memory consumption for the dataflow job.
 * - maxConcurrentAggregates configures the number of ongoing aggregates.
 * - maxConcurrentFlushes configures the number of concurrent flushes.
 * - maxEstBytesPerAgg configures the estimated size of each aggregate.
 * - The max memory consumption is (maxEstBytesPerAgg * maxConcurrentAggregates) + (maxEstBytesPerAgg * maxConcurrentFlushes).
 *   Example with default values: (70,000,000 * 5) + (70,000,000 * 5) = 350,000,000 + 350,000,000 = 700,000,000 bytes (approx 0.7 GB).
 * - stalenessDeadlinePerAggMs is how long we will wait to flush an aggregate if it is not fulfilling the requirement of entry count or max memory.
 * - maxRecordsPerAgg configures the max number of records in an aggregate.
 */

data class MemoryAndParallelismConfig(
    val maxConcurrentAggregates: Int = 5,
    val maxConcurrentFlushes: Int = 5,
    val stalenessDeadlinePerAggMs: Duration = Duration.parse("5m"),
    val maxRecordsPerAgg: Long = 100_000L,
    val maxEstBytesPerAgg: Long = 70_000_000L,
)

@Factory
class MemoryAndParallelismConfigFactory {
    @Singleton
    fun getMemoryAndParallelismConfig() = MemoryAndParallelismConfig()
}
