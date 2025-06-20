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
        // We are not setting the default database here because the client is expecting that the
        // database exists.
        // That means that the database should be created before using this client which will make
        // the creation of the default to fail because it doesn't exist yet.
        // In order to solve this chicken-and-egg problem, we avoid to set a default db in the
        // client.
        // The default resolved database in ClickhouseConfiguration will be used as a namespace for
        // the table creation if not namespace is specified.
        return Client.Builder()
            .addEndpoint(config.endpoint)
            .setUsername(config.username)
            .setPassword(config.password)
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
