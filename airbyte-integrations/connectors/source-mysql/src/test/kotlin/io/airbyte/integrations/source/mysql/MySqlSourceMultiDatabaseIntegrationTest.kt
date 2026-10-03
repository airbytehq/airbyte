/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.ConnectorUncleanExitException
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.integrations.source.mysql.MySqlContainerFactory.execAsRoot
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.SyncMode
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.assertThrows
import org.testcontainers.containers.MySQLContainer

/** One CDC connection reading tables from several databases via `table_include_regex`. */
class MySqlSourceMultiDatabaseIntegrationTest {

    @Test
    fun testCheck() {
        val output: BufferingOutputConsumer = CliRunner.source("check", regexConfig()).run()
        assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, output.statuses().single().status)
    }

    @Test
    fun testDiscover() {
        val streams: Set<String> =
            discover(regexConfig()).map { "${it.namespace}.${it.name}" }.toSet()
        assertEquals(setOf("db_a.orders", "db_a.order_items", "db_b.orders"), streams)
    }

    @Test
    fun testCdcAcrossDatabases() {
        val config = regexConfig()
        val catalog = cdcCatalog(discover(config))

        val run1: BufferingOutputConsumer = CliRunner.source("read", config, catalog).run()
        assertEquals(
            mapOf("db_a.orders" to 2, "db_a.order_items" to 1, "db_b.orders" to 2),
            countByStream(run1),
        )

        execute(
            "INSERT INTO db_a.orders (id, v) VALUES (3, 'a3')",
            "INSERT INTO db_b.orders (id, v) VALUES (3, 'b3')",
            "INSERT INTO other.orders (id, v) VALUES (3, 'x3')",
        )
        val state: List<AirbyteStateMessage> = listOf(run1.states().last())
        val run2: BufferingOutputConsumer = CliRunner.source("read", config, catalog, state).run()
        val newRecords: Map<String, List<String>> =
            run2.records().groupBy({ "${it.namespace}.${it.stream}" }, { it.data["v"].asText() })
        assertEquals(listOf("a3"), newRecords["db_a.orders"])
        assertEquals(listOf("b3"), newRecords["db_b.orders"])
        assertTrue("other.orders" !in newRecords)
    }

    @Test
    fun testSwitchingToRegexInvalidatesNarrowSchemaHistory() {
        // State from a single-database connection only has schema history for db_a.
        val singleDbConfig = cdcConfig().apply { database = "db_a" }
        val singleDbCatalog = cdcCatalog(discover(singleDbConfig))
        val state = CliRunner.source("read", singleDbConfig, singleDbCatalog).run().states().last()

        val regexConfig = regexConfig().apply { database = "db_a" }
        val run2 =
            CliRunner.source("read", regexConfig, cdcCatalog(discover(regexConfig)), listOf(state))
        assertThrows<ConnectorUncleanExitException> { run2.run() }
        val errors: String = run2.results.traces().mapNotNull { it.error?.message }.joinToString()
        assertTrue(errors.contains("does not cover database(s) [db_b]"), errors)
    }

    companion object {
        lateinit var dbContainer: MySQLContainer<*>

        fun cdcConfig(): MySqlSourceConfigurationSpecification =
            MySqlContainerFactory.config(dbContainer).apply { setIncrementalValue(Cdc()) }

        fun regexConfig(): MySqlSourceConfigurationSpecification =
            cdcConfig().apply {
                database = null
                tableIncludeRegex = listOf("db_a\\..*", "db_b\\.orders")
            }

        fun discover(config: MySqlSourceConfigurationSpecification): List<AirbyteStream> =
            CliRunner.source("discover", config).run().catalogs().single().streams

        fun cdcCatalog(streams: List<AirbyteStream>): ConfiguredAirbyteCatalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    streams.map {
                        CatalogHelpers.toDefaultConfiguredStream(it)
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withPrimaryKey(it.sourceDefinedPrimaryKey)
                            .withCursorField(listOf(MySqlSourceCdcMetaFields.CDC_CURSOR.id))
                    }
                )

        fun countByStream(output: BufferingOutputConsumer): Map<String, Int> =
            output.records().groupingBy { "${it.namespace}.${it.stream}" }.eachCount()

        /** Runs as root: the CDC test user only has SELECT and replication privileges. */
        fun execute(vararg sql: String) {
            for (statement in sql) {
                dbContainer.execAsRoot(statement)
            }
        }

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            dbContainer =
                MySqlContainerFactory.exclusive(
                    imageName = "mysql:9.2.0",
                    MySqlContainerFactory.WithNetwork,
                    MySqlContainerFactory.WithCdc,
                )
            execute(
                "CREATE DATABASE db_a",
                "CREATE DATABASE db_b",
                "CREATE DATABASE other",
                "CREATE TABLE db_a.orders (id INT PRIMARY KEY, v VARCHAR(80))",
                "CREATE TABLE db_a.order_items (id INT PRIMARY KEY, v VARCHAR(80))",
                "CREATE TABLE db_b.orders (id INT PRIMARY KEY, v VARCHAR(80))",
                "CREATE TABLE db_b.customers (id INT PRIMARY KEY, v VARCHAR(80))",
                "CREATE TABLE other.orders (id INT PRIMARY KEY, v VARCHAR(80))",
                "INSERT INTO db_a.orders (id, v) VALUES (1, 'a1'), (2, 'a2')",
                "INSERT INTO db_a.order_items (id, v) VALUES (1, 'i1')",
                "INSERT INTO db_b.orders (id, v) VALUES (1, 'b1'), (2, 'b2')",
                "INSERT INTO db_b.customers (id, v) VALUES (1, 'c1')",
                "INSERT INTO other.orders (id, v) VALUES (1, 'x1')",
            )
        }
    }
}
