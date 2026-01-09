/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres_v2

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import java.sql.Statement
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.PostgreSQLContainer

/**
 * Integration tests for Xmin-based incremental sync mode.
 *
 * Note: The current implementation configures Xmin mode but still requires a user-defined cursor.
 * Full Xmin support would automatically use PostgreSQL's xmin system column as the cursor,
 * which would detect all inserts and updates without requiring a user-specified cursor column.
 *
 * These tests verify that the Xmin configuration works and that incremental syncs function
 * correctly when a cursor is specified alongside Xmin mode.
 */
class PostgresV2SourceXminIntegrationTest {

    @BeforeEach
    fun resetTable() {
        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { stmt: Statement ->
                stmt.execute("DELETE FROM $tableName")
            }
            connection.createStatement().use { stmt: Statement ->
                stmt.execute("INSERT INTO $tableName (k, v) VALUES (10, 'foo'), (20, 'bar')")
            }
        }
    }

    @Test
    fun testXminConfigurationWithFullRefresh() {
        val fullRefreshCatalog =
            getConfiguredCatalog().apply { streams[0].syncMode = SyncMode.FULL_REFRESH }
        val run1: BufferingOutputConsumer =
            CliRunner.source("read", xminConfig, fullRefreshCatalog).run()
        val recordsFromRun1: List<AirbyteRecordMessage> = run1.records()

        assertEquals(2, recordsFromRun1.size, "Should read 2 records with Xmin config")

        val recordValues = recordsFromRun1.map { it.data.get("v").asText() }.sorted()
        assertEquals(listOf("bar", "foo"), recordValues)
    }

    @Test
    fun testXminConfigurationWithIncrementalRead() {
        // First read - should get all records
        val run1: BufferingOutputConsumer =
            CliRunner.source("read", xminConfig, getConfiguredCatalog()).run()

        val recordsFromRun1: List<AirbyteRecordMessage> = run1.records()
        assertEquals(2, recordsFromRun1.size, "Should read 2 records in first run")

        val lastStateMessageFromRun1 = run1.states().last()
        val lastStreamStateFromRun1 = lastStateMessageFromRun1.stream.streamState

        // State should be cursor_based (current implementation)
        assertEquals("cursor_based", lastStreamStateFromRun1.get("state_type").asText())
        assertEquals("20", lastStreamStateFromRun1.get("cursor").textValue())

        // Insert new data after first read
        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { stmt: Statement ->
                stmt.execute("INSERT INTO $tableName (k, v) VALUES (100, 'new-record')")
            }
        }

        // Second read with state - should only get new record
        val run2InputState: List<AirbyteStateMessage> = listOf(lastStateMessageFromRun1)
        val run2: BufferingOutputConsumer =
            CliRunner.source("read", xminConfig, getConfiguredCatalog(), run2InputState).run()
        val recordsFromRun2: List<AirbyteRecordMessage> = run2.records()

        assertEquals(1, recordsFromRun2.size, "Should only read 1 new record")
        assertEquals("new-record", recordsFromRun2[0].data.get("v").asText())
    }

    @Test
    fun testXminConfigurationWithEmptyTable() {
        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { stmt: Statement ->
                stmt.execute("DELETE FROM $tableName")
            }
        }

        val run1: BufferingOutputConsumer =
            CliRunner.source("read", xminConfig, getConfiguredCatalog()).run()

        assertTrue(run1.records().isEmpty(), "Should have no records for empty table")
    }

    @Test
    fun testXminSystemColumnExists() {
        // Verify that the xmin system column is accessible in PostgreSQL
        // This validates that future full Xmin support can query this column
        connectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { stmt: Statement ->
                val rs = stmt.executeQuery("SELECT xmin, k, v FROM $tableName ORDER BY k")
                var count = 0
                while (rs.next()) {
                    val xmin = rs.getLong("xmin")
                    assertTrue(xmin > 0, "xmin should be a positive transaction ID")
                    count++
                }
                assertEquals(2, count, "Should read 2 rows with xmin column")
            }
        }
    }

    companion object {
        val log = KotlinLogging.logger {}
        val dbContainer: PostgreSQLContainer<*> =
            PostgresContainerFactory.shared(imageName = "postgres:15-alpine")

        // Configuration with Xmin incremental mode
        val xminConfig: PostgresV2SourceConfigurationSpecification =
            PostgresV2SourceConfigurationSpecification().apply {
                host = dbContainer.host
                port = dbContainer.getMappedPort(PostgreSQLContainer.POSTGRESQL_PORT)
                username = dbContainer.username
                password = dbContainer.password
                database = dbContainer.databaseName
                schemas = listOf("public")
                checkpointTargetIntervalSeconds = 60
                concurrency = 1
                setIncrementalValue(Xmin) // Use Xmin mode
            }

        val connectionFactory: JdbcConnectionFactory by lazy {
            JdbcConnectionFactory(PostgresV2SourceConfigurationFactory().make(xminConfig))
        }

        fun getConfiguredCatalog(): ConfiguredAirbyteCatalog {
            val desc = StreamDescriptor().withName(tableName).withNamespace("public")
            val discoveredStream =
                DiscoveredStream(
                    id = StreamIdentifier.Companion.from(desc),
                    columns = listOf(Field("k", IntFieldType), Field("v", StringFieldType)),
                    primaryKeyColumnIDs = listOf(listOf("k")),
                )
            val stream: AirbyteStream =
                PostgresV2SourceOperations()
                    .create(
                        PostgresV2SourceConfigurationFactory().make(xminConfig),
                        discoveredStream,
                    )
            val configuredStream: ConfiguredAirbyteStream =
                CatalogHelpers.toDefaultConfiguredStream(stream)
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withPrimaryKey(discoveredStream.primaryKeyColumnIDs)
                    .withCursorField(listOf("k"))
            return ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))
        }

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            provisionTestContainer(connectionFactory)
        }

        lateinit var tableName: String

        fun provisionTestContainer(targetConnectionFactory: JdbcConnectionFactory) {
            tableName = "test_xmin_" + (1..8).map { ('a'..'z').random() }.joinToString("")

            targetConnectionFactory.get().use { connection: Connection ->
                connection.isReadOnly = false
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute("CREATE TABLE $tableName (k INTEGER PRIMARY KEY, v VARCHAR(80))")
                }
            }
        }
    }
}
