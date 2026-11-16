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

    @Test
    fun testSpecialCharactersInTableAndPrimaryKeyNames() {
        assertSubsequentReadCapturesInsert("dbo", SPECIAL_TABLE, SPECIAL_PK)
    }

    @Test
    fun testSpecialCharactersInSchemaName() {
        assertSubsequentReadCapturesInsert(SPECIAL_SCHEMA, SPECIAL_SCHEMA_TABLE, SPECIAL_PK)
    }

    private fun assertSubsequentReadCapturesInsert(schema: String, table: String, pk: String) {
        val catalog = configuredCatalog(schema, table)
        val state1: AirbyteStateMessage =
            CliRunner.source("read", config(), catalog).run().states().last()

        execute("INSERT INTO [$schema].[$table] ([$pk], [Item No_]) VALUES (3, 'ITEM-3')")
        execute("EXEC sys.sp_cdc_scan")

        // A failed read emits an ERROR trace and then run() throws ConnectorUncleanExitException.
        val run2: BufferingOutputConsumer = assertDoesNotThrow {
            CliRunner.source("read", config(), catalog, listOf(state1)).run()
        }
        val errorTraces: List<AirbyteTraceMessage> =
            run2.traces().filter { it.type == AirbyteTraceMessage.Type.ERROR }
        assertEquals(emptyList<AirbyteTraceMessage>(), errorTraces)
        val insertedRecords: List<AirbyteRecordMessage> =
            run2.records().filter { it.data[pk]?.asInt() == 3 }
        assertEquals(1, insertedRecords.size, "records: ${run2.records()}")
        assertEquals("ITEM-3", insertedRecords.first().data["Item No_"].asText())
    }

    private fun configuredCatalog(schema: String, table: String): ConfiguredAirbyteCatalog {
        val stream: AirbyteStream? =
            CliRunner.source("discover", config()).run().catalogs().firstOrNull()?.streams?.find {
                it.namespace == schema && it.name == table
            }
        assertNotNull(stream, "stream $schema.$table not discovered")
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
        const val SPECIAL_SCHEMA = "CRON\$Sales"
        const val SPECIAL_SCHEMA_TABLE = "Sales Line"

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
            execute("EXEC sys.sp_cdc_enable_db", "CREATE SCHEMA [$SPECIAL_SCHEMA]")
            for ((schema, table) in
                listOf("dbo" to SPECIAL_TABLE, SPECIAL_SCHEMA to SPECIAL_SCHEMA_TABLE)) {
                execute(
                    "CREATE TABLE [$schema].[$table] " +
                        "([$SPECIAL_PK] INT PRIMARY KEY, [Item No_] NVARCHAR(20))",
                    "EXEC sys.sp_cdc_enable_table @source_schema = N'$schema', " +
                        "@source_name = N'$table', @role_name = NULL",
                    "INSERT INTO [$schema].[$table] ([$SPECIAL_PK], [Item No_]) " +
                        "VALUES (1, 'ITEM-1'), (2, 'ITEM-2')",
                )
            }
            // SQL Agent is disabled in the test container, so the CDC capture job never runs.
            execute("EXEC sys.sp_cdc_scan")
        }

        @JvmStatic
        @AfterAll
        fun stopTestContainer() {
            if (::dbContainer.isInitialized) dbContainer.stop()
        }
    }
}
