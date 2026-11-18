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
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
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

// TK-TODO: NEVER MERGE THIS FILE. Local-only test of the Bulk CDK; delete it before merging.
/**
 * Exercises the Bulk CDK's `airbyte_source_type` support end to end from inside a connector,
 * against a source-postgres built on the local CDK (`cdkVersion=local`).
 *
 * Reads columns whose configured type is wider than their type in the database, with the database
 * type in `airbyte_source_type`, as the platform configures them after a narrowing type change in
 * the source.
 */
class PostgresSourceFieldConversionIntegrationTest {

    @Test
    @Timeout(value = 300)
    fun testStandardRead() {
        val ops = IntegrationTestOperations(config(cdc = false))
        val output: BufferingOutputConsumer =
            ops.read(widenedCatalog(ops.discover(), SyncMode.FULL_REFRESH))
        Assertions.assertEquals(emptyList<String>(), errors(output))
        Assertions.assertEquals(listOf(EXPECTED_ROW_1), data(output))
    }

    @Test
    @Timeout(value = 300)
    fun testCdcRead() {
        val ops = IntegrationTestOperations(config(cdc = true))
        val catalog: ConfiguredAirbyteCatalog = widenedCatalog(ops.discover(), SyncMode.INCREMENTAL)

        // Sync 1: the initial snapshot.
        val sync1: BufferingOutputConsumer = ops.read(catalog)
        Assertions.assertEquals(emptyList<String>(), errors(sync1))
        Assertions.assertEquals(listOf(EXPECTED_ROW_1), data(sync1))

        // Sync 2: a change read from the WAL.
        execute(INSERT_ROW_2)
        val sync2: BufferingOutputConsumer = ops.read(catalog, sync1.states())
        Assertions.assertEquals(emptyList<String>(), errors(sync2))
        Assertions.assertEquals(listOf(EXPECTED_ROW_2), data(sync2))
    }

    @Test
    @Timeout(value = 300)
    fun testSourceTypeChangedAgain() {
        val ops = IntegrationTestOperations(config(cdc = false))
        // k is an integer in the database, not a boolean.
        val catalog: ConfiguredAirbyteCatalog =
            widenedCatalog(
                ops.discover(),
                SyncMode.FULL_REFRESH,
                "k" to """{"type": "string", "airbyte_source_type": "boolean"}""",
            )
        val output: BufferingOutputConsumer = ops.read(catalog)
        Assertions.assertEquals(emptyList<JsonNode>(), data(output))
        assertSingleError(output, "schema expects source type boolean")
    }

    @Test
    @Timeout(value = 300)
    fun testDedupPrimaryKeyIsNotConverted() {
        val ops = IntegrationTestOperations(config(cdc = false))
        val catalog: ConfiguredAirbyteCatalog =
            widenedCatalog(
                ops.discover(),
                SyncMode.FULL_REFRESH,
                destinationSyncMode = DestinationSyncMode.APPEND_DEDUP,
                primaryKey = "k",
            )
        val output: BufferingOutputConsumer = ops.read(catalog)
        Assertions.assertEquals(emptyList<JsonNode>(), data(output))
        assertSingleError(output, "part of the primary key or cursor")
    }

    /**
     * The record data, without the CDC meta fields, as a destination would parse it: number nodes
     * are compared by value, not by Jackson node class.
     */
    private fun data(output: BufferingOutputConsumer): List<JsonNode> =
        output
            .records()
            .filter { it.stream == TABLE }
            .map { record ->
                val data = record.data.deepCopy() as ObjectNode
                data.remove(
                    data.fieldNames().asSequence().filter { it.startsWith("_ab_") }.toList(),
                )
                Jsons.readTree(Jsons.writeValueAsString(data))
            }

    private fun errors(output: BufferingOutputConsumer): List<String> =
        output
            .traces()
            .filter { it.type == AirbyteTraceMessage.Type.ERROR }
            .map { it.error.message }

    private fun assertSingleError(
        output: BufferingOutputConsumer,
        expectedMessagePart: String,
    ) {
        val errors: List<String> = errors(output)
        Assertions.assertEquals(1, errors.size, "errors: $errors")
        Assertions.assertTrue(
            errors.single().contains(expectedMessagePart),
            "error: ${errors.single()}",
        )
    }

