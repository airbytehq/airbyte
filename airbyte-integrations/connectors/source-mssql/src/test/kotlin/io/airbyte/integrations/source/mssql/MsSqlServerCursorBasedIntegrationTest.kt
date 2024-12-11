/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mssql.config_spec.MsSqlServerSourceConfigurationSpecification
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
import kotlin.test.assertEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

class MsSqlServerCursorBasedIntegrationTest {

    @Test
    fun testCursorBasedRead() {
        val run1: BufferingOutputConsumer =
            CliRunner.source("read", config, getConfiguredCatalog()).run()

        val lastStateMessageFromRun1 = run1.states().last()
        val lastStreamStateFromRun1 = lastStateMessageFromRun1.stream.streamState
        println("SGX lastStreamStateFromRun1=$lastStreamStateFromRun1")

        assertEquals("20", lastStreamStateFromRun1.get("cursor").textValue())
        assertEquals(2, lastStreamStateFromRun1.get("version").intValue())
        assertEquals("cursor_based", lastStreamStateFromRun1.get("state_type").asText())
        assertEquals(tableName, lastStreamStateFromRun1.get("stream_name").asText())
        assertEquals(listOf("k"), lastStreamStateFromRun1.get("cursor_field").map { it.asText() })
        assertEquals(
            dbContainer.schemaName,
            lastStreamStateFromRun1.get("stream_namespace").asText()
        )
        assertEquals(0, lastStreamStateFromRun1.get("cursor_record_count").asInt())

        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { stmt: Statement ->
                stmt.execute(
                    "INSERT INTO ${dbContainer.schemaName}.$tableName (k, v) VALUES (3, 'baz-ignore')"
                )
                stmt.execute(
                    "INSERT INTO ${dbContainer.schemaName}.$tableName (k, v) VALUES (13, 'baz-ignore')"
                )
                stmt.execute(
                    "INSERT INTO ${dbContainer.schemaName}.$tableName (k, v) VALUES (30, 'baz')"
                )
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
        val recordMessagesFromRun1: List<AirbyteRecordMessage> = run1.records()
        assertEquals(
            actual = recordMessagesFromRun1.size,
            expected = 1,
            message = recordMessagesFromRun1.toString()
        )
    }

    @Test
    fun testWithFullRefresh() {
        val fullRefreshCatalog =
            getConfiguredCatalog().apply { streams[0].syncMode = SyncMode.FULL_REFRESH }
        log.info { "SGX running connector. Run1" }
        val run1: BufferingOutputConsumer =
            CliRunner.source("read", config, fullRefreshCatalog).run()
        val recordMessageFromRun1: List<AirbyteRecordMessage> = run1.records()
        assertEquals(3, recordMessageFromRun1.size, recordMessageFromRun1.toString())
        val lastStateMessageFromRun1 = run1.states().last()

        log.info { "SGX running connector. Run2" }
        val run2: BufferingOutputConsumer =
            CliRunner.source("read", config, fullRefreshCatalog, listOf(lastStateMessageFromRun1))
                .run()
        val recordMessageFromRun2: List<AirbyteRecordMessage> = run2.records()
        assertEquals(recordMessageFromRun2.size, 0)
    }

    companion object {
        val log = KotlinLogging.logger {}
        val dbContainer: MsSqlServercontainer =
            MsSqlServerContainerFactory.shared(MsSqlServerImage.SQLSERVER_2022)

        val config: MsSqlServerSourceConfigurationSpecification =
            dbContainer.config

        val connectionFactory: JdbcConnectionFactory by lazy {
            JdbcConnectionFactory(MsSqlServerSourceConfigurationFactory().make(config))
        }

        fun getConfiguredCatalog(): ConfiguredAirbyteCatalog {
            val desc = StreamDescriptor().withName(tableName).withNamespace(dbContainer.schemaName)
            val discoveredStream =
                DiscoveredStream(
                    id = StreamIdentifier.Companion.from(desc),
                    columns = listOf(Field("k", IntFieldType), Field("v", StringFieldType)),
                    primaryKeyColumnIDs = listOf(listOf("k")),
                )
            val stream: AirbyteStream = MsSqlServerStreamFactory().createGlobal(discoveredStream)
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
                    stmt.execute(
                        "CREATE TABLE ${dbContainer.schemaName}.$tableName(k INT PRIMARY KEY, v VARCHAR(80))"
                    )
                }
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute(
                        "INSERT INTO ${dbContainer.schemaName}.$tableName (k, v) VALUES (5, 'abc'), (10, 'foo'), (20, 'bar')"
                    )
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
              "name": "${tableName}",
              "namespace": "${dbContainer.schemaName}"
            },
            "stream_state": {
              "cursor": "10",
              "version": 2,
              "state_type": "cursor_based",
              "stream_name": "${tableName}",
              "cursor_field": [
                "k"
              ],
              "stream_namespace": "${dbContainer.schemaName}",
              "cursor_record_count": 1
            }
        }
    }
    """
}
