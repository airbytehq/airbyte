/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata

import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.sql.Connection
import java.sql.PreparedStatement
import java.sql.SQLException
import java.util.ArrayList
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.ArgumentCaptor
import org.mockito.ArgumentMatchers.anyString
import org.mockito.Captor
import org.mockito.InjectMocks
import org.mockito.Mock
import org.mockito.Mockito.*
import org.mockito.MockitoAnnotations

class TeradataSqlOperationsTest {

    @Mock private lateinit var database: JdbcDatabase

    @InjectMocks private lateinit var teradataSqlOperations: TeradataSqlOperations

    @Mock private lateinit var mockConnection: Connection

    @Mock private lateinit var mockPreparedStatement: PreparedStatement

    @Captor private lateinit var stringCaptor: ArgumentCaptor<String>

    @BeforeEach
    @Throws(SQLException::class)
    fun setUp() {
        MockitoAnnotations.openMocks(this)
    }

    @Test
    @Throws(SQLException::class)
    fun testEmptyInsertRecordsInternal() {
        val records: MutableList<AirbyteRecordMessage> = ArrayList()
        val schemaName = "test_schema"
        val tableName = "test_table"
        teradataSqlOperations.insertRecordsInternal(database, records, schemaName, tableName)
    }

    @Test
    @Throws(SQLException::class)
    fun testInsertRecordsInternal() {
        // Arrange
        val record1 = mock(AirbyteRecordMessage::class.java)
        `when`(record1.emittedAt).thenReturn(System.currentTimeMillis())

        val records = listOf(record1)
        val schemaName = "test_schema"
        val tableName = "test_table"
        teradataSqlOperations.insertRecordsInternal(database, records, schemaName, tableName)
    }

    @Test
    @Throws(Exception::class)
    fun testIsSchemaExists() {
        doReturn(1).`when`(database).queryInt(anyString())
        teradataSqlOperations.isSchemaExists(database, "schema")
        verify(database, times(1)).queryInt(stringCaptor.capture())
        assertTrue(stringCaptor.value.contains("SELECT COUNT(1) FROM DBC.Databases"))
    }

    @Test
    @Throws(Exception::class)
    fun testIsSchemaNotExists() {
        doReturn(0).`when`(database).queryInt(anyString())
        teradataSqlOperations.isSchemaExists(database, "schema")
        verify(database, times(1)).queryInt(stringCaptor.capture())
        assertTrue(stringCaptor.value.contains("SELECT COUNT(1) FROM DBC.Databases"))
    }

    @Test
    @Throws(Exception::class)
    fun testCreateSchemaIfNotExists() {
        // Test case where schema does not exist
        doNothing().`when`(database).execute(anyString())
        doReturn(0).`when`(database).queryInt(anyString())
        teradataSqlOperations.createSchemaIfNotExists(database, "schema")
        verify(database, times(1)).queryInt(stringCaptor.capture())
        assertTrue(stringCaptor.value.contains("SELECT COUNT(1) FROM DBC.Databases"))
        verify(database, times(1)).execute(stringCaptor.capture())
        assertTrue(stringCaptor.value.contains("CREATE DATABASE \"schema\""))
    }

    @Test
    @Throws(Exception::class)
    fun testCreateSchemaIfExists() {
        // Test case where schema already exists
        doNothing().`when`(database).execute(anyString())
        doReturn(1).`when`(database).queryInt(anyString())
        teradataSqlOperations.createSchemaIfNotExists(database, "schema")
        verify(database, times(1)).queryInt(stringCaptor.capture())
        assertTrue(stringCaptor.value.contains("SELECT COUNT(1) FROM DBC.Databases"))
        verify(database, times(0)).execute("")
    }

    @Test
    @Throws(Exception::class)
    fun testIsTableExists() {
        doReturn(1).`when`(database).queryInt(anyString())
        teradataSqlOperations.createTableIfNotExists(database, "schema", "table")
        verify(database, times(1)).queryInt(stringCaptor.capture())
        assertTrue(stringCaptor.value.contains("SELECT COUNT(1) FROM DBC.TABLES"))
    }

    @Test
    fun testCreateTableQuery() {
        val query = teradataSqlOperations.createTableQuery(database, "schema", "table")
        assertEquals(
            "CREATE SET TABLE schema.table, FALLBACK ( _airbyte_ab_id VARCHAR(256), _airbyte_data JSON, _airbyte_emitted_at TIMESTAMP(6))  UNIQUE PRIMARY INDEX (_airbyte_ab_id) ",
            query
        )
    }

    @Test
    @Throws(Exception::class)
    fun testCreateTableIfNotExists() {
        // Test case where schema does not exist
        doNothing().`when`(database).execute(anyString())
        doReturn(0).`when`(database).queryInt(anyString())
        teradataSqlOperations.createTableIfNotExists(database, "schema", "table")
        verify(database, times(1)).queryInt(stringCaptor.capture())
        assertTrue(stringCaptor.value.contains("SELECT COUNT(1) FROM DBC.TABLES"))
        verify(database, times(1)).execute(stringCaptor.capture())
        assertTrue(stringCaptor.value.contains("CREATE SET TABLE"))
    }

    @Test
    @Throws(Exception::class)
    fun testCreateTableIfExists() {
        // Test case where schema already exists
        doNothing().`when`(database).execute(anyString())
        doReturn(1).`when`(database).queryInt(anyString())
        teradataSqlOperations.createTableIfNotExists(database, "schema", "table")
        verify(database, times(1)).queryInt(stringCaptor.capture())
        assertTrue(stringCaptor.value.contains("SELECT COUNT(1) FROM DBC.TABLES"))
        verify(database, times(0)).execute("")
    }

    @Test
    @Throws(SQLException::class)
    fun testDropTableIfExists() {
        doNothing().`when`(database).execute(anyString())

        teradataSqlOperations.dropTableIfExists(database, "schema", "table")

        verify(database, times(1)).execute(stringCaptor.capture())
        assertTrue(stringCaptor.value.contains("DROP TABLE schema.table"))
    }

    @Test
    fun testTruncateTableQuery() {
        val query = teradataSqlOperations.truncateTableQuery(database, "schema", "table")
        assertEquals("DELETE schema.table ALL;\n", query)
    }

    @Test
    @Throws(Exception::class)
    fun testExecuteTransactionEmptyQueries() {
        val queries: MutableList<String> = ArrayList()

        // Test case where transaction executes successfully
        doNothing().`when`(database).execute(anyString())

        teradataSqlOperations.executeTransaction(database, queries)

        verify(database, times(0)).execute("")

        // Test case where transaction fails
        doThrow(SQLException("Execution failed")).`when`(database).execute(anyString())
    }

    @Test
    @Throws(Exception::class)
    fun testExecuteTransaction() {
        val queries = listOf("query1;", "query2;")

        // Test case where transaction executes successfully
        doNothing().`when`(database).execute(anyString())

        teradataSqlOperations.executeTransaction(database, queries)

        verify(database, times(1)).execute(stringCaptor.capture())
        assertEquals("query1;query2;", stringCaptor.value)

        // Test case where transaction fails
        doThrow(SQLException("Execution failed")).`when`(database).execute(anyString())
    }
}
