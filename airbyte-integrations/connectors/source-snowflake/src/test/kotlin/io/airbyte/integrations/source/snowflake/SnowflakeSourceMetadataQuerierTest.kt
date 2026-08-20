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
        column: JdbcMetadataQuerier.ColumnMetadata,
    ): ResultSet {
        val rs = mock(ResultSet::class.java)
        `when`(rs.next()).thenReturn(true, false)
        `when`(rs.getString("TABLE_CAT")).thenReturn(table.catalog)
        `when`(rs.getString("TABLE_SCHEM")).thenReturn(table.schema)
        `when`(rs.getString("TABLE_NAME")).thenReturn(table.name)
        `when`(rs.getString("COLUMN_NAME")).thenReturn(column.name)
        `when`(rs.getString("TYPE_NAME")).thenReturn(column.type.typeName)
        `when`(rs.getInt("DATA_TYPE")).thenReturn(column.type.typeCode)
        `when`(rs.getInt("COLUMN_SIZE")).thenReturn(column.type.precision ?: 0)
        `when`(rs.getInt("DECIMAL_DIGITS")).thenReturn(column.type.scale ?: 0)
        `when`(rs.getString("IS_NULLABLE")).thenReturn("YES")
        `when`(rs.getInt("ORDINAL_POSITION")).thenReturn(column.ordinal ?: 1)
        return rs
    }
}
