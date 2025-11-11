/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import io.airbyte.cdk.load.dataflow.config.AggregatePublishingConfig
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class SnowflakeBeanFactory {
    @Singleton
    fun aggregatePublishingConfig(): AggregatePublishingConfig {
        // NOT speed mode
        return AggregatePublishingConfig(
            maxRecordsPerAgg = 100_000L,
            maxEstBytesPerAgg = 50_000_000L,
            maxEstBytesAllAggregates = 250_000_000L,
            maxBufferedAggregates = 5,
        )
    }
}
