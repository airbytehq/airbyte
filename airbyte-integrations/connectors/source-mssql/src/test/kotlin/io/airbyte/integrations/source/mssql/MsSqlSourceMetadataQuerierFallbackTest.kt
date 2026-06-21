package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.TableName
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.mockk.*
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import java.sql.Connection
import java.sql.DatabaseMetaData
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.sql.Statement

class MsSqlSourceMetadataQuerierFallbackTest {

    @Test
    fun testPrimaryKeysFallbackWhenInsufficientFilteringCondition() {
        val mockBase = mockk<JdbcMetadataQuerier>()
        val mockConn = mockk<Connection>()
        val mockStatement = mockk<Statement>()
        val mockPreparedStatement = mockk<PreparedStatement>()
        val mockResultSet = mockk<ResultSet>()
        val mockDatabaseMetaData = mockk<DatabaseMetaData>()
        val mockTablesResultSet = mockk<ResultSet>()

        every { mockBase.conn } returns mockConn

        val mockConfig = mockk<MsSqlServerSourceConfiguration>()
        every { mockConfig.global } returns false
        every { mockConfig.namespaces } returns setOf("dbo")
        every { mockBase.config } returns mockConfig

        // Mock DatabaseMetaData and Table discovery
        every { mockConn.metaData } returns mockDatabaseMetaData
        every { mockConn.catalog } returns "db"
        every { mockConn.close() } just Runs
        every { mockDatabaseMetaData.getTables(any(), any(), any(), any()) } returns mockTablesResultSet
        every { mockTablesResultSet.next() } returnsMany listOf(true, false, false)
        every { mockTablesResultSet.getString("TABLE_CAT") } returns "db"
        every { mockTablesResultSet.getString("TABLE_SCHEM") } returns "dbo"
        every { mockTablesResultSet.getString("TABLE_NAME") } returns "test_table"
        every { mockTablesResultSet.getString("TABLE_TYPE") } returns "TABLE"
        every { mockTablesResultSet.close() } just Runs

        // Throw the specific exception on the bulk query
        every { mockConn.createStatement() } returns mockStatement
        every { mockStatement.executeQuery(any()) } throws RuntimeException("Insufficient filtering condition")
        every { mockStatement.close() } just Runs

        // Mock the PreparedStatement fallback
        every { mockConn.prepareStatement(any()) } returns mockPreparedStatement
        every { mockPreparedStatement.setString(any(), any()) } just Runs
        every { mockPreparedStatement.executeQuery() } returns mockResultSet
        every { mockPreparedStatement.close() } just Runs

        // Provide exactly one row in the result set for the fallback query
        every { mockResultSet.next() } returnsMany listOf(true, false)
        every { mockResultSet.getString("table_schema") } returns "dbo"
        every { mockResultSet.getString("table_name") } returns "test_table"
        every { mockResultSet.getString("constraint_name") } returns "PK_test"
        every { mockResultSet.getInt("ordinal_position") } returns 1
        every { mockResultSet.getString("column_name") } returns "id"
        every { mockResultSet.wasNull() } returns false
        every { mockResultSet.close() } just Runs

        val metadataQuerier = MsSqlSourceMetadataQuerier(mockBase, null)
        val spyQuerier = spyk(metadataQuerier)

        // Stub streamNamespaces to return dbo
        every { spyQuerier.streamNamespaces() } returns listOf("dbo")

        val mockTable = TableName("db", "dbo", "test_table", "TABLE")
        val primaryKeysMap = spyQuerier.memoizedPrimaryKeys

        assertNotNull(primaryKeysMap)
        assertEquals(1, primaryKeysMap.size)
        assertTrue(primaryKeysMap.containsKey(mockTable))
        assertEquals(listOf(listOf("id")), primaryKeysMap[mockTable])
    }

    @Test
    fun testClusteredIndexKeysFallbackWhenInsufficientFilteringCondition() {
        val mockBase = mockk<JdbcMetadataQuerier>()
        val mockConn = mockk<Connection>()
        val mockStatement = mockk<Statement>()
        val mockPreparedStatement = mockk<PreparedStatement>()
        val mockResultSet = mockk<ResultSet>()
        val mockDatabaseMetaData = mockk<DatabaseMetaData>()
        val mockTablesResultSet = mockk<ResultSet>()

        every { mockBase.conn } returns mockConn

        val mockConfig = mockk<MsSqlServerSourceConfiguration>()
        every { mockConfig.global } returns false
        every { mockConfig.namespaces } returns setOf("dbo")
        every { mockBase.config } returns mockConfig

        // Mock DatabaseMetaData and Table discovery
        every { mockConn.metaData } returns mockDatabaseMetaData
        every { mockConn.catalog } returns "db"
        every { mockConn.close() } just Runs
        every { mockDatabaseMetaData.getTables(any(), any(), any(), any()) } returns mockTablesResultSet
        every { mockTablesResultSet.next() } returnsMany listOf(true, false, false)
        every { mockTablesResultSet.getString("TABLE_CAT") } returns "db"
        every { mockTablesResultSet.getString("TABLE_SCHEM") } returns "dbo"
        every { mockTablesResultSet.getString("TABLE_NAME") } returns "test_table"
        every { mockTablesResultSet.getString("TABLE_TYPE") } returns "TABLE"
        every { mockTablesResultSet.close() } just Runs

        // First createStatement call returns a statement that throws
        every { mockConn.createStatement() } returns mockStatement
        every { mockStatement.executeQuery(any()) } throws RuntimeException("Insufficient filtering condition")
        every { mockStatement.close() } just Runs

        // PrepareStatement is called during fallback
        every { mockConn.prepareStatement(any()) } returns mockPreparedStatement
        every { mockPreparedStatement.setString(any(), any()) } just Runs
        every { mockPreparedStatement.executeQuery() } returns mockResultSet
        every { mockPreparedStatement.close() } just Runs

        every { mockResultSet.next() } returnsMany listOf(true, false)
        every { mockResultSet.getString("table_schema") } returns "dbo"
        every { mockResultSet.getString("table_name") } returns "test_table"
        every { mockResultSet.getString("index_name") } returns "IDX_test"
        every { mockResultSet.getInt("key_ordinal") } returns 1
        every { mockResultSet.getString("column_name") } returns "id"
        every { mockResultSet.wasNull() } returns false
        every { mockResultSet.close() } just Runs

        val metadataQuerier = MsSqlSourceMetadataQuerier(mockBase, null)
        val spyQuerier = spyk(metadataQuerier)

        // Stub streamNamespaces to return dbo
        every { spyQuerier.streamNamespaces() } returns listOf("dbo")

        val mockTable = TableName("db", "dbo", "test_table", "TABLE")
        val clusteredIndexMap = spyQuerier.memoizedClusteredIndexKeys

        assertNotNull(clusteredIndexMap)
        assertEquals(1, clusteredIndexMap.size)
        assertTrue(clusteredIndexMap.containsKey(mockTable))
        assertEquals(listOf(listOf("id")), clusteredIndexMap[mockTable])
    }
}
