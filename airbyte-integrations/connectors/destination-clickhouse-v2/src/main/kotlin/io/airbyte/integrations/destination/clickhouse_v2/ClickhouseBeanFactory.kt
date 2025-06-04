package io.airbyte.integrations.destination.clickhouse_v2

import com.clickhouse.client.api.Client
import com.clickhouse.data.ClickHouseDataType
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableWriter
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseSpecification
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfigurationFactory
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoadSqlTableOperations
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoadDatabaseInitialStatusGatherer
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoadNativeTableOperations
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoadSqlGenerator
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class ClickhouseBeanFactory {

    @Singleton
    fun clickhouseDirectLoadSqlTableOperations(
        sqlGenerator: ClickhouseDirectLoadSqlGenerator,
        destinationHandler: ClickhouseDatabaseHandler,
    ): DirectLoadTableSqlOperations = ClickhouseDirectLoadSqlTableOperations(
        sqlGenerator,
        destinationHandler,
    )

    @Singleton
    fun stateGatherer(airbyteClient: AirbyteClient<ClickHouseDataType>,
                      clickhouseConfiguration: ClickhouseConfiguration): DatabaseInitialStatusGatherer<DirectLoadInitialStatus> =
        ClickhouseDirectLoadDatabaseInitialStatusGatherer(
            airbyteClient,
            clickhouseConfiguration,
    )

    @Singleton
    fun destinationWriter(
        names: TableCatalog,
        stateGatherer: DatabaseInitialStatusGatherer<DirectLoadInitialStatus>,
        directLoader: ClickhouseDirectLoadNativeTableOperations,
        directLoadTableSqlOperations: DirectLoadTableSqlOperations,
        destinationHandler: ClickhouseDatabaseHandler,
        streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    ): DestinationWriter {
        return DirectLoadTableWriter(
            // TODO: get the internal namespace from the configuration
            internalNamespace = "airbyte_internal",
            names = names,
            stateGatherer = stateGatherer,
            destinationHandler = destinationHandler,
            nativeTableOperations = directLoader,
            sqlTableOperations = directLoadTableSqlOperations,
            streamStateStore = streamStateStore,
            directLoadTableTempTableNameMigration = null,
        )
    }

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
