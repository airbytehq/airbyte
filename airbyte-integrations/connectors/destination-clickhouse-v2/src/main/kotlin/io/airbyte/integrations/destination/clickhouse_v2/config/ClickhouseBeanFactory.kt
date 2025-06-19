/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.config

import com.clickhouse.client.api.Client
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.orchestration.db.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.load.write.db.DbConstants.DEFAULT_INTERNAL_NAMESPACE
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfigurationFactory
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseSpecification
import io.micronaut.context.annotation.Factory
import jakarta.inject.Named
import jakarta.inject.Singleton

@Factory
class ClickhouseBeanFactory {

    @Singleton @Named("internalNamespace") fun internalNamespace() = DEFAULT_INTERNAL_NAMESPACE

    @Singleton
    fun clickhouseClient(config: ClickhouseConfiguration): Client {
        return Client.Builder()
            .addEndpoint(config.endpoint)
            .setUsername(config.username)
            .setPassword(config.password)
            .setDefaultDatabase(config.resolvedDatabase)
            .compressClientRequest(true)
            .build()
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
    fun tempTableNameGenerator(
        @Named("internalNamespace") namespace: String,
    ): TempTableNameGenerator = DefaultTempTableNameGenerator(namespace)
}
