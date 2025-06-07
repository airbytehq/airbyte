package io.airbyte.integrations.destination.clickhouse_v2.config

import com.clickhouse.client.api.Client
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.write.db.DbConstants.DEFAULT_INTERNAL_NAMESPACE
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseSpecification
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import io.micronaut.context.annotation.Factory
import jakarta.inject.Named
import jakarta.inject.Singleton

@Factory
class ClickhouseBeanFactory {

    @Singleton
    @Named("internalNamespace")
    fun internalNamespace() = DEFAULT_INTERNAL_NAMESPACE

    @Singleton
    fun clickhouseClient(config: ClickhouseConfiguration): Client {
        return Client.Builder()
            .addEndpoint(config.endpoint)
            .setUsername(config.username)
            .setPassword(config.password)
            .setDefaultDatabase(config.resolvedDatabase)
            .build()
    }

    @Singleton
    fun clickhouseConfiguration(
        specFactory: ConfigurationSpecificationSupplier<ClickhouseSpecification>,
    ): ClickhouseConfiguration {
        val spec = specFactory.get()

        return ClickhouseConfiguration(
            spec.hostname,
            spec.port,
            spec.protocol.value,
            spec.database,
            spec.username,
            spec.password,
        )
    }
}
