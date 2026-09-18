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
import java.sql.ResultSet
import java.sql.Statement
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.MySQLContainer

/**
 * End-to-end CDC coverage for servers whose `gtid_executed` contains tagged GTIDs.
 *
 * MySQL 8.4 allows a GTID to carry a tag (WL#15294), e.g. `<uuid>:mysqlsh:1-42`. InnoDB Cluster
 * emits these for AdminAPI operations and, once present, they stay in `gtid_executed` forever.
 * [MySqlSourceDebeziumOperations] feeds `gtid_executed` and `gtid_purged` to Debezium's GTID set
 * parser to decide whether a saved CDC position is still valid, so a parser that cannot read tags
 * fails every single sync against such a server.
 *
 * [MySqlSourceTaggedGtidTest] pins the parser behavior itself; this test pins the behavior of an
 * actual sync against an actual server that has emitted a tagged GTID. The tag is produced with
 * `SET @@SESSION.GTID_NEXT = 'AUTOMATIC:<tag>'`, which makes every subsequently auto-generated GTID
 * of that session carry the tag, without needing an InnoDB Cluster to reproduce it.
 *
 * See https://github.com/airbytehq/airbyte/issues/85846.
 */
class MySqlSourceTaggedGtidIntegrationTest {

    @Test
    @Timeout(value = 300)
    fun testCdcSyncAgainstTaggedGtidServer() {
        // Guard against a vacuous test: the server must really be in the broken-before state.
        assertTrue(
            gtidExecuted().contains(":$GTID_TAG:"),
            "expected a tagged GTID in gtid_executed, got '${gtidExecuted()}'",
        )

        val run1: BufferingOutputConsumer =
            CliRunner.source("read", config(), configuredCatalog).run()
        assertEquals(
            emptyList<String>(),
            run1.traces().filter { it.error != null }.map { it.error.internalMessage },
        )
        assertEquals(listOf(1, 2), run1.records().map { it.k() }.sorted())
        val state1: AirbyteStateMessage = run1.states().last()

        // Keep emitting tagged GTIDs while the connector is between syncs: the incremental read
        // has to both resume from the tagged position and parse the ones added since.
        dbContainer.execAsRoot(
            "SET @@SESSION.GTID_NEXT = 'AUTOMATIC:$GTID_TAG';" +
                "INSERT INTO test.tbl (k, v) VALUES (3, 'baz');" +
                "SET @@SESSION.GTID_NEXT = 'AUTOMATIC';",
        )

        val run2InputState: List<AirbyteStateMessage> = listOf(state1)
        val run2: BufferingOutputConsumer =
            CliRunner.source("read", config(), configuredCatalog, run2InputState).run()
        assertEquals(
            emptyList<String>(),
            run2.traces().filter { it.error != null }.map { it.error.internalMessage },
        )
        assertEquals(listOf(3), run2.records().map { it.k() })
        assertTrue(gtidExecuted().contains(":$GTID_TAG:"))
    }

    companion object {
        val log = KotlinLogging.logger {}
        lateinit var dbContainer: MySQLContainer<*>

        const val GTID_TAG = "airbyte"

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
                    MySqlContainerFactory.WithCdc,
                )
            connectionFactory.get().use { connection: Connection ->
                connection.isReadOnly = false
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute("CREATE TABLE test.tbl(k INT PRIMARY KEY, v VARCHAR(80))")
                }
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute("INSERT INTO test.tbl (k, v) VALUES (1, 'foo'), (2, 'bar')")
                }
            }
            // The untagged transactions above plus this tagged one give the mixed
            // '<uuid>:1-N:<tag>:1-M' shape that an InnoDB Cluster member reports.
            dbContainer.execAsRoot(
                "SET @@SESSION.GTID_NEXT = 'AUTOMATIC:$GTID_TAG';" +
                    "CREATE TABLE test.tagged_marker(k INT PRIMARY KEY);" +
                    "SET @@SESSION.GTID_NEXT = 'AUTOMATIC';",
            )
            log.info { "gtid_executed after provisioning: ${gtidExecuted()}" }
        }

        fun gtidExecuted(): String =
            connectionFactory.get().use { connection: Connection ->
                connection.createStatement().use { stmt: Statement ->
                    stmt.executeQuery("SELECT @@GLOBAL.GTID_EXECUTED").use { rs: ResultSet ->
                        rs.next()
                        // MySQL wraps long GTID sets, the tag delimiters do not survive otherwise.
                        rs.getString(1).replace("\n", "")
                    }
                }
            }

        fun AirbyteRecordMessage.k(): Int = data["k"].asInt()
    }
}
