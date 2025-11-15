/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb_v2.config

import com.mongodb.ConnectionString
import com.mongodb.MongoClientSettings
import com.mongodb.kotlin.client.coroutine.MongoClient
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.dataflow.config.AggregatePublishingConfig
import io.airbyte.cdk.load.orchestration.db.BaseDirectLoadInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class MongodbBeanFactory {
    @Singleton
    fun mongoClient(config: MongodbConfiguration): MongoClient {
        val connectionString = ConnectionString(config.connectionString)
        val settings = MongoClientSettings.builder()
            .applyConnectionString(connectionString)
            .applicationName("airbyte-v2")
            .build()

        return MongoClient.create(settings)
    }

    @Singleton
    fun mongodbConfiguration(
        configFactory: MongodbConfigurationFactory,
        specSupplier: ConfigurationSpecificationSupplier<MongodbSpecification>,
    ): MongodbConfiguration {
        return configFactory.make(specSupplier.get())
    }

    @Singleton
    fun tempTableNameGenerator(): TempTableNameGenerator {
        return DefaultTempTableNameGenerator()
    }

    @Singleton
    fun initialStatusGatherer(
        client: TableOperationsClient,
        tempTableNameGenerator: TempTableNameGenerator,
    ): DatabaseInitialStatusGatherer<DirectLoadInitialStatus> {
        return object : BaseDirectLoadInitialStatusGatherer(client, tempTableNameGenerator) {}
    }

    @Singleton
    fun aggregatePublishingConfig(dataChannelMedium: DataChannelMedium): AggregatePublishingConfig {
        // Different settings for STDIO vs SOCKET mode
        return if (dataChannelMedium == DataChannelMedium.STDIO) {
            AggregatePublishingConfig(
                maxRecordsPerAgg = 10_000_000_000_000L,
                maxEstBytesPerAgg = 350_000_000L,
                maxEstBytesAllAggregates = 350_000_000L * 5,
            )
        } else {
            // SOCKET mode (faster IPC)
            AggregatePublishingConfig(
                maxRecordsPerAgg = 10_000_000_000_000L,
                maxEstBytesPerAgg = 350_000_000L,
                maxEstBytesAllAggregates = 350_000_000L * 5,
                maxBufferedAggregates = 6,
            )
        }
    }
}
