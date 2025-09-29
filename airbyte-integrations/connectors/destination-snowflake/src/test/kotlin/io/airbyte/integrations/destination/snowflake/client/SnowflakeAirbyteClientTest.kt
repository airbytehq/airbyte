/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.client

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.command.Overwrite
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.snowflake.db.ColumnDefinition
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.COUNT_TOTAL_ALIAS
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeDirectLoadSqlGenerator
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
import net.snowflake.client.jdbc.SnowflakeSQLException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class SnowflakeAirbyteClientTest {

    private lateinit var client: SnowflakeAirbyteClient
    private lateinit var dataSource: DataSource
    private lateinit var sqlGenerator: SnowflakeDirectLoadSqlGenerator
    private lateinit var snowflakeColumnUtils: SnowflakeColumnUtils
    private lateinit var snowflakeConfiguration: SnowflakeConfiguration

    @BeforeEach
    fun setup() {
        dataSource = mockk()
        sqlGenerator = mockk(relaxed = true)
        snowflakeColumnUtils = mockk(relaxed = true)
        snowflakeConfiguration = mockk(relaxed = true)
        client =
            SnowflakeAirbyteClient(
                dataSource,
                sqlGenerator,
                snowflakeColumnUtils,
                snowflakeConfiguration
            )
    }

    @Test
    fun testCountTable() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val resultSet =
            mockk<ResultSet> {
                every { next() } returns true andThen false
                every { getLong(COUNT_TOTAL_ALIAS) } returns 1L
            }
        val statement = mockk<Statement> { every { executeQuery(any()) } returns resultSet }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection

        runBlocking {
            val result = client.countTable(tableName)
            assertEquals(1L, result)
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testCountMissingTable() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val statement =
            mockk<Statement> { every { executeQuery(any()) } throws SnowflakeSQLException("test") }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection

        runBlocking {
            val result = client.countTable(tableName)
            assertEquals(null, result)
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testCountTableNoResults() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val resultSet = mockk<ResultSet> { every { next() } returns false }
        val statement = mockk<Statement> { every { executeQuery(any()) } returns resultSet }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection

        runBlocking {
            val result = client.countTable(tableName)
            assertEquals(0L, result)
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testCreateNamespace() {
        val namespace = "namespace"
        val resultSet = mockk<ResultSet>(relaxed = true)
        val statement = mockk<Statement> { every { executeQuery(any()) } returns resultSet }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection

        runBlocking {
            client.createNamespace(namespace)
            verify(exactly = 1) { sqlGenerator.createNamespace(namespace) }
            verify(exactly = 1) { sqlGenerator.createFileFormat(namespace) }
            verify(exactly = 2) { mockConnection.close() }
        }
    }

    @Test
    fun testCreateTable() {
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)
        val stream = mockk<DestinationStream>()
        val tableName = TableName(namespace = "namespace", name = "name")
        val resultSet = mockk<ResultSet>(relaxed = true)
        val statement = mockk<Statement> { every { executeQuery(any()) } returns resultSet }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection

        runBlocking {
            client.createTable(
                stream = stream,
                tableName = tableName,
                columnNameMapping = columnNameMapping,
                replace = true,
            )
            verify(exactly = 1) {
                sqlGenerator.createTable(stream, tableName, columnNameMapping, true)
            }
            verify(exactly = 1) { sqlGenerator.createSnowflakeStage(tableName) }
            verify(exactly = 2) { mockConnection.close() }
        }
    }

    @Test
    fun testCopyTable() {
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)
        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val destinationTableName = TableName(namespace = "namespace", name = "destination")
        val resultSet = mockk<ResultSet>(relaxed = true)
        val statement = mockk<Statement> { every { executeQuery(any()) } returns resultSet }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection

        runBlocking {
            client.copyTable(
                columnNameMapping = columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = destinationTableName,
            )
            verify(exactly = 1) {
                sqlGenerator.copyTable(columnNameMapping, sourceTableName, destinationTableName)
            }
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testUpsertTable() {
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)
        val sourceTableName = TableName(namespace = "namespace", name = "source")
        val destinationTableName = TableName(namespace = "namespace", name = "destination")
        val stream = mockk<DestinationStream>()
        val resultSet = mockk<ResultSet>(relaxed = true)
        val statement = mockk<Statement> { every { executeQuery(any()) } returns resultSet }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection

        runBlocking {
            client.upsertTable(
                stream = stream,
                columnNameMapping = columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = destinationTableName,
            )
            verify(exactly = 1) {
                sqlGenerator.upsertTable(
                    stream,
                    columnNameMapping,
                    sourceTableName,
                    destinationTableName
                )
            }
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testDropTable() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val resultSet = mockk<ResultSet>(relaxed = true)
        val statement = mockk<Statement> { every { executeQuery(any()) } returns resultSet }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection

        runBlocking {
            client.dropTable(tableName)
            verify(exactly = 1) { sqlGenerator.dropTable(tableName) }
            verify(exactly = 1) { sqlGenerator.dropStage(tableName) }
            verify(exactly = 2) { mockConnection.close() }
        }
    }

    @Test
    fun testGetGenerationId() {
        val generationId = 2L
        val tableName = TableName(namespace = "namespace", name = "name")
        val resultSet =
            mockk<ResultSet> {
                every { next() } returns true
                every { getLong(COLUMN_NAME_AB_GENERATION_ID) } returns generationId
            }
        val statement = mockk<Statement> { every { executeQuery(any()) } returns resultSet }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection

        runBlocking {
            val result = client.getGenerationId(tableName)
            assertEquals(generationId, result)
            verify(exactly = 1) { sqlGenerator.getGenerationId(tableName) }
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testGetGenerationIdNoResult() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val resultSet = mockk<ResultSet> { every { next() } returns false }
        val statement = mockk<Statement> { every { executeQuery(any()) } returns resultSet }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection

        runBlocking {
            val result = client.getGenerationId(tableName)
            assertEquals(0L, result)
            verify(exactly = 1) { sqlGenerator.getGenerationId(tableName) }
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testGetGenerationIdError() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val resultSet = mockk<ResultSet> { every { next() } throws SQLException("error") }
        val statement = mockk<Statement> { every { executeQuery(any()) } returns resultSet }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection

        runBlocking {
            val result = client.getGenerationId(tableName)
            assertEquals(0L, result)
            verify(exactly = 1) { sqlGenerator.getGenerationId(tableName) }
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testCreateStaging() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val resultSet = mockk<ResultSet>(relaxed = true)
        val statement = mockk<Statement> { every { executeQuery(any()) } returns resultSet }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection

        runBlocking {
            client.createSnowflakeStage(tableName)
            verify(exactly = 1) { sqlGenerator.createSnowflakeStage(tableName) }
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testPutInStaging() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val tempFilePath = "/some/file/path.csv"
        val resultSet = mockk<ResultSet>(relaxed = true)
        val statement = mockk<Statement> { every { executeQuery(any()) } returns resultSet }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection

        runBlocking {
            client.putInStage(tableName, tempFilePath)
            verify(exactly = 1) { sqlGenerator.putInStage(tableName, tempFilePath) }
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testCopyFromStaging() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val resultSet = mockk<ResultSet>(relaxed = true)
        val statement = mockk<Statement> { every { executeQuery(any()) } returns resultSet }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection

        runBlocking {
            client.copyFromStage(tableName)
            verify(exactly = 1) { sqlGenerator.copyFromStage(tableName) }
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
                every { getString(DESCRIBE_TABLE_COLUMN_NAME_FIELD) } returns
                    column1 andThen
                    column2
            }
        val statement = mockk<Statement> { every { executeQuery(any()) } returns resultSet }
        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
            }

        every { dataSource.connection } returns mockConnection

        runBlocking {
            val columns = client.describeTable(tableName)
            assertEquals(listOf(column1, column2), columns)
            verify(exactly = 1) { sqlGenerator.showColumns(tableName) }
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun `getColumnsFromDb should return correct column definitions`() {
        val tableName = TableName("test_namespace", "test_table")
        val resultSet = mockk<ResultSet>()
        every { resultSet.next() } returns true andThen true andThen true andThen false
        every { resultSet.getString("name") } returns
            "COL1" andThen
            "_AIRBYTE_RAW_ID" andThen
            "COL2"
        every { resultSet.getString("type") } returns
            "VARCHAR(255)" andThen
            "TEXT" andThen
            "NUMBER(38,0)"
        every { resultSet.getString("null?") } returns "Y" andThen "N" andThen "N"

        val statement = mockk<Statement>()
        every { statement.executeQuery(any()) } returns resultSet

        val connection = mockk<Connection>()
        every { connection.createStatement() } returns statement
        every { connection.close() } just Runs

        every { dataSource.connection } returns connection

        val result = client.getColumnsFromDb(tableName)

        val expectedColumns =
            setOf(
                ColumnDefinition("COL1", "VARCHAR", true),
                ColumnDefinition("_AIRBYTE_RAW_ID", "TEXT", false),
                ColumnDefinition("COL2", "NUMBER", false)
            )

        assertEquals(expectedColumns, result)
    }

    @Test
    fun `getColumnsFromStream should return correct column definitions`() {
        val schema = mockk<AirbyteType>()
        val stream =
            DestinationStream(
                unmappedNamespace = "test_namespace",
                unmappedName = "test_stream",
                importType = Overwrite,
                schema = schema,
                generationId = 1,
                minimumGenerationId = 1,
                syncId = 1,
                namespaceMapper = NamespaceMapper(NamespaceDefinitionType.DESTINATION)
            )
        val columnNameMapping =
            ColumnNameMapping(
                mapOf(
                    "col1" to "COL1_MAPPED",
                    "col2" to "COL2_MAPPED",
                )
            )

        val col1FieldType = mockk<FieldType>()
        every { col1FieldType.type } returns mockk()
        every { col1FieldType.nullable } returns true

        val col2FieldType = mockk<FieldType>()
        every { col2FieldType.type } returns mockk()
        every { col2FieldType.nullable } returns false

        every { schema.asColumns() } returns
            linkedMapOf("col1" to col1FieldType, "col2" to col2FieldType)
        every { snowflakeColumnUtils.toDialectType(col1FieldType.type) } returns "VARCHAR(255)"
        every { snowflakeColumnUtils.toDialectType(col2FieldType.type) } returns "NUMBER(38,0)"

        val result = client.getColumnsFromStream(stream, columnNameMapping)

        val expectedColumns =
            setOf(
                ColumnDefinition("COL1_MAPPED", "VARCHAR", true),
                ColumnDefinition("COL2_MAPPED", "NUMBER", false)
            )

        assertEquals(expectedColumns, result)
    }

    @Test
    fun `generateSchemaChanges should correctly identify changes`() {
        val columnsInDb =
            setOf(
                ColumnDefinition("COL1", "VARCHAR", true),
                ColumnDefinition("COL2", "NUMBER", false),
                ColumnDefinition("COL3", "BOOLEAN", true)
            )
        val columnsInStream =
            setOf(
                ColumnDefinition("COL1", "VARCHAR", true), // Unchanged
                ColumnDefinition("COL3", "TEXT", true), // Modified
                ColumnDefinition("COL4", "DATE", false) // Added
            )

        val (added, deleted, modified) = client.generateSchemaChanges(columnsInDb, columnsInStream)

        assertEquals(1, added.size)
        assertEquals("COL4", added.first().name)
        assertEquals(1, deleted.size)
        assertEquals("COL2", deleted.first().name)
        assertEquals(1, modified.size)
        assertEquals("COL3", modified.first().name)
    }

    @Test
    fun testCreateNamespaceWithNetworkFailure() {
        val namespace = "test_namespace"
        val sql = "CREATE SCHEMA IF NOT EXISTS test_namespace"

        every { sqlGenerator.createNamespace(namespace) } returns sql

        val connection = mockk<Connection>()
        val statement = mockk<Statement>()

        every { dataSource.connection } returns connection
        every { connection.createStatement() } returns statement
        every { statement.executeQuery(sql) } throws SQLException("Network error", "08S01")
        every { statement.close() } just Runs
        every { connection.close() } just Runs

        runBlocking {
            try {
                client.createNamespace(namespace)
                assert(false) { "Expected SQLException" }
            } catch (e: SQLException) {
                assertEquals("Network error", e.message)
                assertEquals("08S01", e.sqlState)
            }
        }
    }

    @Test
    fun testCountTableWithClosedConnection() {
        val tableName = TableName("namespace", "table")
        val sql = "SELECT COUNT(*) FROM namespace.table"

        every { sqlGenerator.countTable(tableName) } returns sql

        val connection = mockk<Connection>()

        every { dataSource.connection } returns connection
        every { connection.isClosed } returns true
        every { connection.close() } just Runs

        runBlocking {
            try {
                client.countTable(tableName)
                assert(false) { "Expected error for closed connection" }
            } catch (e: Exception) {
                // Expected - connection was closed
            }
        }
    }

    @Test
    fun testExecuteWithTransientNetworkError() {
        val connection = mockk<Connection>()
        val statement = mockk<Statement>()
        val sql = "INSERT INTO table VALUES (1)"

        every { dataSource.connection } returns connection
        every { connection.createStatement() } returns statement

        // Simulate transient network error (typically retryable)
        every { statement.executeQuery(sql) } throws
            SnowflakeSQLException("Request reached its timeout", "HY000", 390114)
        every { statement.close() } just Runs
        every { connection.close() } just Runs

        try {
            client.execute(sql)
            assert(false) { "Expected SnowflakeSQLException" }
        } catch (e: SnowflakeSQLException) {
            assertEquals(390114, e.errorCode) // NETWORK_ERROR
            // In production, this would typically trigger a retry
        }
    }
}
