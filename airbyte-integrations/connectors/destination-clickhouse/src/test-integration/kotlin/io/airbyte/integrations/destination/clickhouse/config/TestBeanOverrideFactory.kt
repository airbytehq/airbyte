package io.airbyte.integrations.destination.clickhouse.config

import io.airbyte.cdk.load.dataflow.config.MemoryAndParallelismConfig
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton

@Factory
@Requires(env = [Environment.TEST])
class TestBeanOverrideFactory {
    @Singleton
    @Primary
    fun testConfig() = MemoryAndParallelismConfig(
        // Set this to 1 so we flush aggregates immediately for easier testing.
        maxRecordsPerAgg = 1,
    )
}
