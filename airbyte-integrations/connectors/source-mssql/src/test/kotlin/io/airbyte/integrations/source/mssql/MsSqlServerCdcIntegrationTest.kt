/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.SyncMode
import java.sql.Connection
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInstance
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.assertDoesNotThrow
import org.testcontainers.containers.MSSQLServerContainer

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class MsSqlServerCdcIntegrationTest {

    /**
     * Regression test for https://github.com/airbytehq/airbyte/pull/73349: Navision / Business
     * Central style identifiers containing spaces and `$` must be escaped in Debezium's
     * `message.key.columns`, otherwise the engine fails config validation on startup. The second
     * read also proves the escaped value still matches the real table, since Debezium treats the
     * table part as a regex.
     */
    @Test
    fun testSpecialCharactersInTableAndPrimaryKeyNames() {
        val catalog = configuredCatalog(SPECIAL_TABLE)
        val state1: AirbyteStateMessage =
            CliRunner.source("read", config(), catalog).run().states().last()

        execute("INSERT INTO dbo.[$SPECIAL_TABLE] ([$SPECIAL_PK], [Item No_]) VALUES (3, 'ITEM-3')")
        execute("EXEC sys.sp_cdc_scan")

        // A failed read emits an ERROR trace and then run() throws ConnectorUncleanExitException.
        val run2: BufferingOutputConsumer = assertDoesNotThrow {
            CliRunner.source("read", config(), catalog, listOf(state1)).run()
        }
        val errorTraces: List<AirbyteTraceMessage> =
            run2.traces().filter { it.type == AirbyteTraceMessage.Type.ERROR }
        assertEquals(emptyList<AirbyteTraceMessage>(), errorTraces)
        val insertedRecords: List<AirbyteRecordMessage> =
            run2.records().filter { it.data[SPECIAL_PK]?.asInt() == 3 }
        assertEquals(1, insertedRecords.size, "records: ${run2.records()}")
        assertEquals("ITEM-3", insertedRecords.first().data["Item No_"].asText())
    }

    private fun configuredCatalog(tableName: String): ConfiguredAirbyteCatalog {
        val stream: AirbyteStream? =
            CliRunner.source("discover", config())
                .run()
                .catalogs()
                .firstOrNull()
                ?.streams
                ?.find { it.namespace == "dbo" && it.name == tableName }
        assertNotNull(stream, "stream dbo.$tableName not discovered")
        val configuredStream =
            CatalogHelpers.toDefaultConfiguredStream(stream)
                .withSyncMode(SyncMode.INCREMENTAL)
                .withPrimaryKey(stream!!.sourceDefinedPrimaryKey)
                .withCursorField(
                    listOf(MsSqlSourceOperations.MsSqlServerCdcMetaFields.CDC_CURSOR.id),
                )
        return ConfiguredAirbyteCatalog().withStreams(listOf(configuredStream))
    }

    companion object {
        const val SPECIAL_TABLE = "CRON UK\$Item Ledger Entry"
        const val SPECIAL_PK = "Entry No_"

        lateinit var dbContainer: MSSQLServerContainer<*>

        fun config(): MsSqlServerSourceConfigurationSpecification =
            MsSqlServerContainerFactory.config(dbContainer).also { it.setIncrementalValue(Cdc()) }

        fun execute(vararg sql: String) {
            JdbcConnectionFactory(MsSqlServerSourceConfigurationFactory().make(config()))
                .get()
                .use { connection: Connection ->
                    connection.isReadOnly = false
                    for (statement in sql) {
                        connection.createStatement().use { it.execute(statement) }
                    }
                }
        }

        @JvmStatic
        @BeforeAll
        @Timeout(value = 300)
        fun startAndProvisionTestContainer() {
            dbContainer =
                MsSqlServerContainerFactory.exclusive(
                    "mcr.microsoft.com/mssql/server:2022-latest",
                    MsSqlServerContainerFactory.WithNetwork,
                    MsSqlServerContainerFactory.WithTestDatabase,
                )
            execute(
                "EXEC sys.sp_cdc_enable_db",
                "CREATE TABLE dbo.[$SPECIAL_TABLE] " +
                    "([$SPECIAL_PK] INT PRIMARY KEY, [Item No_] NVARCHAR(20))",
                "EXEC sys.sp_cdc_enable_table @source_schema = N'dbo', " +
                    "@source_name = N'$SPECIAL_TABLE', @role_name = NULL",
                "INSERT INTO dbo.[$SPECIAL_TABLE] ([$SPECIAL_PK], [Item No_]) " +
                    "VALUES (1, 'ITEM-1'), (2, 'ITEM-2')",
                // SQL Agent is disabled in the test container, so the CDC capture job never runs.
                "EXEC sys.sp_cdc_scan",
            )
        }

        @JvmStatic
        @AfterAll
        fun stopTestContainer() {
            if (::dbContainer.isInitialized) dbContainer.stop()
        }
    }
}
