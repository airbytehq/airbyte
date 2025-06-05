package io.airbyte.integrations.destination.clickhouse_v2

import com.clickhouse.client.api.Client
import com.clickhouse.data.ClickHouseDataType
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseSpecification
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfigurationFactory
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoadDatabaseInitialStatusGatherer
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class ClickhouseBeanFactory {

    @Singleton
    fun tableStatusGatherer(
        airbyteClient: AirbyteClient,
        clickhouseConfiguration: ClickhouseConfiguration,
    ): DatabaseInitialStatusGatherer<DirectLoadInitialStatus> =
        ClickhouseDirectLoadDatabaseInitialStatusGatherer(
            airbyteClient,
            clickhouseConfiguration,
    )

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
        configFactory: ClickhouseConfigurationFactory,
        specFactory: ConfigurationSpecificationSupplier<ClickhouseSpecification>,
    ): ClickhouseConfiguration {
        val spec = specFactory.get()

        return configFactory.makeWithoutExceptionHandling(spec)
    }
}
