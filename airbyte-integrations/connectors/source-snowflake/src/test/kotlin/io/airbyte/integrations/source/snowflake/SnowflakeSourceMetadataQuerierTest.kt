/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.DefaultJdbcConstants.NamespaceKind
import io.mockk.every
import io.mockk.mockk
import io.mockk.slot
import io.mockk.verify
import java.sql.Connection
import java.sql.DatabaseMetaData
import java.sql.ResultSet
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class SnowflakeSourceMetadataQuerierTest {

    private fun makeResultSet(rows: List<Map<String, Any?>>): ResultSet {
        val rs = mockk<ResultSet>()
        var index = -1
        var lastColumn: String? = null
        every { rs.next() } answers { ++index < rows.size }
        every { rs.getString(any<String>()) } answers {
            lastColumn = firstArg()
            rows[index][lastColumn] as? String
        }
        every { rs.getInt(any<String>()) } answers {
            lastColumn = firstArg()
            (rows[index][lastColumn] as? Int) ?: 0
        }
        every { rs.wasNull() } answers { rows[index][lastColumn] == null }
        every { rs.close() } returns Unit
        return rs
    }

    private fun makeQuerier(
        schema: String?,
        tableRows: List<Map<String, Any?>>,
        columnRowsByPattern: Map<String?, List<Map<String, Any?>>>,
    ): Pair<SnowflakeSourceMetadataQuerier, DatabaseMetaData> {
        val dbmd = mockk<DatabaseMetaData>()
        every { dbmd.searchStringEscape } returns "\\"
        every { dbmd.getTables(any(), any(), null, any()) } answers { makeResultSet(tableRows) }
        every { dbmd.getColumns(any(), any(), null, null) } answers {
            makeResultSet(columnRowsByPattern[secondArg()] ?: emptyList())
        }
        val conn = mockk<Connection>()
        every { conn.metaData } returns dbmd
        val config = mockk<JdbcSourceConfiguration>()
        every { config.namespaces } returns setOf("TEST_DB")
        every { config.checkPrivileges } returns false
        val base = mockk<JdbcMetadataQuerier>()
        every { base.conn } returns conn
        every { base.constants } returns
            DefaultJdbcConstants(namespaceKind = NamespaceKind.CATALOG_AND_SCHEMA)
        every { base.config } returns config
        return SnowflakeSourceMetadataQuerier(base, schema) to dbmd
    }

    private fun tableRow(catalog: String, schema: String, name: String) =
        mapOf(
            "TABLE_CAT" to catalog,
            "TABLE_SCHEM" to schema,
            "TABLE_NAME" to name,
            "TABLE_TYPE" to "TABLE",
        )

    private fun columnRow(
        catalog: String,
        schema: String,
        table: String,
        column: String,
        ordinal: Int = 1,
    ) =
        mapOf(
            "TABLE_CAT" to catalog,
            "TABLE_SCHEM" to schema,
            "TABLE_NAME" to table,
            "COLUMN_NAME" to column,
            "TYPE_NAME" to "TEXT",
            "DATA_TYPE" to 12,
            "COLUMN_SIZE" to 16777216,
            "DECIMAL_DIGITS" to 0,
            "IS_NULLABLE" to "YES",
            "ORDINAL_POSITION" to ordinal,
        )

    @Test
    fun `escapeSearchPattern escapes LIKE metacharacters`() {
        assertEquals(
            "TEST\\_SCHEMA",
            SnowflakeSourceMetadataQuerier.escapeSearchPattern("TEST_SCHEMA", "\\"),
        )
        assertEquals(
            "TEST\\%",
            SnowflakeSourceMetadataQuerier.escapeSearchPattern("TEST%", "\\"),
        )
        assertEquals(
            "A\\\\B\\_C",
            SnowflakeSourceMetadataQuerier.escapeSearchPattern("A\\B_C", "\\"),
        )
        assertEquals(
            "TEST_SCHEMA",
            SnowflakeSourceMetadataQuerier.escapeSearchPattern("TEST_SCHEMA", ""),
        )
    }

    @Test
    fun `getTables is called with the escaped schema pattern`() {
        val slot = slot<String>()
        val dbmd = mockk<DatabaseMetaData>()
        every { dbmd.searchStringEscape } returns "\\"
        every { dbmd.getTables("TEST_DB", capture(slot), null, any()) } answers {
            makeResultSet(emptyList())
        }
        val conn = mockk<Connection>()
        every { conn.metaData } returns dbmd
        val config = mockk<JdbcSourceConfiguration>()
        every { config.namespaces } returns setOf("TEST_DB")
        every { config.checkPrivileges } returns false
        val base = mockk<JdbcMetadataQuerier>()
        every { base.conn } returns conn
        every { base.constants } returns
            DefaultJdbcConstants(namespaceKind = NamespaceKind.CATALOG_AND_SCHEMA)
        every { base.config } returns config
        val querier = SnowflakeSourceMetadataQuerier(base, "TEST_SCHEMA")
        querier.memoizedTableNames
        assertEquals("TEST\\_SCHEMA", slot.captured)
    }

    @Test
    fun `over-matched tables from getTables are filtered to the configured schema`() {
        val (querier, _) =
            makeQuerier(
                schema = "TEST_SCHEMA",
                tableRows =
                    listOf(
                        tableRow("TEST_DB", "TEST_SCHEMA", "USERS"),
                        tableRow("TEST_DB", "TESTXSCHEMA", "USERS"),
                    ),
                columnRowsByPattern = emptyMap(),
            )
        assertEquals(listOf("TEST_SCHEMA"), querier.streamNamespaces())
    }

    @Test
    fun `over-matched getColumns results do not produce duplicate columns`() {
        // Simulates a driver that ignores LIKE escaping: the escaped pattern for
        // TEST_SCHEMA over-matches and returns columns for TESTXSCHEMA too, while
        // the literal TESTXSCHEMA query also returns its columns. Without
        // deduplication this produces a duplicate USER_ID and discovery dies with
        // `IllegalStateException: Duplicate key USER_ID`.
        val (querier, dbmd) =
            makeQuerier(
                schema = null,
                tableRows =
                    listOf(
                        tableRow("TEST_DB", "TEST_SCHEMA", "USERS"),
                        tableRow("TEST_DB", "TESTXSCHEMA", "USERS"),
                    ),
                columnRowsByPattern =
                    mapOf(
                        "TEST\\_SCHEMA" to
                            listOf(
                                columnRow("TEST_DB", "TEST_SCHEMA", "USERS", "USER_ID"),
                                columnRow("TEST_DB", "TESTXSCHEMA", "USERS", "USER_ID"),
                            ),
                        "TEST_SCHEMA" to
                            listOf(
                                columnRow("TEST_DB", "TEST_SCHEMA", "USERS", "USER_ID"),
                                columnRow("TEST_DB", "TESTXSCHEMA", "USERS", "USER_ID"),
                            ),
                        "TESTXSCHEMA" to
                            listOf(
                                columnRow("TEST_DB", "TESTXSCHEMA", "USERS", "USER_ID"),
                            ),
                    ),
            )
        val testX =
            querier.columnMetadata(TableName("TEST_DB", "TESTXSCHEMA", "USERS", "TABLE"))
        assertEquals(listOf("USER_ID"), testX.map { it.name })
        val test =
            querier.columnMetadata(TableName("TEST_DB", "TEST_SCHEMA", "USERS", "TABLE"))
        assertEquals(listOf("USER_ID"), test.map { it.name })
        verify { dbmd.getColumns("TEST_DB", "TEST\\_SCHEMA", null, null) }
    }
}
