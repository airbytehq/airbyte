// Copyright (c) 2025 Airbyte, Inc., all rights reserved.

package io.airbyte.cdk.test.fixtures.tests

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.JdbcAirbyteStreamFactory
import io.airbyte.cdk.jdbc.BigIntegerFieldType
import io.airbyte.cdk.jdbc.LocalDateTimeFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.test.fixtures.cleanup.TestAssetResourceNamer
import io.airbyte.cdk.test.fixtures.connector.ColumnDefinition
import io.airbyte.cdk.test.fixtures.connector.ColumnType
import io.airbyte.cdk.test.fixtures.connector.SqlDialect
import io.airbyte.cdk.test.fixtures.connector.TableDefinition
import io.airbyte.cdk.test.fixtures.connector.TestDbExecutor
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import kotlin.collections.iterator
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.TestInstance

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
abstract class BaseConnectorTest(
    val testDbExecutor: TestDbExecutor,
    private val testAssetResourceNamer: TestAssetResourceNamer
) {

    private val log = KotlinLogging.logger {}

    protected abstract val sqlDialect: SqlDialect
    protected abstract val streamFactory: JdbcAirbyteStreamFactory
    protected abstract val configFactory:
        SourceConfigurationFactory<ConfigurationSpecification, SourceConfiguration>
    protected abstract var config: ConfigurationSpecification
    protected val namespaces: MutableList<String> = mutableListOf()
    protected val tables: MutableMap<String, MutableList<TableDefinition>> = mutableMapOf()

    @AfterAll
    fun disconnectDatabase() {
        try {
            testDbExecutor.close()
        } catch (e: Exception) {
            log.warn(e) { "Error while disconnecting from test ." }
        }
    }

    @BeforeEach
    fun setupPerTestMethodData() {
        setupNamespaces()
        setupTablesForAllNamespaces()
        setupTestData()
    }

    @AfterEach
    fun tearDownPerTestMethodData() {
        tables.clear()
        namespaces.clear()
    }

    protected abstract fun setupTestData()

    protected abstract fun cleanupTestData()

    protected open fun setupNamespaces(num: Int = 1) {
        for (i in 1..num) {
            val namespace = testAssetResourceNamer.getName()
            namespaces.add(namespace)
            testDbExecutor.executeUpdate(sqlDialect.buildCreateNamespaceQuery(namespace))
        }
    }

    protected fun dropCurrentNamespaces() {
        for (namespace in namespaces) {
            testDbExecutor.executeUpdate(sqlDialect.buildDropNamespaceQuery(namespace))
        }
    }

    protected open fun setupTablesForAllNamespaces(num: Int = 1) {
        for (namespace in namespaces) {
            for (i in 1..num) {
                val tableName = testAssetResourceNamer.getName()
                val colId =
                    ColumnDefinition(
                        name = "id",
                        type = ColumnType.BIGINT,
                        jdbcType = BigIntegerFieldType,
                        isPrimaryKey = true,
                        isNullable = false,
                    )
                val colName =
                    ColumnDefinition(
                        name = "name",
                        type = ColumnType.VARCHAR,
                        jdbcType = StringFieldType,
                        length = 255,
                        isNullable = false,
                    )
                val colCreatedAt =
                    ColumnDefinition(
                        name = "created_at",
                        type = ColumnType.TIMESTAMP,
                        jdbcType = LocalDateTimeFieldType,
                        isNullable = false,
                        defaultValue = "CURRENT_TIMESTAMP",
                    )
                val table =
                    TableDefinition(
                        tableName = tableName,
                        columns = listOf(colId, colName, colCreatedAt),
                        namespace = namespace,
                    )
                tables.putIfAbsent(namespace, mutableListOf())
                tables[namespace]!!.add(table)
                testDbExecutor.executeUpdate(sqlDialect.buildCreateTableQuery(table))
            }
        }
    }

    protected fun dropCurrentTables() {
        for ((namespace, tableList) in tables) {
            for (table in tableList) {
                testDbExecutor.executeUpdate(
                    sqlDialect.buildDropTableQuery(namespace, table.tableName),
                )
            }
        }
    }

    fun performReadOperation(catalog: ConfiguredAirbyteCatalog): BufferingOutputConsumer =
        CliRunner.source("read", config, catalog).run()

    fun getConfiguredStream(
        table: TableDefinition,
        syncMode: SyncMode,
    ): ConfiguredAirbyteStream {
        val desc = StreamDescriptor().withName(table.tableName).withNamespace(table.namespace)
        val discoveredStream =
            DiscoveredStream(
                id = StreamIdentifier.from(desc),
                columns = table.columns.map { Field(it.name, it.jdbcType) },
                primaryKeyColumnIDs =
                    table.columns
                        .filter { it.isPrimaryKey }
                        .map {
                            listOf(
                                it.name,
                            )
                        },
            )
        val sourceConfig: SourceConfiguration = configFactory.make(config)
        val stream: AirbyteStream = streamFactory.create(sourceConfig, discoveredStream)
        return CatalogHelpers.toDefaultConfiguredStream(stream)
            .withSyncMode(syncMode)
            .withPrimaryKey(discoveredStream.primaryKeyColumnIDs)
    }

    fun getConfiguredCatalog(
        syncMode: SyncMode,
    ): ConfiguredAirbyteCatalog {
        val configuredStreams =
            tables.values.flatMap { tableList ->
                tableList.map { getConfiguredStream(it, syncMode) }
            }
        return ConfiguredAirbyteCatalog().withStreams(configuredStreams)
    }
}
