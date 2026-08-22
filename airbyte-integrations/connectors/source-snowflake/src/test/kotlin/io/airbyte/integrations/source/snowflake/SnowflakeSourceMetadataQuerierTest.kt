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
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.sql.Connection
import java.sql.DatabaseMetaData
import java.sql.ResultSet
import java.sql.ResultSetMetaData
import java.sql.SQLException
import java.sql.Statement
import java.sql.Types
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.mockito.ArgumentMatchers.any
import org.mockito.ArgumentMatchers.anyString
import org.mockito.ArgumentMatchers.eq
import org.mockito.Mockito.doAnswer
import org.mockito.Mockito.mock
import org.mockito.Mockito.times
import org.mockito.Mockito.verify
import org.mockito.Mockito.`when`

class SnowflakeSourceMetadataQuerierTest {

    @Test
    fun `fields returns empty when privilege probe fails with SQLException`() {
        val table =
            TableName(catalog = "DB", schema = "PUBLIC", name = "V_WITH_SESSION_VAR", type = "VIEW")
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
        `when`(stmt.executeQuery(anyString())).thenThrow(SQLException("session variable error"))
        val tablesRs = tableResultSet(table)
        val columnsRs =
            columnResultSet(
                table,
                listOf(
                    JdbcMetadataQuerier.ColumnMetadata(
                        name = "C1",
                        label = "C1",
                        type = SystemType("VARCHAR", Types.VARCHAR, 100, 0),
                        nullable = true,
                        ordinal = 1,
                    )
                )
            )
        `when`(dbmd.getTables("DB", "PUBLIC", null, arrayOf("TABLE", "VIEW"))).thenReturn(tablesRs)
        `when`(dbmd.getColumns("DB", "PUBLIC", null, null)).thenReturn(columnsRs)

        val streamId =
            StreamIdentifier.from(
                StreamDescriptor().withNamespace("PUBLIC").withName("V_WITH_SESSION_VAR")
            )
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
        val tablesRs = tableResultSet(table)
        val columnsRs =
            columnResultSet(
                table,
                listOf(
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
        `when`(dbmd.getTables("DB", "PUBLIC", null, arrayOf("TABLE", "VIEW"))).thenReturn(tablesRs)
        `when`(dbmd.getColumns("DB", "PUBLIC", null, null)).thenReturn(columnsRs)

        val colAResultSet = queryMetadataResultSet("COL_A", "COL_A")
        doAnswer { invocation ->
                val sql = invocation.getArgument<String>(0)
                when {
                    sql.contains("\"COL_A\"") && sql.contains("\"COL_B\"") ->
                        throw SQLException("session variable error")
                    sql.contains("\"COL_A\"") && !sql.contains("\"COL_B\"") -> colAResultSet
                    sql.contains("\"COL_B\"") && !sql.contains("\"COL_A\"") ->
                        throw SQLException("no privilege")
                    else -> throw SQLException("unexpected sql: $sql")
                }
            }
            .`when`(stmt)
            .executeQuery(anyString())

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
        val lowerSchemaRs = emptyResultSet()
        val upperSchemaRs = emptyResultSet()
        `when`(dbmd.getTables("DB", "myschema", null, arrayOf("TABLE", "VIEW")))
            .thenReturn(lowerSchemaRs)
        `when`(dbmd.getTables("DB", "MYSCHEMA", null, arrayOf("TABLE", "VIEW")))
            .thenReturn(upperSchemaRs)

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
        val publicSchemaRs = emptyResultSet()
        `when`(dbmd.getTables("DB", "PUBLIC", null, arrayOf("TABLE", "VIEW")))
            .thenReturn(publicSchemaRs)

        querier.memoizedTableNames

        verify(dbmd, times(1)).getTables("DB", "PUBLIC", null, arrayOf("TABLE", "VIEW"))
    }

    @Test
    fun `table discovery scales as namespaces times schema variants`() {
        val dbmd = mock(DatabaseMetaData::class.java)
        val conn = mock(Connection::class.java)
        val config = mock(JdbcSourceConfiguration::class.java)
        val base = baseQuerier(conn, config)
        val querier = SnowflakeSourceMetadataQuerier(base, schema = "myschema")

        `when`(conn.metaData).thenReturn(dbmd)
        `when`(config.namespaces).thenReturn(setOf("db1", "DB2"))
        `when`(config.checkPrivileges).thenReturn(false)
        val sharedEmptyRs = emptyResultSet()
        `when`(dbmd.getTables(anyString(), anyString(), eq(null), any())).thenReturn(sharedEmptyRs)

        querier.memoizedTableNames

        // namespacesToTry = [db1, DB2, DB1, DB2] and schemasToTry = [myschema, MYSCHEMA]
        // DISTINCT namespaces are not applied, so DB2 appears twice while db1/DB1 are unique.
        verify(dbmd, times(6)).getTables(anyString(), anyString(), eq(null), any())
    }

    private fun baseQuerier(
        conn: Connection,
        config: JdbcSourceConfiguration
    ): JdbcMetadataQuerier {
        val jdbcConnectionFactory = mock(JdbcConnectionFactory::class.java)
        `when`(jdbcConnectionFactory.get()).thenReturn(conn)
        return JdbcMetadataQuerier(
            constants =
                DefaultJdbcConstants(
                    namespaceKind = DefaultJdbcConstants.NamespaceKind.CATALOG_AND_SCHEMA
                ),
            config = config,
            selectQueryGenerator = SnowflakeSourceOperations(),
            fieldTypeMapper = SnowflakeSourceOperations(),
            checkQueries = JdbcCheckQueries(),
            jdbcConnectionFactory = jdbcConnectionFactory,
        )
    }

    private fun emptyResultSet(): ResultSet {
        val rs = mock(ResultSet::class.java)
        `when`(rs.next()).thenReturn(false)
        return rs
    }

    private fun tableResultSet(table: TableName): ResultSet {
        val rs = mock(ResultSet::class.java)
        `when`(rs.next()).thenReturn(true).thenReturn(false)
        `when`(rs.getString("TABLE_CAT")).thenReturn(table.catalog)
        `when`(rs.getString("TABLE_SCHEM")).thenReturn(table.schema)
        `when`(rs.getString("TABLE_NAME")).thenReturn(table.name)
        `when`(rs.getString("TABLE_TYPE")).thenReturn(table.type)
        return rs
    }

    private fun columnResultSet(
        table: TableName,
        columns: List<JdbcMetadataQuerier.ColumnMetadata>,
    ): ResultSet {
        val rs = mock(ResultSet::class.java)
        if (columns.isEmpty()) {
            `when`(rs.next()).thenReturn(false)
            return rs
        }

        val first = columns.first()
        val second = columns.getOrNull(1)

        `when`(rs.next()).thenReturn(true).thenReturn(second != null).thenReturn(false)
        `when`(rs.getString("TABLE_CAT")).thenReturn(table.catalog)
        `when`(rs.getString("TABLE_SCHEM")).thenReturn(table.schema)
        `when`(rs.getString("TABLE_NAME")).thenReturn(table.name)
        if (second == null) {
            `when`(rs.getString("COLUMN_NAME")).thenReturn(first.name)
            `when`(rs.getString("TYPE_NAME")).thenReturn(first.type.typeName)
            `when`(rs.getInt("DATA_TYPE")).thenReturn(first.type.typeCode)
            `when`(rs.getInt("COLUMN_SIZE")).thenReturn(100)
            `when`(rs.getInt("DECIMAL_DIGITS")).thenReturn(0)
            `when`(rs.getInt("ORDINAL_POSITION")).thenReturn(first.ordinal ?: 1)
        } else {
            `when`(rs.getString("COLUMN_NAME")).thenReturn(first.name).thenReturn(second.name)
            `when`(rs.getString("TYPE_NAME"))
                .thenReturn(first.type.typeName)
                .thenReturn(second.type.typeName)
            `when`(rs.getInt("DATA_TYPE"))
                .thenReturn(first.type.typeCode)
                .thenReturn(second.type.typeCode)
            `when`(rs.getInt("COLUMN_SIZE")).thenReturn(100).thenReturn(100)
            `when`(rs.getInt("DECIMAL_DIGITS")).thenReturn(0).thenReturn(0)
            `when`(rs.getInt("ORDINAL_POSITION"))
                .thenReturn(first.ordinal ?: 1)
                .thenReturn(second.ordinal ?: 2)
        }
        `when`(rs.getString("IS_NULLABLE")).thenReturn("YES")
        return rs
    }

    private fun queryMetadataResultSet(columnName: String, columnLabel: String): ResultSet {
        val rs = mock(ResultSet::class.java)
        val rsmd = mock(ResultSetMetaData::class.java)
        `when`(rs.metaData).thenReturn(rsmd)
        `when`(rsmd.columnCount).thenReturn(1)
        `when`(rsmd.getColumnName(1)).thenReturn(columnName)
        `when`(rsmd.getColumnLabel(1)).thenReturn(columnLabel)
        `when`(rsmd.getColumnTypeName(1)).thenReturn("VARCHAR")
        `when`(rsmd.getColumnType(1)).thenReturn(Types.VARCHAR)
        `when`(rsmd.getPrecision(1)).thenReturn(100)
        `when`(rsmd.getScale(1)).thenReturn(0)
        `when`(rsmd.isNullable(1)).thenReturn(ResultSetMetaData.columnNullable)
        return rs
    }
}
