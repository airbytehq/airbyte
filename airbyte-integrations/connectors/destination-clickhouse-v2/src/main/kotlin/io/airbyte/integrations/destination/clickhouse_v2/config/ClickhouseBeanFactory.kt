/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.config

import com.clickhouse.client.api.Client
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.orchestration.db.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfigurationFactory
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseSpecification
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class ClickhouseBeanFactory {
    @Singleton
    fun clickhouseClient(config: ClickhouseConfiguration): Client {

        val clientWithDb =
            Client.Builder()
                .addEndpoint(config.endpoint)
                .setUsername(config.username)
                .setPassword(config.password)
                .setDefaultDatabase(config.resolvedDatabase)
                .compressClientRequest(true)
                .build()

        return if (clientWithDb.ping()) {
            clientWithDb
        } else {
            // We don't set the default database here because the client expects that database
            // to already exist during instantiation. If we instantiate the client with a default
            // database that does not exist, it will hard fail.

            // In order to solve this chicken-and-egg problem, we avoid setting the default db on
            // the client.
            // Instead, we resolve the default database in the ClickhouseConfiguration, which is
            // used for table creation when the stream descriptor does not specificy a namespace
            // directly.
            Client.Builder()
                .addEndpoint(config.endpoint)
                .setUsername(config.username)
                .setPassword(config.password)
                .compressClientRequest(true)
                .build()
        }
    }

    @Singleton
    fun clickhouseConfiguration(
        configFactory: ClickhouseConfigurationFactory,
        specFactory: ConfigurationSpecificationSupplier<ClickhouseSpecification>,
    ): ClickhouseConfiguration {
        val spec = specFactory.get()

        return configFactory.makeWithoutExceptionHandling(spec)
    }

    @Singleton
    fun tempTableNameGenerator(): TempTableNameGenerator = DefaultTempTableNameGenerator()
}
