/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.cdc.DebeziumOffset
import io.airbyte.cdk.read.cdc.ValidDebeziumWarmStartState
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.mssql.MsSqlServerDebeziumOperations.Companion.MSSQL_CDC_OFFSET
import io.airbyte.integrations.source.mssql.MsSqlServerDebeziumOperations.Companion.MSSQL_DB_HISTORY
import io.airbyte.integrations.source.mssql.MsSqlServerDebeziumOperations.Companion.MSSQL_STATE
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.SyncMode
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInstance
import org.junit.jupiter.api.Timeout
import org.testcontainers.containers.MSSQLServerContainer

/**
 * airbytehq/oncall#13544: a sync that resumes from a heartbeat offset (change_lsn = NULL) must
 * still replay the schema-history records of columns added via ALTER TABLE. A heartbeat offset is
 * simulated by rewriting the saved state, which keeps the test deterministic.
 */
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class MsSqlServerCdcHeartbeatSchemaChangeIntegrationTest {

    private lateinit var container: MSSQLServerContainer<*>
    private lateinit var spec: MsSqlServerSourceConfigurationSpecification
    private lateinit var config: MsSqlServerSourceConfiguration
    private lateinit var catalog: ConfiguredAirbyteCatalog
    private lateinit var heartbeatState: AirbyteStateMessage
    private lateinit var resumedRecords: List<AirbyteRecordMessage>

    @BeforeAll
    @Timeout(value = 600)
    fun syncAcrossSchemaChangeAndHeartbeat() {
        container =
            MsSqlServerContainerFactory.exclusive(
                "mcr.microsoft.com/mssql/server:2022-latest",
                MsSqlServerContainerFactory.WithNetwork,
                MsSqlServerContainerFactory.WithTestDatabase,
            )
        spec = MsSqlServerContainerFactory.config(container).also { it.setIncrementalValue(Cdc()) }
        config = MsSqlServerSourceConfigurationFactory().make(spec)

        execute(
            "EXEC sys.sp_cdc_enable_db",
            "CREATE TABLE dbo.users (id INT IDENTITY PRIMARY KEY, email NVARCHAR(100))",
            "EXEC sys.sp_cdc_enable_table @source_schema = 'dbo', @source_name = 'users', " +
                "@role_name = NULL, @capture_instance = 'dbo_users'",
            "INSERT INTO dbo.users (email) VALUES ('alice@example.com')",
        )
        val state1 = read(discoverUsers(), state = null).states().last()

        execute(
            "ALTER TABLE dbo.users ADD nickname NVARCHAR(50) NULL",
            "EXEC sys.sp_cdc_enable_table @source_schema = 'dbo', @source_name = 'users', " +
                "@role_name = NULL, @capture_instance = 'dbo_users_v2'",
            "INSERT INTO dbo.users (email, nickname) VALUES ('dave@example.com', 'dave')",
        )
        catalog = discoverUsers()
        val sync2 = read(catalog, state1)
        // Sanity check: the ALTER is handled when the offset carries a real change_lsn.
        assertEquals("dave", nickname(sync2.records(), "dave@example.com"))
        val state2 = sync2.states().last()
        assertNotNull(sharedState(state2)[MSSQL_STATE][MSSQL_DB_HISTORY])

        heartbeatState =
            withOffset(state2) { it.put("change_lsn", "NULL").put("event_serial_no", 0) }
        execute("INSERT INTO dbo.users (email, nickname) VALUES ('erin@example.com', 'erin')")
        resumedRecords = read(catalog, heartbeatState).records()
    }

    @AfterAll
    fun stopContainer() {
        if (::container.isInitialized) container.stop()
    }

    @Test
    fun `resume from heartbeat offset keeps columns added via ALTER`() {
        assertEquals("erin", nickname(resumedRecords, "erin@example.com"))
    }

    @Test
    fun `deserializeState normalizes heartbeat offset`() {
        val warmStart = operations().deserializeState(sharedState(heartbeatState))

        assertInstanceOf(ValidDebeziumWarmStartState::class.java, warmStart)
        val offset = (warmStart as ValidDebeziumWarmStartState).offset.wrapped.values.first()
        assertEquals(offset["commit_lsn"].asText(), offset["change_lsn"].asText())
    }

    @Test
    fun `sanitizeOffset runs before heartbeat normalization`() {
        // Mid-transaction offset: normalizing first would set change_lsn to commit_lsn and skip
        // the rest of the transaction on resume, instead of restoring the starting position.
        val midTransaction =
            withOffset(heartbeatState) {
                it.put("change_lsn", MID_TX_CHANGE_LSN).put("event_serial_no", 2)
            }
        val operations = operations()
        operations.deserializeState(sharedState(midTransaction))

        val heartbeat = offsetValues(sharedState(heartbeatState)).first()
        val serialized =
            operations.serializeState(
                DebeziumOffset(mapOf(offsetKey(sharedState(heartbeatState)) to heartbeat)),
                null,
            )

        val offset = offsetValues(serialized).first()
        assertEquals(MID_TX_CHANGE_LSN, offset["change_lsn"].asText())
        assertEquals(2, offset["event_serial_no"].asInt())
    }

    private fun operations() =
        MsSqlServerDebeziumOperations(JdbcConnectionFactory(config), config, catalog)

    /** Runs each statement, then a CDC scan: SQL Server Agent is not running in the container. */
    private fun execute(vararg statements: String) {
        JdbcConnectionFactory(config).get().use { connection ->
            connection.isReadOnly = false
            connection.createStatement().use { stmt -> statements.forEach(stmt::execute) }
        }
        JdbcConnectionFactory(config).get().use { connection ->
            connection.createStatement().use { it.execute("EXEC sys.sp_cdc_scan") }
        }
    }

    private fun discoverUsers(): ConfiguredAirbyteCatalog {
        val stream =
            CliRunner.source("discover", spec).run().catalogs().first().streams.first {
                it.namespace == "dbo" && it.name == "users"
            }
        val configuredStream =
            CatalogHelpers.toDefaultConfiguredStream(stream)
                .withSyncMode(SyncMode.INCREMENTAL)
                .withCursorField(
                    listOf(MsSqlSourceOperations.MsSqlServerCdcMetaFields.CDC_CURSOR.id)
                )
        return ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))
    }

    private fun read(catalog: ConfiguredAirbyteCatalog, state: AirbyteStateMessage?) =
        CliRunner.source("read", spec, catalog, state?.let { listOf(it) }).run()

    private fun nickname(records: List<AirbyteRecordMessage>, email: String): String? =
        records.single { it.data["email"]?.asText() == email }.data["nickname"]?.textValue()

    private fun sharedState(state: AirbyteStateMessage): JsonNode = state.global.sharedState

    private fun offsetKey(sharedState: JsonNode): JsonNode =
        Jsons.readTree(sharedState[MSSQL_STATE][MSSQL_CDC_OFFSET].fieldNames().next())

    private fun offsetValues(sharedState: JsonNode): List<ObjectNode> =
        sharedState[MSSQL_STATE][MSSQL_CDC_OFFSET].elements().asSequence().toList().map {
            Jsons.readTree(it.asText()) as ObjectNode
        }

    /** Copies [state], applying [edit] to each Debezium offset value (stored as JSON strings). */
    private fun withOffset(
        state: AirbyteStateMessage,
        edit: (ObjectNode) -> Unit,
    ): AirbyteStateMessage {
        val copy = Jsons.readValue(Jsons.writeValueAsString(state), AirbyteStateMessage::class.java)
        val offsetNode = copy.global.sharedState[MSSQL_STATE][MSSQL_CDC_OFFSET] as ObjectNode
        offsetNode.fieldNames().asSequence().toList().forEach { key ->
            val value = Jsons.readTree(offsetNode[key].asText()) as ObjectNode
            edit(value)
            offsetNode.put(key, Jsons.writeValueAsString(value))
        }
        return copy
    }

    companion object {
        private const val MID_TX_CHANGE_LSN = "00000000:00000001:0001"
    }
}
