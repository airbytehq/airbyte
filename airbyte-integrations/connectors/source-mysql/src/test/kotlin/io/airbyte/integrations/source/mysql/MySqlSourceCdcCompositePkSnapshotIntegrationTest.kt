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
import java.sql.Statement
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.MySQLContainer

/**
 * Regression test for the concurrent CDC initial snapshot of a table with a composite primary key.
 *
 * The concurrent partitions creator splits a large table into partitions bounded on the FIRST
 * primary key column only. The first partition must include its lower bound (the minimum value of
 * that column). Before the fix, the inclusive comparison was gated on the bound covering *every*
 * checkpoint column, so for composite keys the first partition was read with `pk0 > min` and every
 * row sharing the minimum first-column value was silently dropped.
 *
 * The table is kept small; partitioning is forced by lowering the expected throughput (and hence
 * the target partition byte size) through the JDBC constants property.
 */
class MySqlSourceCdcCompositePkSnapshotIntegrationTest {

    @Test
    @Timeout(value = 300)
    fun testInitialSnapshotReadsEveryRowOfCompositePkTable() {
        val output: BufferingOutputConsumer =
            CliRunner.source("read", config(), configuredCatalog).run()

        val records: List<AirbyteRecordMessage> = output.records()
        val keys: Set<Pair<Int, Int>> =
            records.map { it.data["id"].asInt() to it.data["sub"].asInt() }.toSet()

        // Every row is read exactly once, including the whole minimum-`id` group.
        assertEquals(NUM_IDS * NUM_SUBS, records.size, "unexpected record count")
        assertEquals(NUM_IDS * NUM_SUBS, keys.size, "duplicate records emitted")
        assertEquals(
            NUM_SUBS,
            records.count { it.data["id"].asInt() == 1 },
            "rows sharing the minimum first primary key column value were dropped",
        )
        assertEquals(
            NUM_SUBS,
            records.count { it.data["id"].asInt() == NUM_IDS },
            "rows sharing the maximum first primary key column value were dropped",
        )

        // Make sure the snapshot actually went through the concurrent partition split, otherwise
        // this test would pass vacuously with a single unsplit read. Each completed partition
        // checkpoints its upper bound as `pk_val` before the final "snapshot completed" state.
        val partialCheckpoints: Int =
            output.states().count { state: AirbyteStateMessage ->
                state.global?.streamStates?.any { streamState ->
                    streamState.streamState?.get("pk_val")?.let { !it.isNull } ?: false
                }
                    ?: false
            }
        assertTrue(
            partialCheckpoints >= 2,
            "expected the table to be read by several concurrent partitions, " +
                "but only $partialCheckpoints partition checkpoint(s) were emitted",
        )
    }

    companion object {
        val log = KotlinLogging.logger {}
        lateinit var dbContainer: MySQLContainer<*>

        const val NUM_IDS = 300
        const val NUM_SUBS = 100

        // 100 KiB/s with the 3s test checkpoint interval yields a ~300 KiB target partition size,
        // which is far below the DATA_LENGTH of the table created below (several MiB), so the
        // partitions creator splits the table into a few dozen partitions.
        private const val THROUGHPUT_PROPERTY =
            "airbyte.connector.extract.jdbc.expected-throughput-bytes-per-second"
        private const val THROUGHPUT_BYTES_PER_SECOND = "100000"

        fun config(): MySqlSourceConfigurationSpecification =
            MySqlContainerFactory.config(dbContainer).apply { setIncrementalValue(Cdc()) }

        val connectionFactory: JdbcConnectionFactory by lazy {
            JdbcConnectionFactory(MySqlSourceConfigurationFactory().make(config()))
        }

        val configuredCatalog: ConfiguredAirbyteCatalog by lazy {
            val desc = StreamDescriptor().withName("composite").withNamespace("test")
            val discoveredStream =
                DiscoveredStream(
                    id = StreamIdentifier.from(desc),
                    columns =
                        listOf(
                            EmittedField("id", IntFieldType),
                            EmittedField("sub", IntFieldType),
                            EmittedField("payload", StringFieldType),
                        ),
                    primaryKeyColumnIDs = listOf(listOf("id"), listOf("sub")),
                )
            val stream: AirbyteStream =
                MySqlSourceOperations()
                    .create(MySqlSourceConfigurationFactory().make(config()), discoveredStream)
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
            System.setProperty(THROUGHPUT_PROPERTY, THROUGHPUT_BYTES_PER_SECOND)
            dbContainer =
                MySqlContainerFactory.exclusive(
                    imageName = "mysql:9.2.0",
                    MySqlContainerFactory.WithNetwork,
                )
            dbContainer.execAsRoot(MySqlContainerFactory.WithCdc.GTID_ON)
            dbContainer.execAsRoot(MySqlContainerFactory.WithCdc.GRANT.format(dbContainer.username))
            dbContainer.execAsRoot("FLUSH PRIVILEGES;")

            connectionFactory.get().use { connection: Connection ->
                connection.isReadOnly = false
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute(
                        "CREATE TABLE test.composite (" +
                            "id INT NOT NULL, sub INT NOT NULL, payload VARCHAR(255), " +
                            "PRIMARY KEY (id, sub))"
                    )
                }
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute(
                        "INSERT INTO test.composite (id, sub, payload) " +
                            "WITH RECURSIVE ids AS (" +
                            "SELECT 1 AS n UNION ALL SELECT n + 1 FROM ids WHERE n < $NUM_IDS), " +
                            "subs AS (" +
                            "SELECT 1 AS n UNION ALL SELECT n + 1 FROM subs WHERE n < $NUM_SUBS) " +
                            "SELECT ids.n, subs.n, REPEAT('x', 200) FROM ids CROSS JOIN subs"
                    )
                }
                // Refresh InnoDB statistics so information_schema.TABLES.DATA_LENGTH, which the
                // concurrent partitions creator uses as its table size estimate, is populated.
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute("ANALYZE TABLE test.composite")
                }
                connection.createStatement().use { stmt: Statement ->
                    stmt
                        .executeQuery(
                            "SELECT DATA_LENGTH FROM information_schema.TABLES " +
                                "WHERE TABLE_SCHEMA = 'test' AND TABLE_NAME = 'composite'"
                        )
                        .use { rs ->
                            assertTrue(rs.next())
                            val dataLength: Long = rs.getLong(1)
                            log.info { "test.composite DATA_LENGTH = $dataLength" }
                            assertTrue(
                                dataLength > 3 * THROUGHPUT_BYTES_PER_SECOND.toLong(),
                                "table too small to be split into concurrent partitions",
                            )
                        }
                }
            }
        }

        @JvmStatic
        @AfterAll
        fun clearProperties() {
            System.clearProperty(THROUGHPUT_PROPERTY)
        }
    }
}
