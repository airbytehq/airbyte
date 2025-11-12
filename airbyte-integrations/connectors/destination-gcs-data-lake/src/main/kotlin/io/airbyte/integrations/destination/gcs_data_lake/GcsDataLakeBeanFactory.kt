/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import io.airbyte.cdk.load.dataflow.config.AggregatePublishingConfig
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class GcsDataLakeBeanFactory {
    @Singleton
    fun aggregatePublishingConfig(): AggregatePublishingConfig {
        // NOT speed mode
        return AggregatePublishingConfig(
            maxRecordsPerAgg = 10_000_000_000L,
            maxEstBytesPerAgg = 150_000_000L,
            maxEstBytesAllAggregates = 150_000_000L * 5,
            maxBufferedAggregates = 5,
        )
    }
}
