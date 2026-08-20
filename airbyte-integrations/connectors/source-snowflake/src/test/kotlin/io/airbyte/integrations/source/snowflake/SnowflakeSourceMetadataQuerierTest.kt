/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.sql.Connection
import java.sql.DatabaseMetaData
import java.sql.ResultSet
import java.sql.SQLException
import java.sql.Statement
import java.sql.Types
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.mockito.ArgumentMatchers
import org.mockito.Mockito.mock
import org.mockito.Mockito.times
import org.mockito.Mockito.verify
import org.mockito.Mockito.`when`

class SnowflakeSourceMetadataQuerierTest {

    @Test
    fun `fields returns empty when privilege probe fails with SQLException`() {
        val table = TableName(catalog = "DB", schema = "PUBLIC", name = "V_WITH_SESSION_VAR", type = "VIEW")
        val dbmd = mock(DatabaseMetaData::class.java)
        val conn = mock(Connection::class.java)
        val stmt = mock(java.sql.Statement::class.java)
        val config = mock(JdbcSourceConfiguration::class.java)
        val base = baseQuerier(conn, config)
        val querier = SnowflakeSourceMetadataQuerier(base, schema = "PUBLIC")

        `when`(conn.metaData).thenReturn(dbmd)
        `when`(conn.createStatement()).thenReturn(stmt)
        `when`(config.namespaces).thenReturn(setOf("DB"))
        `when`(config.checkPrivileges).thenReturn(true)
        `when`(stmt.executeQuery(ArgumentMatchers.anyString())).thenThrow(SQLException("session variable error"))

        `when`(dbmd.getTables("DB", "PUBLIC", null, arrayOf("TABLE", "VIEW")))
            .thenReturn(tableResultSet(table))
        `when`(dbmd.getColumns("DB", "PUBLIC", null, null))
            .thenReturn(
                columnResultSet(
                    table,
                    JdbcMetadataQuerier.ColumnMetadata(
                        name = "C1",
                        label = "C1",
                        type = SystemType("VARCHAR", Types.VARCHAR, 100, 0),
                        nullable = true,
                        ordinal = 1,
                    )
                )
            )

        val streamId =
            StreamIdentifier.from(StreamDescriptor().withNamespace("PUBLIC").withName("V_WITH_SESSION_VAR"))
        val fields = querier.fields(streamId)

        assertTrue(fields.isEmpty())
    }

    @Test
    fun `fields falls back to per-column queries when multi-column probe fails`() {
        val table = TableName(catalog = "DB", schema = "PUBLIC", name = "V_PARTIAL", type = "VIEW")
        val dbmd = mock(DatabaseMetaData::class.java)
        val conn = mock(Connection::class.java)
        val stmt = mock(Statement::class.java)
        val config = mock(JdbcSourceConfiguration::class.java)
        val base = baseQuerier(conn, config)
        val querier = SnowflakeSourceMetadataQuerier(base, schema = "PUBLIC")

        `when`(conn.metaData).thenReturn(dbmd)
        `when`(conn.createStatement()).thenReturn(stmt)
        `when`(config.namespaces).thenReturn(setOf("DB"))
        `when`(config.checkPrivileges).thenReturn(true)
        `when`(dbmd.getTables("DB", "PUBLIC", null, arrayOf("TABLE", "VIEW")))
            .thenReturn(tableResultSet(table))
        `when`(dbmd.getColumns("DB", "PUBLIC", null, null))
            .thenReturn(
                columnResultSet(
                    table,
                    JdbcMetadataQuerier.ColumnMetadata(
                        name = "COL_A",
                        label = "COL_A",
                        type = SystemType("VARCHAR", Types.VARCHAR, 100, 0),
                        nullable = true,
                        ordinal = 1,
                    ),
                    JdbcMetadataQuerier.ColumnMetadata(
                        name = "COL_B",
                        label = "COL_B",
                        type = SystemType("VARCHAR", Types.VARCHAR, 100, 0),
                        nullable = true,
                        ordinal = 2,
                    ),
                )
            )

        val multiSql = "SELECT \"COL_A\", \"COL_B\" FROM \"PUBLIC\".\"V_PARTIAL\" LIMIT ?"
        val colASql = "SELECT \"COL_A\" FROM \"PUBLIC\".\"V_PARTIAL\" LIMIT ?"
        val colBSql = "SELECT \"COL_B\" FROM \"PUBLIC\".\"V_PARTIAL\" LIMIT ?"
        `when`(stmt.executeQuery(multiSql)).thenThrow(SQLException("session var missing"))
        `when`(stmt.executeQuery(colASql)).thenReturn(queryMetadataResultSet("COL_A", "COL_A"))
        `when`(stmt.executeQuery(colBSql)).thenThrow(SQLException("no privilege"))

        val streamId =
            StreamIdentifier.from(StreamDescriptor().withNamespace("PUBLIC").withName("V_PARTIAL"))
        val fields = querier.fields(streamId)

        assertEquals(listOf("COL_A"), fields.map { it.id })
    }

