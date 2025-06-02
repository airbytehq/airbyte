package io.airbyte.integrations.destination.clickhouse_v2

import com.clickhouse.client.api.Client
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableWriter
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse_v2.write.ClickhouseWriter
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickHouseDirectLoadSqlTableOperations
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoadDatabaseInitialStatusGatherer
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoadNativeTableOperations
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoadSqlGenerator
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class ClickhouseBeanFactory {

    @Singleton
    fun clickhouseDirectLoadSqlTableOperations(
        clickhouseClient: Client,
        sqlGenerator: ClickhouseDirectLoadSqlGenerator,
        destinationHandler: ClickhouseDatabaseHandler,
    ): DirectLoadTableSqlOperations = ClickhouseDirectLoadSqlTableOperations(
        clickhouseClient,
        sqlGenerator,
        destinationHandler,
    )

    @Singleton
    fun stateGatherer(clickhouseClient: Client) = ClickhouseDirectLoadDatabaseInitialStatusGatherer(
        clickhouseClient,
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
            internalNamespace = "_internal",
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
}
