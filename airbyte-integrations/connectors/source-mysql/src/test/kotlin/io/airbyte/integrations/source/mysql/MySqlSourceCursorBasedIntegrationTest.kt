/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
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
import org.testcontainers.containers.MySQLContainer

class MySqlSourceCursorBasedIntegrationTest {

    @BeforeEach
    fun resetTable() {
        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { stmt: Statement ->
                stmt.execute("DELETE FROM test.$tableName")
            }
            connection.createStatement().use { stmt: Statement ->
                stmt.execute("INSERT INTO test.$tableName (k, v) VALUES (10, 'foo'), (20, 'bar')")
            }
        }
    }

    @Test
    fun testCursorBasedRead() {
        val run1: BufferingOutputConsumer =
            CliRunner.source("read", config, getConfiguredCatalog()).run()

        val lastStateMessageFromRun1 = run1.states().last()
        val lastStreamStateFromRun1 = lastStateMessageFromRun1.stream.streamState

        assertEquals("20", lastStreamStateFromRun1.get("cursor").textValue())
        assertEquals(2, lastStreamStateFromRun1.get("version").intValue())
        assertEquals("cursor_based", lastStreamStateFromRun1.get("state_type").asText())
        assertEquals(tableName, lastStreamStateFromRun1.get("stream_name").asText())
        assertEquals(listOf("k"), lastStreamStateFromRun1.get("cursor_field").map { it.asText() })
        assertEquals("test", lastStreamStateFromRun1.get("stream_namespace").asText())
        assertEquals(0, lastStreamStateFromRun1.get("cursor_record_count").asInt())

        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { stmt: Statement ->
                stmt.execute("INSERT INTO test.$tableName (k, v) VALUES (3, 'baz-ignore')")
                stmt.execute("INSERT INTO test.$tableName (k, v) VALUES (13, 'baz-ignore')")
                stmt.execute("INSERT INTO test.$tableName (k, v) VALUES (30, 'baz')")
            }
        }

        val run2InputState: List<AirbyteStateMessage> = listOf(lastStateMessageFromRun1)
        val run2: BufferingOutputConsumer =
            CliRunner.source("read", config, getConfiguredCatalog(), run2InputState).run()
        val recordMessageFromRun2: List<AirbyteRecordMessage> = run2.records()
        assertEquals(recordMessageFromRun2.size, 1)
    }

    @Test
    fun testWithV1State() {
        var state: AirbyteStateMessage = Jsons.readValue(V1_STATE, AirbyteStateMessage::class.java)
        val run1: BufferingOutputConsumer =
            CliRunner.source("read", config, getConfiguredCatalog(), listOf(state)).run()
        val recordMessageFromRun1: List<AirbyteRecordMessage> = run1.records()
        assertEquals(recordMessageFromRun1.size, 1)
    }

    @Test
    fun testWithV1StateEmptyCursor() {
        var state: AirbyteStateMessage =
            Jsons.readValue(V1_STATE_EMPTY_CURSOR, AirbyteStateMessage::class.java)
        val run1: BufferingOutputConsumer =
            CliRunner.source("read", config, getConfiguredCatalog(), listOf(state)).run()
        val recordMessageFromRun1: List<AirbyteRecordMessage> = run1.records()
        assertEquals(recordMessageFromRun1.size, 2)
    }

    @Test
    fun testWithFullRefresh() {
        val fullRefreshCatalog =
            getConfiguredCatalog().apply { streams[0].syncMode = SyncMode.FULL_REFRESH }
        val run1: BufferingOutputConsumer =
            CliRunner.source("read", config, fullRefreshCatalog).run()
        val recordMessageFromRun1: List<AirbyteRecordMessage> = run1.records()
        assertEquals(recordMessageFromRun1.size, 2)
        val lastStateMessageFromRun1 = run1.states().last()

        val run2: BufferingOutputConsumer =
            CliRunner.source("read", config, fullRefreshCatalog, listOf(lastStateMessageFromRun1))
                .run()
        val recordMessageFromRun2: List<AirbyteRecordMessage> = run2.records()
        assertEquals(recordMessageFromRun2.size, 0)
    }

    @Test
    fun testWithFullRefreshWithEmptyTable() {
        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { stmt: Statement ->
                stmt.execute("DELETE FROM test.$tableName")
            }
        }

        val fullRefreshCatalog =
            getConfiguredCatalog().apply { streams[0].syncMode = SyncMode.FULL_REFRESH }
        val run1: BufferingOutputConsumer =
            CliRunner.source("read", config, fullRefreshCatalog).run()

        assertTrue(run1.states().isEmpty())
        assertTrue(run1.records().isEmpty())

        val run2: BufferingOutputConsumer =
            CliRunner.source("read", config, fullRefreshCatalog).run()
        assertTrue(run2.states().isEmpty())
        assertTrue(run2.records().isEmpty())
    }

    @Test
    fun testCursorBasedReadWithEmptyTable() {
        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { stmt: Statement ->
                stmt.execute("DELETE FROM test.$tableName")
            }
        }

        val run1: BufferingOutputConsumer =
            CliRunner.source("read", config, getConfiguredCatalog()).run()

        assertTrue(run1.states().isEmpty())
        assertTrue(run1.records().isEmpty())

        val run2: BufferingOutputConsumer =
            CliRunner.source("read", config, getConfiguredCatalog()).run()
        assertTrue(run2.states().isEmpty())
        assertTrue(run2.records().isEmpty())
    }

    @Test
    fun testCursorBasedViewRead() {
        provisionView(connectionFactory)
        val catalog = getConfiguredCatalog()
        catalog.streams[0].stream.name = viewName
        val run1: BufferingOutputConsumer = CliRunner.source("read", config, catalog).run()
        val lastStateMessageFromRun1 = run1.states().last()
        val lastStreamStateFromRun1 = lastStateMessageFromRun1.stream.streamState

        assertEquals("20", lastStreamStateFromRun1.get("cursor").textValue())
        assertEquals(2, lastStreamStateFromRun1.get("version").intValue())
        assertEquals("cursor_based", lastStreamStateFromRun1.get("state_type").asText())
        assertEquals(viewName, lastStreamStateFromRun1.get("stream_name").asText())
        assertEquals(listOf("k"), lastStreamStateFromRun1.get("cursor_field").map { it.asText() })
        assertEquals("test", lastStreamStateFromRun1.get("stream_namespace").asText())
        assertEquals(0, lastStreamStateFromRun1.get("cursor_record_count").asInt())
    }

    companion object {
        val log = KotlinLogging.logger {}
        val dbContainer: MySQLContainer<*> = MySqlContainerFactory.shared(imageName = "mysql:8.0")

        val config: MySqlSourceConfigurationSpecification =
            MySqlContainerFactory.config(dbContainer)

        val connectionFactory: JdbcConnectionFactory by lazy {
            JdbcConnectionFactory(MySqlSourceConfigurationFactory().make(config))
        }

        fun getConfiguredCatalog(): ConfiguredAirbyteCatalog {
            val desc = StreamDescriptor().withName(tableName).withNamespace("test")
            val discoveredStream =
                DiscoveredStream(
                    id = StreamIdentifier.Companion.from(desc),
                    columns = listOf(Field("k", IntFieldType), Field("v", StringFieldType)),
                    primaryKeyColumnIDs = listOf(listOf("k")),
                )
            val stream: AirbyteStream =
                MySqlSourceOperations()
                    .create(
                        MySqlSourceConfigurationFactory().make(config),
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
            tableName = (1..8).map { ('a'..'z').random() }.joinToString("")

            targetConnectionFactory.get().use { connection: Connection ->
                connection.isReadOnly = false
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute("CREATE TABLE test.$tableName(k INT PRIMARY KEY, v VARCHAR(80))")
                }
            }
        }

        lateinit var viewName: String
        fun provisionView(targetConnectionFactory: JdbcConnectionFactory) {
            viewName = "$tableName-view"
            targetConnectionFactory.get().use { connection: Connection ->
                connection.isReadOnly = false
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute("CREATE VIEW test.`$viewName` AS SELECT * FROM test.`$tableName`")
                }
            }
        }
    }
    val V1_STATE: String =
        """  
      {
        "type": "STREAM",
        "stream": {
            "stream_descriptor": {
              "name": "$tableName",
              "namespace": "test"
            },
            "stream_state": {
              "cursor": "10",
              "version": 2,
              "state_type": "cursor_based",
              "stream_name": "$tableName",
              "cursor_field": [
                "k"
              ],
              "stream_namespace": "test",
              "cursor_record_count": 1
            }
        }
    }
    """

    // Legacy mysql connector saved the following state for an empty table in user cursor mode
    val V1_STATE_EMPTY_CURSOR: String =
        """  
      {
        "type": "STREAM",
        "stream": {
            "stream_descriptor": {
              "name": "$tableName",
              "namespace": "test"
            },
            "stream_state": {
              "version": 2,
              "state_type": "cursor_based",
              "stream_name": "$tableName",
              "cursor_field": [
                "k"
              ],
              "stream_namespace": "test",
              "cursor_record_count": 1
            }
        }
    }
    """
}