    @Test
    fun `table discovery tries original and uppercase schema when configured schema is lowercase`() {
        val dbmd = mock(DatabaseMetaData::class.java)
        val conn = mock(Connection::class.java)
        val config = mock(JdbcSourceConfiguration::class.java)
        val base = baseQuerier(conn, config)
        val querier = SnowflakeSourceMetadataQuerier(base, schema = "myschema")

        `when`(conn.metaData).thenReturn(dbmd)
        `when`(config.namespaces).thenReturn(setOf("DB"))
        `when`(config.checkPrivileges).thenReturn(false)
        `when`(dbmd.getTables("DB", "myschema", null, arrayOf("TABLE", "VIEW"))).thenReturn(emptyResultSet())
        `when`(dbmd.getTables("DB", "MYSCHEMA", null, arrayOf("TABLE", "VIEW"))).thenReturn(emptyResultSet())

        querier.memoizedTableNames

        verify(dbmd, times(1)).getTables("DB", "myschema", null, arrayOf("TABLE", "VIEW"))
        verify(dbmd, times(1)).getTables("DB", "MYSCHEMA", null, arrayOf("TABLE", "VIEW"))
    }

    @Test
    fun `table discovery only queries one schema when already uppercase`() {
        val dbmd = mock(DatabaseMetaData::class.java)
        val conn = mock(Connection::class.java)
        val config = mock(JdbcSourceConfiguration::class.java)
        val base = baseQuerier(conn, config)
        val querier = SnowflakeSourceMetadataQuerier(base, schema = "PUBLIC")

        `when`(conn.metaData).thenReturn(dbmd)
        `when`(config.namespaces).thenReturn(setOf("DB"))
        `when`(config.checkPrivileges).thenReturn(false)
        `when`(dbmd.getTables("DB", "PUBLIC", null, arrayOf("TABLE", "VIEW"))).thenReturn(emptyResultSet())

        querier.memoizedTableNames

        verify(dbmd, times(1)).getTables("DB", "PUBLIC", null, arrayOf("TABLE", "VIEW"))
    }

    @Test
    fun `table discovery scales as namespaces times distinct schema variants`() {
        val dbmd = mock(DatabaseMetaData::class.java)
        val conn = mock(Connection::class.java)
        val config = mock(JdbcSourceConfiguration::class.java)
        val base = baseQuerier(conn, config)
        val querier = SnowflakeSourceMetadataQuerier(base, schema = "myschema")

        `when`(conn.metaData).thenReturn(dbmd)
        `when`(config.namespaces).thenReturn(setOf("db1", "DB2"))
        `when`(config.checkPrivileges).thenReturn(false)
        `when`(dbmd.getTables(ArgumentMatchers.anyString(), ArgumentMatchers.anyString(), ArgumentMatchers.isNull(), ArgumentMatchers.any()))
            .thenReturn(emptyResultSet())

        querier.memoizedTableNames

        // namespacesToTry = [db1, DB2, DB1, DB2] => 3 distinct calls over namespace values due to duplicate DB2
        // schemasToTry = [myschema, MYSCHEMA] => 2 calls per namespace value in iteration
        verify(dbmd, times(8)).getTables(
            ArgumentMatchers.anyString(),
            ArgumentMatchers.anyString(),
            ArgumentMatchers.isNull(),
            ArgumentMatchers.any(),
        )
    }

