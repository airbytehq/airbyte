/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.client

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.postgres.sql.PostgresDirectLoadSqlGenerator
import io.mockk.Runs
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.verify
import java.sql.Connection
import java.sql.ResultSet
import java.sql.SQLException
import java.sql.Statement
import javax.sql.DataSource
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class PostgresAirbyteClientTest {

    private lateinit var client: PostgresAirbyteClient
    private lateinit var dataSource: DataSource
    private lateinit var sqlGenerator: PostgresDirectLoadSqlGenerator

    companion object {
        private const val MOCK_SQL_QUERY = "MOCK_SQL_QUERY"
    }

    @BeforeEach
    fun setup() {
        dataSource = mockk()
        sqlGenerator = mockk()
        client = PostgresAirbyteClient(dataSource, sqlGenerator)
    }

    @Test
    fun testCountTable() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val resultSet =
            mockk<ResultSet> {
                every { next() } returns true
                every { getLong(COUNT_TOTAL_ALIAS) } returns 42L
            }
        val statement =
            mockk<Statement> {
                every { executeQuery(any()) } returns resultSet
                every { close() } just Runs
            }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection
        every { sqlGenerator.countTable(tableName) } returns MOCK_SQL_QUERY

        runBlocking {
            val result = client.countTable(tableName)
            assertEquals(42L, result)
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testCountTableNoResults() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val resultSet = mockk<ResultSet> { every { next() } returns false }
        val statement =
            mockk<Statement> {
                every { executeQuery(any()) } returns resultSet
                every { close() } just Runs
            }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection
        every { sqlGenerator.countTable(tableName) } returns MOCK_SQL_QUERY

        runBlocking {
            val result = client.countTable(tableName)
            assertEquals(0L, result)
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testCountMissingTable() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val statement =
            mockk<Statement> { every { executeQuery(any()) } throws SQLException("table does not exist") }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection

        runBlocking {
            val result = client.countTable(tableName)
            assertNull(result)
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testCreateNamespace() {
        val namespace = "test_namespace"
        val statement =
            mockk<Statement> {
                every { execute(any()) } returns true
                every { close() } just Runs
            }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection
        every { sqlGenerator.createNamespace(namespace) } returns MOCK_SQL_QUERY

        runBlocking {
            client.createNamespace(namespace)
            verify(exactly = 1) { statement.execute(MOCK_SQL_QUERY) }
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testCreateTable() {
        val stream = mockk<DestinationStream>()
        val tableName = TableName(namespace = "namespace", name = "name")
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)
        val statement =
            mockk<Statement> {
                every { execute(any()) } returns true
                every { close() } just Runs
            }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection
        every { sqlGenerator.createTable(stream, tableName, columnNameMapping, true) } returns MOCK_SQL_QUERY

        runBlocking {
            client.createTable(
                stream = stream,
                tableName = tableName,
                columnNameMapping = columnNameMapping,
                replace = true
            )
            verify(exactly = 1) { statement.execute(MOCK_SQL_QUERY) }
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testOverwriteTable() {
        val sourceTableName = TableName(namespace = "source_ns", name = "source")
        val targetTableName = TableName(namespace = "target_ns", name = "target")
        val statement =
            mockk<Statement> {
                every { execute(any()) } returns true
                every { close() } just Runs
            }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection
        every { sqlGenerator.overwriteTable(sourceTableName, targetTableName) } returns MOCK_SQL_QUERY

        runBlocking {
            client.overwriteTable(sourceTableName, targetTableName)
            verify(exactly = 1) { statement.execute(MOCK_SQL_QUERY) }
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testCopyTable() {
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)
        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val targetTableName = TableName(namespace = "namespace", name = "target")
        val statement =
            mockk<Statement> {
                every { execute(any()) } returns true
                every { close() } just Runs
            }

        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }
        every { dataSource.connection } returns mockConnection
        every { sqlGenerator.copyTable(columnNameMapping, sourceTableName, targetTableName) } returns MOCK_SQL_QUERY

        runBlocking {
            client.copyTable(
                columnNameMapping = columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = targetTableName
            )
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testUpsertTable() {
        val stream = mockk<DestinationStream>()
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)
        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val targetTableName = TableName(namespace = "namespace", name = "target")
        val statement =
            mockk<Statement> {
                every { execute(any()) } returns true
                every { close() } just Runs
            }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection
        every { sqlGenerator.upsertTable(stream, columnNameMapping, sourceTableName, targetTableName) } returns MOCK_SQL_QUERY

        runBlocking {
            client.upsertTable(
                stream = stream,
                columnNameMapping = columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = targetTableName
            )
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testDropTable() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val statement =
            mockk<Statement> {
                every { execute(any()) } returns true
                every { close() } just Runs
            }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection
        every { sqlGenerator.dropTable(tableName) } returns MOCK_SQL_QUERY

        runBlocking {
            client.dropTable(tableName)
            verify(exactly = 1) { statement.execute(MOCK_SQL_QUERY) }
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testGetGenerationId() {
        val generationId = 123L
        val tableName = TableName(namespace = "namespace", name = "name")
        val resultSet =
            mockk<ResultSet> {
                every { next() } returns true
                every { getLong(COLUMN_NAME_AB_GENERATION_ID) } returns generationId
            }
        val statement =
            mockk<Statement> {
                every { executeQuery(any()) } returns resultSet
                every { close() } just Runs
            }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection
        every { sqlGenerator.getGenerationId(tableName) } returns MOCK_SQL_QUERY

        runBlocking {
            val result = client.getGenerationId(tableName)
            assertEquals(generationId, result)
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testGetGenerationIdNoResult() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val resultSet =
            mockk<ResultSet> {
                every { next() } returns false
            }
        val statement =
            mockk<Statement> {
                every { executeQuery(any()) } returns resultSet
                every { close() } just Runs
            }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection
        every { sqlGenerator.getGenerationId(tableName) } returns MOCK_SQL_QUERY

        runBlocking {
            val result = client.getGenerationId(tableName)
            assertEquals(0, result)
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testGetGenerationIdError() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val statement =
            mockk<Statement> { every { executeQuery(any()) } throws SQLException("error") }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection
        every { sqlGenerator.getGenerationId(tableName) } returns MOCK_SQL_QUERY

        runBlocking {
            val result = client.getGenerationId(tableName)
            assertEquals(0L, result)
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testDescribeTable() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val column1 = "column1"
        val column2 = "column2"
        val resultSet =
            mockk<ResultSet> {
                every { next() } returns true andThen true andThen false
                every { getString("column_name") } returns column1 andThen column2
            }
        val statement =
            mockk<Statement> {
                every { executeQuery(any()) } returns resultSet
                every { close() } just Runs
            }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection
        every { sqlGenerator.getTableSchema(tableName) } returns MOCK_SQL_QUERY

        val columns = client.describeTable(tableName)
        assertEquals(listOf(column1, column2), columns)
        verify(exactly = 1) { sqlGenerator.getTableSchema(tableName) }
        verify(exactly = 1) { mockConnection.close() }
    }
}
