/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres_v2

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.DiscoveredStream
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.StringFieldType
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
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.PostgreSQLContainer

/**
 * Integration tests for CDC (Change Data Capture) using PostgreSQL's logical replication.
 *
 * These tests verify that the connector can be configured for CDC mode with:
 * - wal_level=logical
 * - A replication slot with pgoutput plugin
 * - A publication for the tables being synced
 */
class PostgresV2SourceCdcIntegrationTest {

    @Test
    fun testCdcConfigurationIsValid() {
        // Verify that CDC configuration is correctly parsed
        val config = PostgresContainerFactory.cdcConfig(dbContainer, REPLICATION_SLOT, PUBLICATION)

        val parsedConfig = PostgresV2SourceConfigurationFactory().make(config)

        assertTrue(parsedConfig.global, "CDC mode should enable global state")
        assertTrue(
            parsedConfig.incrementalConfiguration is CdcIncrementalConfiguration,
            "Should be CDC incremental configuration"
        )

        val cdcConfig = parsedConfig.incrementalConfiguration as CdcIncrementalConfiguration
        assertEquals(REPLICATION_SLOT, cdcConfig.replicationSlot)
        assertEquals(PUBLICATION, cdcConfig.publication)
    }

    @Test
    fun testCdcReplicationSlotExists() {
        // Verify that the replication slot was created and is accessible
        connectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { stmt: Statement ->
                val rs =
                    stmt.executeQuery(
                        """
                    SELECT slot_name, plugin, slot_type, database
                    FROM pg_replication_slots
                    WHERE slot_name = '$REPLICATION_SLOT'
                """.trimIndent()
                    )

                assertTrue(rs.next(), "Replication slot should exist")
                assertEquals(REPLICATION_SLOT, rs.getString("slot_name"))
                assertEquals("pgoutput", rs.getString("plugin"))
                assertEquals("logical", rs.getString("slot_type"))
            }
        }
    }

    @Test
    fun testCdcPublicationExists() {
        // Verify that the publication was created
        connectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { stmt: Statement ->
                val rs =
                    stmt.executeQuery(
                        """
                    SELECT pubname FROM pg_publication WHERE pubname = '$PUBLICATION'
                """.trimIndent()
                    )

                assertTrue(rs.next(), "Publication should exist")
                assertEquals(PUBLICATION, rs.getString("pubname"))
            }
        }
    }

    @Test
    fun testCdcTableInPublication() {
        // Verify that the test table is included in the publication
        connectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { stmt: Statement ->
                val rs =
                    stmt.executeQuery(
                        """
                    SELECT schemaname, tablename
                    FROM pg_publication_tables
                    WHERE pubname = '$PUBLICATION' AND tablename = '$tableName'
                """.trimIndent()
                    )

                assertTrue(rs.next(), "Table should be in publication")
                assertEquals("public", rs.getString("schemaname"))
                assertEquals(tableName, rs.getString("tablename"))
            }
        }
    }

    @Test
    fun testWalLevelIsLogical() {
        // Verify that wal_level is set to logical (required for CDC)
        connectionFactory.get().use { connection: Connection ->
            connection.createStatement().use { stmt: Statement ->
                val rs = stmt.executeQuery("SHOW wal_level")

                assertTrue(rs.next(), "Should get wal_level")
                assertEquals("logical", rs.getString("wal_level"))
            }
        }
    }

    @Test
    fun testCdcPositionParsing() {
        // Test LSN parsing and formatting
        val lsnString = "0/16B3748"
        val position = PostgresV2SourceCdcPosition.fromLsnString(lsnString)

        assertEquals(lsnString, position.lsnString)
        assertTrue(position.lsn > 0, "LSN should be positive")

        // Test round-trip
        val position2 = PostgresV2SourceCdcPosition.fromLsn(position.lsn)
        assertEquals(position.lsn, position2.lsn)
        assertEquals(position.lsnString, position2.lsnString)
    }

    @Test
    fun testCdcPositionComparison() {
        val pos1 = PostgresV2SourceCdcPosition.fromLsnString("0/100")
        val pos2 = PostgresV2SourceCdcPosition.fromLsnString("0/200")
        val pos3 = PostgresV2SourceCdcPosition.fromLsnString("1/100")

        assertTrue(pos1 < pos2, "pos1 should be less than pos2")
        assertTrue(pos2 < pos3, "pos2 should be less than pos3")
        assertTrue(pos1 < pos3, "pos1 should be less than pos3")
    }

    @Test
    fun testCdcMetaFieldsInCdcMode() {
        // Verify that CDC meta fields are returned when in CDC mode
        val cdcConfig =
            PostgresContainerFactory.cdcConfig(dbContainer, REPLICATION_SLOT, PUBLICATION)
        val parsedConfig = PostgresV2SourceConfigurationFactory().make(cdcConfig)
        val operations = PostgresV2SourceOperations(parsedConfig)

        val metaFields = operations.globalMetaFields
        assertTrue(metaFields.isNotEmpty(), "CDC mode should have meta fields")

        val metaFieldIds = metaFields.map { it.id }
        assertTrue("_ab_cdc_updated_at" in metaFieldIds, "Should have _ab_cdc_updated_at")
        assertTrue("_ab_cdc_deleted_at" in metaFieldIds, "Should have _ab_cdc_deleted_at")
        assertTrue("_ab_cdc_lsn" in metaFieldIds, "Should have _ab_cdc_lsn")
        assertTrue("_ab_cdc_cursor" in metaFieldIds, "Should have _ab_cdc_cursor")
    }

    @Test
    fun testNonCdcModeHasNoMetaFields() {
        // Verify that non-CDC mode doesn't have CDC meta fields
        val config = PostgresContainerFactory.config(dbContainer)
        val parsedConfig = PostgresV2SourceConfigurationFactory().make(config)
        val operations = PostgresV2SourceOperations(parsedConfig)

        val metaFields = operations.globalMetaFields
        assertTrue(metaFields.isEmpty(), "Non-CDC mode should not have CDC meta fields")
    }

    companion object {
        val log = KotlinLogging.logger {}

        const val REPLICATION_SLOT = "airbyte_test_slot"
        const val PUBLICATION = "airbyte_test_publication"

        // Use a dedicated CDC-enabled container
        val dbContainer: PostgreSQLContainer<*> =
            PostgresContainerFactory.shared(
                imageName = "postgres:15-alpine",
                PostgresContainerFactory.WithCdc
            )

        val cdcConfig: PostgresV2SourceConfigurationSpecification by lazy {
            PostgresContainerFactory.cdcConfig(dbContainer, REPLICATION_SLOT, PUBLICATION)
        }

        val connectionFactory: JdbcConnectionFactory by lazy {
            JdbcConnectionFactory(PostgresV2SourceConfigurationFactory().make(cdcConfig))
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
                        PostgresV2SourceConfigurationFactory().make(cdcConfig),
                        discoveredStream,
                    )
            val configuredStream: ConfiguredAirbyteStream =
                CatalogHelpers.toDefaultConfiguredStream(stream)
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withPrimaryKey(discoveredStream.primaryKeyColumnIDs)
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
            tableName = "test_cdc_" + (1..8).map { ('a'..'z').random() }.joinToString("")

            targetConnectionFactory.get().use { connection: Connection ->
                connection.isReadOnly = false

                // Grant replication permission to the user
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute("ALTER ROLE ${dbContainer.username} WITH REPLICATION")
                }

                // Create the test table
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute("CREATE TABLE $tableName (k INTEGER PRIMARY KEY, v VARCHAR(80))")
                }

                // Create the publication for the test table
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute("CREATE PUBLICATION $PUBLICATION FOR TABLE $tableName")
                }

                // Create the logical replication slot
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute(
                        "SELECT pg_create_logical_replication_slot('$REPLICATION_SLOT', 'pgoutput')"
                    )
                }

                // Insert initial test data
                connection.createStatement().use { stmt: Statement ->
                    stmt.execute("INSERT INTO $tableName (k, v) VALUES (1, 'initial')")
                }
            }
        }
    }
}
