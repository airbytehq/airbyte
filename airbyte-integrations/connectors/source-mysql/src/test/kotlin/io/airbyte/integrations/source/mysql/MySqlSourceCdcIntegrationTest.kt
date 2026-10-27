/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.integrations.source.mysql.MySqlContainerFactory.execAsRoot
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import java.sql.Statement
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.assertDoesNotThrow
import org.testcontainers.containers.MySQLContainer

class MySqlSourceCdcIntegrationTest {

    @Test
    fun testCheck() {
        val run1: BufferingOutputConsumer = CliRunner.source("check", config(), null).run()

        assertEquals(1, run1.messages().size)
        assertEquals(
            AirbyteConnectionStatus.Status.SUCCEEDED,
            run1.messages().first().connectionStatus.status,
        )

        MySqlContainerFactory.exclusive(
                imageName = "mysql:9.2.0",
                MySqlContainerFactory.WithCdcOff,
            )
            .use { nonCdcDbContainer ->
                {
                    val invalidConfig: MySqlSourceConfigurationSpecification =
                        MySqlContainerFactory.config(nonCdcDbContainer).apply {
                            setIncrementalValue(Cdc())
                        }

                    val nonCdcConnectionFactory =
                        JdbcConnectionFactory(MySqlSourceConfigurationFactory().make(invalidConfig))

                    provisionTestContainer(nonCdcDbContainer, nonCdcConnectionFactory)

                    val run2: BufferingOutputConsumer =
                        CliRunner.source("check", invalidConfig, null).run()

                    val messageInRun2 =
                        run2
                            .messages()
                            .filter { it.type == AirbyteMessage.Type.CONNECTION_STATUS }
                            .first()

                    assertEquals(
                        AirbyteConnectionStatus.Status.FAILED,
                        messageInRun2.connectionStatus.status,
                    )
                }
            }
    }

    @Test
    fun test() {
        val state1 = CliRunner.source("read", config(), configuredCatalog).run().states().last()

        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { stmt: Statement ->
                stmt.execute("INSERT INTO test.tbl (k, v) VALUES (3, 'baz')")
            }
        }

        val run2InputState: List<AirbyteStateMessage> = listOf(state1)
        CliRunner.source("read", config(), configuredCatalog, run2InputState).run().records()
    }

    /**
     * Regression test for https://github.com/airbytehq/airbyte/issues/75558: a transaction
     * committed under a server UUID that the saved offset has never seen (what a failover, an
     * upgrade or a restore of a managed MySQL instance produces) made MySqlGtidSet.subtract() throw
     * a NullPointerException in Debezium before 3.4.3 (DBZ-9682), which the connector reported as
     * "Incumbent CDC state is invalid" on every subsequent sync.
     */
    @Test
    fun testResumesAfterGtidFromUnknownServerUuid() {
        val state1: AirbyteStateMessage =
            CliRunner.source("read", config(), configuredCatalog).run().states().last()

        // execAsRoot runs `mysql -e`, so the three statements share one session.
        dbContainer.execAsRoot(
            "SET @@SESSION.GTID_NEXT = '$FOREIGN_SERVER_UUID:1';" +
                "INSERT INTO test.tbl (k, v) VALUES (5, 'qux');" +
                "SET @@SESSION.GTID_NEXT = 'AUTOMATIC';",
        )

        // A failed read emits an ERROR trace and then run() throws ConnectorUncleanExitException.
        val run2: BufferingOutputConsumer = assertDoesNotThrow {
            CliRunner.source("read", config(), configuredCatalog, listOf(state1)).run()
        }
        val errorTraces: List<AirbyteTraceMessage> =
            run2.traces().filter { it.type == AirbyteTraceMessage.Type.ERROR }
        assertEquals(emptyList<AirbyteTraceMessage>(), errorTraces)
        val insertedRecords: List<AirbyteRecordMessage> =
            run2.records().filter { it.data["k"]?.asInt() == 5 }
        assertEquals(1, insertedRecords.size, "records: ${run2.records()}")
        assertEquals("qux", insertedRecords.first().data["v"].asText())
    }

    @Test
    fun testFullRefresh() {
        val fullRefreshCatalog = configuredCatalog.apply {
            streams.forEach { it.syncMode = SyncMode.FULL_REFRESH }
        }
        CliRunner.source("read", config(), fullRefreshCatalog).run()
        connectionFactory.get().use { connection: Connection ->
            connection.isReadOnly = false
            connection.createStatement().use { stmt: Statement ->
                stmt.execute("INSERT INTO test.tbl (k, v) VALUES (4, 'baz')")
            }
        }
    }

    companion object {
        val log = KotlinLogging.logger {}
        lateinit var dbContainer: MySQLContainer<*>

        /** A server UUID which no saved offset from [dbContainer] can have seen. */
        const val FOREIGN_SERVER_UUID = "11111111-2222-3333-4444-555555555555"

        fun config(): MySqlSourceConfigurationSpecification =
            MySqlContainerFactory.config(dbContainer).apply { setIncrementalValue(Cdc()) }

        val connectionFactory: JdbcConnectionFactory by lazy {
            JdbcConnectionFactory(MySqlSourceConfigurationFactory().make(config()))
        }

        val configuredCatalog: ConfiguredAirbyteCatalog by lazy {
            val desc = StreamDescriptor().withName("tbl").withNamespace("test")
            val discoveredStream =
                DiscoveredStream(
                    id = StreamIdentifier.Companion.from(desc),
                    columns =
                        listOf(EmittedField("k", IntFieldType), EmittedField("v", StringFieldType)),
                    primaryKeyColumnIDs = listOf(listOf("k")),
                )
            val stream: AirbyteStream =
                MySqlSourceOperations()
                    .create(
                        MySqlSourceConfigurationFactory().make(config()),
                        discoveredStream,
                    )
            val configuredStream: ConfiguredAirbyteStream =
                CatalogHelpers.toDefaultConfiguredStream(stream)
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withPrimaryKey(discoveredStream.primaryKeyColumnIDs)
                    .withCursorField(listOf(MySqlSourceCdcMetaFields.CDC_CURSOR.id))
            ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))
        }

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            dbContainer =
                MySqlContainerFactory.exclusive(
                    imageName = "mysql:9.2.0",
                    MySqlContainerFactory.WithNetwork,
                )
            provisionTestContainer(dbContainer, connectionFactory)
        }

        fun provisionTestContainer(
            targetContainer: MySQLContainer<*>,
            targetConnectionFactory: JdbcConnectionFactory,
        ) {
            val gtidOn =
                "SET @@GLOBAL.ENFORCE_GTID_CONSISTENCY = 'ON';" +
                    "SET @@GLOBAL.GTID_MODE = 'OFF_PERMISSIVE';" +
                    "SET @@GLOBAL.GTID_MODE = 'ON_PERMISSIVE';" +
                    "SET @@GLOBAL.GTID_MODE = 'ON';"
            val grant =
                "GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT " +
                    "ON *.* TO '${targetContainer.username}'@'%';"
            targetContainer.execAsRoot(gtidOn)
            targetContainer.execAsRoot(grant)
            targetContainer.execAsRoot("FLUSH PRIVILEGES;")

            targetConnectionFactory.get().use { connection: Connection ->
                connection.isReadOnly = false
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute("CREATE TABLE test.tbl(k INT PRIMARY KEY, v VARCHAR(80))")
                }
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute("INSERT INTO test.tbl (k, v) VALUES (1, 'foo'), (2, 'bar')")
                }
            }
        }
    }
}
