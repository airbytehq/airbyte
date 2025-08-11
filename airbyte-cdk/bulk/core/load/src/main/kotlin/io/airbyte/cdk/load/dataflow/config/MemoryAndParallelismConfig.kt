package io.airbyte.cdk.load.dataflow.config

import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import jakarta.inject.Named
import kotlin.time.Duration

@Singleton
class MemoryAndParallelismConfig(
    @Named("MaxConcurrentAggregates") val maxConcurrentAggregates: Int,
    @Named("MaxConcurrentFlushes") val maxConcurrentFlushes: Int,
    @Named("StalenessDeadlinePerAggMs") val stalenessDeadlinePerAggMs: Duration,
    @Named("MaxRecordsPerAgg") val maxRecordsPerAgg: Long,
    @Named("MaxEstBytesPerAgg") val maxEstBytesPerAgg: Long,
)

@Factory
class MemoryAndParallelismConfigFactory {
    @Singleton
    @Named("MaxConcurrentAggregates")
    fun maxConcurrentAggregates(): Int = 5

    @Singleton
    @Named("MaxConcurrentFlushes")
    fun maxConcurrentFlushes(): Int = 5

    @Singleton
    @Named("StalenessDeadlinePerAggMs")
    fun stalenessDeadlinePerAggMs(): Duration = Duration.parse("5m")

    @Singleton
    @Named("MaxRecordsPerAgg")
    fun maxRecordsPerAgg(): Long = 100_000L

    @Singleton
    @Named("MaxEstBytesPerAgg")
    fun maxEstBytesPerAgg(): Long = 70_000_000L
}
