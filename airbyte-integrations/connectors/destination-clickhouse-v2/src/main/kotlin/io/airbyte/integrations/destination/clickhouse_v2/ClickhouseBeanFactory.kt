package io.airbyte.integrations.destination.clickhouse_v2

import com.clickhouse.client.api.Client
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickHouseSpecification
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfigurationFactory
import io.airbyte.integrations.destination.clickhouse_v2.write.ClickhouseWriter
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class ClickhouseBeanFactory {
    @Singleton
    fun destinationWriter(): DestinationWriter {
        return ClickhouseWriter()
    }

    @Singleton
    fun clickhouseClient(config: ClickhouseConfiguration): Client {
        log.error { config }
        return Client.Builder()
            .addEndpoint(config.endpoint)
            .setUsername(config.username)
            .setPassword(config.password)
            .setDefaultDatabase(config.resolvedDatabase)
            .build()
    }

    @Singleton
    fun clickhouseConfiguration(factory: ClickhouseConfigurationFactory,
                                specs: ClickHouseSpecification): ClickhouseConfiguration {
        return factory.makeWithoutExceptionHandling(specs)
    }
}
