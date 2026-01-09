/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres_v2

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
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

class PostgresV2SourceCursorBasedIntegrationTest {

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
    fun testFullRefreshRead() {
        val fullRefreshCatalog =
            getConfiguredCatalog().apply { streams[0].syncMode = SyncMode.FULL_REFRESH }
        val run1: BufferingOutputConsumer =
            CliRunner.source("read", config, fullRefreshCatalog).run()
        val recordsFromRun1: List<AirbyteRecordMessage> = run1.records()

        assertEquals(2, recordsFromRun1.size, "Should read 2 records")

        // Verify record content
        val recordValues = recordsFromRun1.map { it.data.get("v").asText() }.sorted()
        assertEquals(listOf("bar", "foo"), recordValues)
    }

    @Test
    fun testCursorBasedRead() {
        val run1: BufferingOutputConsumer =
            CliRunner.source("read", config, getConfiguredCatalog()).run()

        val recordsFromRun1: List<AirbyteRecordMessage> = run1.records()
        assertEquals(2, recordsFromRun1.size, "Should read 2 records in first run")

        val lastStateMessageFromRun1 = run1.states().last()
        val lastStreamStateFromRun1 = lastStateMessageFromRun1.stream.streamState

        assertEquals("20", lastStreamStateFromRun1.get("cursor").textValue())
        assertEquals("cursor_based", lastStreamStateFromRun1.get("state_type").asText())
        assertEquals(tableName, lastStreamStateFromRun1.get("stream_name").asText())
        assertEquals(listOf("k"), lastStreamStateFromRun1.get("cursor_field").map { it.asText() })
        assertEquals("public", lastStreamStateFromRun1.get("stream_namespace").asText())

        // Insert new data after first read
        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { stmt: Statement ->
                stmt.execute(
                    "INSERT INTO $tableName (k, v) VALUES (5, 'baz-ignore')"
                ) // Below cursor, should be ignored
                stmt.execute(
                    "INSERT INTO $tableName (k, v) VALUES (15, 'baz-ignore')"
                ) // Below cursor, should be ignored
                stmt.execute(
                    "INSERT INTO $tableName (k, v) VALUES (100, 'baz')"
                ) // Above cursor, should be read
            }
        }

        // Run incremental read with state from first run
        val run2InputState: List<AirbyteStateMessage> = listOf(lastStateMessageFromRun1)
        val run2: BufferingOutputConsumer =
            CliRunner.source("read", config, getConfiguredCatalog(), run2InputState).run()
        val recordsFromRun2: List<AirbyteRecordMessage> = run2.records()

        assertEquals(1, recordsFromRun2.size, "Should only read 1 new record above cursor")
        assertEquals("baz", recordsFromRun2[0].data.get("v").asText())

        val lastStateMessageFromRun2 = run2.states().last()
        val lastStreamStateFromRun2 = lastStateMessageFromRun2.stream.streamState
        assertEquals("100", lastStreamStateFromRun2.get("cursor").textValue())
    }

    @Test
    fun testFullRefreshWithEmptyTable() {
        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { stmt: Statement ->
                stmt.execute("DELETE FROM $tableName")
            }
        }

        val fullRefreshCatalog =
            getConfiguredCatalog().apply { streams[0].syncMode = SyncMode.FULL_REFRESH }
        val run1: BufferingOutputConsumer =
            CliRunner.source("read", config, fullRefreshCatalog).run()

        assertTrue(run1.records().isEmpty(), "Should have no records for empty table")
    }

    @Test
    fun testCursorBasedReadWithEmptyTable() {
        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { stmt: Statement ->
                stmt.execute("DELETE FROM $tableName")
            }
        }

        val run1: BufferingOutputConsumer =
            CliRunner.source("read", config, getConfiguredCatalog()).run()

        assertTrue(run1.records().isEmpty(), "Should have no records for empty table")
    }

    companion object {
        val log = KotlinLogging.logger {}
        val dbContainer: PostgreSQLContainer<*> =
            PostgresContainerFactory.shared(imageName = "postgres:15-alpine")

        val config: PostgresV2SourceConfigurationSpecification =
            PostgresContainerFactory.config(dbContainer)

        val connectionFactory: JdbcConnectionFactory by lazy {
            JdbcConnectionFactory(PostgresV2SourceConfigurationFactory().make(config))
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
                        PostgresV2SourceConfigurationFactory().make(config),
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
            tableName = "test_" + (1..8).map { ('a'..'z').random() }.joinToString("")

            targetConnectionFactory.get().use { connection: Connection ->
                connection.isReadOnly = false
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute("CREATE TABLE $tableName (k INTEGER PRIMARY KEY, v VARCHAR(80))")
                }
            }
        }
    }
}