    /**
     * The discovered catalog with every column but `id` widened as the platform would, then
     * [overrides] applied on top.
     */
    private fun widenedCatalog(
        streams: Map<String, AirbyteStream>,
        syncMode: SyncMode,
        vararg overrides: Pair<String, String>,
        destinationSyncMode: DestinationSyncMode = DestinationSyncMode.APPEND,
        primaryKey: String = "id",
    ): ConfiguredAirbyteCatalog {
        val stream: AirbyteStream = streams.getValue(TABLE)
        val properties = stream.jsonSchema["properties"] as ObjectNode
        for ((column, schema) in WIDENED_COLUMNS + overrides) {
            properties.set<JsonNode>(column, Jsons.readTree(schema))
        }
        val configuredStream =
            CatalogHelpers.toDefaultConfiguredStream(stream)
                .withSyncMode(syncMode)
                .withDestinationSyncMode(destinationSyncMode)
                .withPrimaryKey(listOf(listOf(primaryKey)))
        return ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))
    }

    companion object {
        private const val SCHEMA = "public"
        private const val TABLE = "widened"

        /** Column schemas as the platform saves them: wide `type`, database type on the side. */
        val WIDENED_COLUMNS: List<Pair<String, String>> =
            listOf(
                "k" to """{"type": "string", "airbyte_source_type": "integer"}""",
                "i" to """{"type": "number", "airbyte_source_type": "integer"}""",
                "n" to """{"type": "string", "airbyte_source_type": "number"}""",
                "b" to """{"type": "string", "airbyte_source_type": "boolean"}""",
                "d" to
                    """
                    |{"type": "string", "format": "date-time",
                    |"airbyte_type": "timestamp_without_timezone", "airbyte_source_type": "date"}
                    """
                        .trimMargin(),
                "ts" to
                    """
                    |{"type": "string", "format": "date-time",
                    |"airbyte_type": "timestamp_with_timezone",
                    |"airbyte_source_type": "timestamp_without_timezone"}
                    """
                        .trimMargin(),
                "t" to
                    """
                    |{"type": "string", "format": "time",
                    |"airbyte_type": "time_with_timezone",
                    |"airbyte_source_type": "time_without_timezone"}
                    """
                        .trimMargin(),
                "arr" to """{"type": "unknown", "airbyte_source_type": "array"}""",
                // source-postgres reads a scalar bytea as hex text (e.g. \x0102), a string.
                "by" to """{"type": "unknown", "airbyte_source_type": "string"}""",
                // source-postgres reads json and jsonb as text, so the platform sees a string.
                "j" to """{"type": "unknown", "airbyte_source_type": "string"}""",
            )

        private const val CREATE_TABLE =
            """CREATE TABLE $SCHEMA.$TABLE (
            id bigint PRIMARY KEY, k integer, i bigint, n numeric(10, 2), b boolean, d date,
            ts timestamp, t time, arr integer[], by bytea, j jsonb);"""

        private const val INSERT_ROW_1 =
            """INSERT INTO $SCHEMA.$TABLE VALUES (1, 456, 9007199254740993, 2.25, true,
            '2024-01-02', '2024-01-02 03:04:05', '03:04:05', '{1,2}', '\x0102', '{"a": 1}');"""

        private const val INSERT_ROW_2 =
            """INSERT INTO $SCHEMA.$TABLE VALUES (2, 789, -5, 3.75, false,
            '2024-05-06', '2024-05-06 07:08:09', '07:08:09', '{3}', '\x03', '[true]');"""

        val EXPECTED_ROW_1: JsonNode =
            Jsons.readTree(
                """
                |{"id":1,"k":"456","i":9007199254740993,"n":"2.25","b":"true",
                |"d":"2024-01-02T00:00:00.000000","ts":"2024-01-02T03:04:05.000000Z",
                |"t":"03:04:05.000000Z","arr":[1,2],"by":"\\x0102","j":"{\"a\": 1}"}
                """
                    .trimMargin(),
            )
        val EXPECTED_ROW_2: JsonNode =
            Jsons.readTree(
                """
                |{"id":2,"k":"789","i":-5,"n":"3.75","b":"false",
                |"d":"2024-05-06T00:00:00.000000","ts":"2024-05-06T07:08:09.000000Z",
                |"t":"07:08:09.000000Z","arr":[3],"by":"\\x03","j":"[true]"}
                """
                    .trimMargin(),
            )

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
                    .withReplicationSlot()
                    .withPublicationForAllTables()
            // Executed directly: TestDatabase.with() formats its SQL, and the bytea literals
            // contain backslashes.
            execute(CREATE_TABLE)
            execute(INSERT_ROW_1)
        }

        @JvmStatic
        @AfterAll
        fun tearDown() {
            testdb.close()
        }
    }
}