    private fun baseQuerier(conn: Connection, config: JdbcSourceConfiguration): JdbcMetadataQuerier =
        JdbcMetadataQuerier(
            constants = DefaultJdbcConstants(namespaceKind = DefaultJdbcConstants.NamespaceKind.CATALOG_AND_SCHEMA),
            config = config,
            selectQueryGenerator = SnowflakeSourceOperations(),
            fieldTypeMapper = SnowflakeSourceOperations(),
            checkQueries = JdbcCheckQueries(),
            conn = conn,
        )

    private fun emptyResultSet(): ResultSet {
        val rs = mock(ResultSet::class.java)
        `when`(rs.next()).thenReturn(false)
        return rs
    }

    private fun tableResultSet(table: TableName): ResultSet {
        val rs = mock(ResultSet::class.java)
        `when`(rs.next()).thenReturn(true, false)
        `when`(rs.getString("TABLE_CAT")).thenReturn(table.catalog)
        `when`(rs.getString("TABLE_SCHEM")).thenReturn(table.schema)
        `when`(rs.getString("TABLE_NAME")).thenReturn(table.name)
        `when`(rs.getString("TABLE_TYPE")).thenReturn(table.type)
        return rs
    }

    private fun columnResultSet(
        table: TableName,
        vararg columns: JdbcMetadataQuerier.ColumnMetadata,
    ): ResultSet {
        val rs = mock(ResultSet::class.java)
        `when`(rs.next()).thenReturn(*((Array(columns.size) { true }) + false))
        `when`(rs.getString("TABLE_CAT")).thenReturn(*Array(columns.size) { table.catalog })
        `when`(rs.getString("TABLE_SCHEM")).thenReturn(*Array(columns.size) { table.schema })
        `when`(rs.getString("TABLE_NAME")).thenReturn(*Array(columns.size) { table.name })
        `when`(rs.getString("COLUMN_NAME")).thenReturn(*columns.map { it.name }.toTypedArray())
        `when`(rs.getString("TYPE_NAME")).thenReturn(*columns.map { it.type.typeName }.toTypedArray())
        `when`(rs.getInt("DATA_TYPE")).thenReturn(*columns.map { it.type.typeCode }.toTypedArray())
        `when`(rs.getInt("COLUMN_SIZE")).thenReturn(*columns.map { it.type.precision ?: 0 }.toTypedArray())
        `when`(rs.getInt("DECIMAL_DIGITS")).thenReturn(*columns.map { it.type.scale ?: 0 }.toTypedArray())
        `when`(rs.getString("IS_NULLABLE")).thenReturn("YES")
        `when`(rs.getInt("ORDINAL_POSITION")).thenReturn(*columns.map { it.ordinal ?: 1 }.toTypedArray())
        return rs
    }

    private fun queryMetadataResultSet(columnName: String, columnLabel: String): ResultSet {
        val rs = mock(ResultSet::class.java)
        val rsmd = mock(java.sql.ResultSetMetaData::class.java)
        `when`(rs.metaData).thenReturn(rsmd)
        `when`(rsmd.columnCount).thenReturn(1)
        `when`(rsmd.getColumnName(1)).thenReturn(columnName)
        `when`(rsmd.getColumnLabel(1)).thenReturn(columnLabel)
        `when`(rsmd.getColumnTypeName(1)).thenReturn("VARCHAR")
        `when`(rsmd.getColumnType(1)).thenReturn(Types.VARCHAR)
        `when`(rsmd.getPrecision(1)).thenReturn(100)
        `when`(rsmd.getScale(1)).thenReturn(0)
        `when`(rsmd.isNullable(1)).thenReturn(java.sql.ResultSetMetaData.columnNullable)
        return rs
    }
}
