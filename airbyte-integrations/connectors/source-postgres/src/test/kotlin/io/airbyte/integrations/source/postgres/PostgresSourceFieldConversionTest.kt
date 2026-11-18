/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.test.fixtures.connector.IntegrationTestOperations
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.postgres.config.CdcReplicationMethodConfigurationSpecification
import io.airbyte.integrations.source.postgres.config.EncryptionDisable
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationFactory
import io.airbyte.integrations.source.postgres.config.PostgresSourceConfigurationSpecification
import io.airbyte.integrations.source.postgres.config.StandardReplicationMethodConfigurationSpecification
import io.airbyte.integrations.source.postgres.legacy.PostgresTestDatabase
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import java.sql.Connection
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.PostgreSQLContainer

/**
 * Reads columns whose configured type is wider than their type in the database, with the
 * database type in `airbyte_source_type`, as the platform configures them after a narrowing type
 * change in the source.
 */
class PostgresSourceFieldConversionTest {

    @Test
    @Timeout(value = 300)
    fun testStandardRead() {
        val ops = IntegrationTestOperations(config(cdc = false))
        val catalog: ConfiguredAirbyteCatalog =
            widenedCatalog(ops.discover(), SyncMode.FULL_REFRESH)
        val output: BufferingOutputConsumer = ops.read(catalog)
        Assertions.assertEquals(listOf(EXPECTED_ROW_1), data(output))
    }

    @Test
    @Timeout(value = 300)
    fun testCdcRead() {
        val ops = IntegrationTestOperations(config(cdc = true))
        val catalog: ConfiguredAirbyteCatalog =
            widenedCatalog(ops.discover(), SyncMode.INCREMENTAL)

        // Sync 1: the initial snapshot.
        val sync1: BufferingOutputConsumer = ops.read(catalog)
        Assertions.assertEquals(listOf(EXPECTED_ROW_1), data(sync1))

        // Sync 2: a change read from the WAL.
        execute("INSERT INTO $SCHEMA.$TABLE VALUES (2, 789, '2024-05-06', false)")
        val sync2: BufferingOutputConsumer = ops.read(catalog, sync1.states())
        Assertions.assertEquals(listOf(EXPECTED_ROW_2), data(sync2))
    }

    /** The record data, without the CDC meta fields. */
    private fun data(output: BufferingOutputConsumer): List<JsonNode> =
        output
            .records()
            .filter { it.stream == TABLE }
            .map { record ->
                (record.data.deepCopy() as ObjectNode).apply {
                    remove(fieldNames().asSequence().filter { it.startsWith("_ab_") }.toList())
                }
            }

    private fun widenedCatalog(
        streams: Map<String, AirbyteStream>,
        syncMode: SyncMode,
    ): ConfiguredAirbyteCatalog {
        val stream: AirbyteStream = streams.getValue(TABLE)
        val properties = stream.jsonSchema["properties"] as ObjectNode
        properties.set<JsonNode>(
            "k",
            Jsons.readTree("""{"type": "string", "airbyte_source_type": "integer"}"""),
        )
        properties.set<JsonNode>(
            "d",
            Jsons.readTree(
                """{"type": "string", "format": "date-time",
                   |"airbyte_type": "timestamp_without_timezone", "airbyte_source_type": "date"}"""
                    .trimMargin(),
            ),
        )
        properties.set<JsonNode>(
            "b",
            Jsons.readTree("""{"type": "string", "airbyte_source_type": "boolean"}"""),
        )
        val configuredStream =
            CatalogHelpers.toDefaultConfiguredStream(stream)
                .withSyncMode(syncMode)
                .withDestinationSyncMode(DestinationSyncMode.APPEND)
                .withPrimaryKey(listOf(listOf("id")))
        return ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))
    }

    companion object {
        private const val SCHEMA = "public"
        private const val TABLE = "widened"

        val EXPECTED_ROW_1: JsonNode =
            Jsons.readTree("""{"id":1,"k":"456","d":"2024-01-02T00:00:00.000000","b":"true"}""")
        val EXPECTED_ROW_2: JsonNode =
            Jsons.readTree("""{"id":2,"k":"789","d":"2024-05-06T00:00:00.000000","b":"false"}""")

        private lateinit var testdb: PostgresTestDatabase

        fun config(cdc: Boolean): PostgresSourceConfigurationSpecification =
            PostgresSourceConfigurationSpecification().apply {
                host = testdb.container.host
                port = testdb.container.getMappedPort(PostgreSQLContainer.POSTGRESQL_PORT)
                username = testdb.container.username
                password = testdb.container.password
                jdbcUrlParams = ""
                encryptionJson = EncryptionDisable
                database = testdb.databaseName
                schemas = listOf(SCHEMA)
                checkpointTargetIntervalSeconds = 60
                maxDbConnections = 1
                setIncrementalConfigurationSpecificationValue(
                    if (cdc) {
                        CdcReplicationMethodConfigurationSpecification().apply {
                            replicationSlot = testdb.replicationSlotName!!
                            publication = testdb.publicationName!!
                            initialWaitingSeconds = 60
                        }
                    } else {
                        StandardReplicationMethodConfigurationSpecification
                    },
                )
            }

        private fun execute(sql: String) {
            JdbcConnectionFactory(PostgresSourceConfigurationFactory().make(config(cdc = false)))
                .get()
                .use { connection: Connection ->
                    connection.isReadOnly = false
                    connection.createStatement().use { it.execute(sql) }
                }
        }

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            testdb =
                PostgresTestDatabase.`in`(
                        PostgresTestDatabase.BaseImage.POSTGRES_17,
                        PostgresTestDatabase.ContainerModifier.WAL_LEVEL_LOGICAL,
                    )
                    .with(
                        "CREATE TABLE $SCHEMA.$TABLE " +
                            "(id bigint PRIMARY KEY, k integer, d date, b boolean);",
                    )
                    .with("INSERT INTO $SCHEMA.$TABLE VALUES (1, 456, '2024-01-02', true);")
                    .withReplicationSlot()
                    .withPublicationForAllTables()
        }

        @JvmStatic
        @AfterAll
        fun tearDown() {
            testdb.close()
        }
    }
}
