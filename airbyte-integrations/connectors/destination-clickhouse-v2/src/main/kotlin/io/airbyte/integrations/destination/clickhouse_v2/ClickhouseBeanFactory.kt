package io.airbyte.integrations.destination.clickhouse_v2

import com.clickhouse.client.api.Client
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DefaultDirectLoadTableSqlOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableWriter
import io.airbyte.cdk.load.orchestration.db.direct_load_table.migrations.DefaultDirectLoadTableTempTableNameMigration
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.integrations.destination.clickhouse_v2.spec.ClickhouseConfiguration
import io.airbyte.integrations.destination.clickhouse_v2.write.ClickhouseWriter
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickHouseDirectLoadSqlTableOperations
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoadDatabaseInitialStatusGatherer
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoadNativeTableOperations
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoadSqlGenerator
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoadTableExistenceChecker
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class ClickhouseBeanFactory {
    @Singleton
    fun destinationWriter(clickhouseClient: Client,
                          names: TableCatalog,
                          directLoader: ClickhouseDirectLoadNativeTableOperations,
                          sqlGenerator: ClickhouseDirectLoadSqlGenerator,
                          destinationHandler: ClickhouseDatabaseHandler,
                          streamStateStore: StreamStateStore<*>,
                          config: ClickhouseConfiguration,
                          existenceChecker: ClickhouseDirectLoadTableExistenceChecker,
    ): DestinationWriter {
        // This should be converter to a Bean
        val sqlTableOperations =  ClickHouseDirectLoadSqlTableOperations(
            DefaultDirectLoadTableSqlOperations(
                sqlGenerator,
                destinationHandler
            ),
            clickhouseClient
        )

        @Suppress("UNCHECKED_CAST")
        streamStateStore as StreamStateStore<DirectLoadTableExecutionConfig>
        return DirectLoadTableWriter(
            internalNamespace = "_internal",
            names = names,
            stateGatherer =
            ClickhouseDirectLoadDatabaseInitialStatusGatherer(
                clickhouseClient,
            ),
            destinationHandler = destinationHandler,
            nativeTableOperations = directLoader,
            sqlTableOperations = sqlTableOperations,
            streamStateStore = streamStateStore,
            directLoadTableTempTableNameMigration = null,
            // DefaultDirectLoadTableTempTableNameMigration(
            //     internalNamespace = config.resolvedDatabase,
            //     existenceChecker,
            //     sqlTableOperations,
            // ),
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
