/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.client

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.command.Overwrite
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.schema.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.snowflake.db.ColumnDefinition
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.COUNT_TOTAL_ALIAS
import io.airbyte.integrations.destination.snowflake.sql.ColumnAndType
import io.airbyte.integrations.destination.snowflake.sql.DEFAULT_COLUMNS
import io.airbyte.integrations.destination.snowflake.sql.QUOTE
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeDirectLoadSqlGenerator
import io.mockk.Runs
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.verify
import java.sql.Connection
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.sql.SQLException
import java.sql.Statement
import javax.sql.DataSource
import kotlinx.coroutines.runBlocking
import net.snowflake.client.jdbc.SnowflakeSQLException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

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
        snowflakeColumnUtils =
            mockk(relaxed = true) {
                every { formatColumnName(any()) } answers
                    {
                        firstArg<String>().toSnowflakeCompatibleName()
                    }
                every { getFormattedDefaultColumnNames(any()) } returns
                    DEFAULT_COLUMNS.map { it.columnName.toSnowflakeCompatibleName() }
            }
        snowflakeConfiguration =
            mockk(relaxed = true) { every { database } returns "test_database" }
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

        runBlocking {
            val result = client.countTable(tableName)
            assertEquals(0L, result)
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testCreateNamespace() {
        val namespace = "namespace"

        // Mock for schema check - schema doesn't exist
        val schemaCheckResultSet =
            mockk<ResultSet> {
                every { next() } returns true
                every { getBoolean("SCHEMA_EXISTS") } returns false
                every { close() } just Runs
            }

        // Mock for other operations
        val createResultSet = mockk<ResultSet>(relaxed = true)

        val preparedStatement =
            mockk<PreparedStatement>(relaxed = true) {
                every { executeQuery() } returns schemaCheckResultSet
                every { close() } just Runs
            }

        val statement =
            mockk<Statement> {
                every { executeQuery(any()) } returns createResultSet
                every { close() } just Runs
            }

        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { createStatement() } returns statement
                every { prepareStatement(any()) } returns preparedStatement
            }

        every { dataSource.connection } returns mockConnection
        runBlocking {
            client.createNamespace(namespace)
            verify(exactly = 1) { sqlGenerator.createNamespace(namespace) }
            verify(exactly = 1) { preparedStatement.close() }
            verify(exactly = 1) { statement.close() }
            verify(exactly = 2) { mockConnection.close() }
        }
    }

    @Test
    fun testCreateNamespaceWhenAlreadyExists() {
        val namespace = "namespace"

        // Mock for schema check - schema already exists
        val schemaCheckResultSet =
            mockk<ResultSet> {
                every { next() } returns true
                every { getBoolean("SCHEMA_EXISTS") } returns true
                every { close() } just Runs
            }

        val preparedStatement =
            mockk<PreparedStatement>(relaxed = true) {
                every { executeQuery() } returns schemaCheckResultSet
                every { close() } just Runs
            }

        val mockConnection =
            mockk<Connection> {
                every { close() } just Runs
                every { prepareStatement(any()) } returns preparedStatement
            }

        every { dataSource.connection } returns mockConnection

        runBlocking {
            client.createNamespace(namespace)
            verify(exactly = 0) {
                sqlGenerator.createNamespace(namespace)
            } // Should NOT create schema
            verify(exactly = 1) { preparedStatement.close() }
            verify(exactly = 1) { mockConnection.close() } // Only 2 closes: check + format
        }
    }

    @Test
    fun testCreateTable() {
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)
        val stream = mockk<DestinationStream>()
        val tableName = TableName(namespace = "namespace", name = "name")
        val resultSet = mockk<ResultSet>(relaxed = true)
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

        runBlocking {
            client.dropTable(tableName)
            verify(exactly = 1) { sqlGenerator.dropTable(tableName) }
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testGetGenerationId() {
        val generationId = 2L
        val tableName = TableName(namespace = "namespace", name = "name")
        val generationIdColumnName = COLUMN_NAME_AB_GENERATION_ID.toSnowflakeCompatibleName()
        val resultSet =
            mockk<ResultSet> {
                every { next() } returns true
                every { getLong(generationIdColumnName) } returns generationId
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
        every { snowflakeColumnUtils.getGenerationIdColumnName() } returns generationIdColumnName
        every { sqlGenerator.getGenerationId(tableName) } returns
            "SELECT $generationIdColumnName FROM ${tableName.toPrettyString(QUOTE)}"

        runBlocking {
            val result = client.getGenerationId(tableName)
            assertEquals(generationId, result)
            verify(exactly = 1) { sqlGenerator.getGenerationId(tableName) }
            verify(exactly = 1) { statement.close() }
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

        runBlocking {
            client.copyFromStage(tableName, "test.csv.gz")
            verify(exactly = 1) { sqlGenerator.copyFromStage(tableName, "test.csv.gz") }
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testDescribeTable() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val column1 = "column1"
        val column1Type = """{"type":"VARIANT","nullable":false}"""
        val column2 = "column2"
        val column2Type =
            """{"type":"TEXT","length":16777216,"byteLength":16777216,"nullable":false,"fixed":false}"""
        val resultSet =
            mockk<ResultSet> {
                every { next() } returns true andThen true andThen false
                every { getString(DESCRIBE_TABLE_COLUMN_NAME_FIELD) } returns
                    column1 andThen
                    column2
                every { getString(DESCRIBE_TABLE_COLUMN_TYPE_FIELD) } returns
                    column1Type andThen
                    column2Type
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
        val expectedColumns = linkedMapOf(column1 to "VARIANT", column2 to "TEXT")

        every { dataSource.connection } returns mockConnection

        runBlocking {
            val columns = client.describeTable(tableName)
            assertEquals(expectedColumns, columns)
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
            COLUMN_NAME_AB_RAW_ID.toSnowflakeCompatibleName() andThen
            "COL2"
        every { resultSet.getString("type") } returns "VARCHAR(255)" andThen "NUMBER(38,0)"
        every { resultSet.getString("null?") } returns "Y" andThen "N" andThen "N"

        val statement =
            mockk<Statement> {
                every { executeQuery(any()) } returns resultSet
                every { close() } just Runs
            }

        val connection = mockk<Connection>()
        every { connection.createStatement() } returns statement
        every { connection.close() } just Runs

        every { dataSource.connection } returns connection

        val result = client.getColumnsFromDb(tableName)

        val expectedColumns =
            mapOf(
                "COL1" to ColumnType("VARCHAR", true),
                "COL2" to ColumnType("NUMBER", false),
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

        val col2FieldType = mockk<FieldType>()
        every { col2FieldType.type } returns mockk()

        every { schema.asColumns() } returns
            linkedMapOf("col1" to col1FieldType, "col2" to col2FieldType)
        every { snowflakeColumnUtils.toDialectType(col1FieldType.type) } returns "VARCHAR(255)"
        every { snowflakeColumnUtils.toDialectType(col2FieldType.type) } returns "NUMBER(38,0)"
        every { snowflakeColumnUtils.columnsAndTypes(any(), any()) } returns
            listOf(ColumnAndType("COL1_MAPPED", "VARCHAR"), ColumnAndType("COL2_MAPPED", "NUMBER"))
        every { snowflakeColumnUtils.formatColumnName(any(), false) } answers
            {
                firstArg<String>().toSnowflakeCompatibleName()
            }

        val result = client.getColumnsFromStream(stream, columnNameMapping)

        val expectedColumns =
            mapOf(
                "COL1_MAPPED" to ColumnType("VARCHAR", true),
                "COL2_MAPPED" to ColumnType("NUMBER", true),
            )

        assertEquals(expectedColumns, result)
    }

    @Test
    fun `generateSchemaChanges should correctly identify changes`() {
        val columnsInDb =
            setOf(
                ColumnDefinition("COL1", "VARCHAR"),
                ColumnDefinition("COL2", "NUMBER"),
                ColumnDefinition("COL3", "BOOLEAN")
            )
        val columnsInStream =
            setOf(
                ColumnDefinition("COL1", "VARCHAR"), // Unchanged
                ColumnDefinition("COL3", "TEXT"), // Modified
                ColumnDefinition("COL4", "DATE") // Added
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
        val sql = "CREATE SCHEMA test_namespace"

        every { sqlGenerator.createNamespace(namespace) } returns sql

        // Mock for schema check - should fail and throw exception
        val schemaCheckResultSet =
            mockk<ResultSet> {
                every { next() } returns true
                every { getBoolean("SCHEMA_EXISTS") } returns false
                every { close() } just Runs
            }

        val preparedStatement =
            mockk<PreparedStatement>(relaxed = true) {
                every { executeQuery() } returns schemaCheckResultSet
                every { close() } just Runs
            }

        val statement =
            mockk<Statement> {
                every { executeQuery(any()) } throws SQLException("Network error", "08S01")
                every { close() } just Runs
            }

        val connection =
            mockk<Connection> {
                every { createStatement() } returns statement
                every { prepareStatement(any()) } returns preparedStatement
                every { close() } just Runs
            }

        every { dataSource.connection } returns connection

        runBlocking {
            try {
                client.createNamespace(namespace)
                assert(false) { "Expected SQLException" }
            } catch (e: SQLException) {
                assertEquals("Network error", e.message)
                assertEquals("08S01", e.sqlState)
            }
            verify(exactly = 1) { preparedStatement.close() }
            verify(exactly = 1) { statement.close() }
            verify(exactly = 2) { connection.close() }
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
            } catch (_: Exception) {
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
        every { statement.close() } just Runs

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

    @Test
    fun testExecuteWithNoPrivilegesError() {
        val connection = mockk<Connection>()
        val statement = mockk<Statement>()
        val sql = "CREATE TABLE test_table (id INT)"

        every { dataSource.connection } returns connection
        every { connection.createStatement() } returns statement
        every { statement.close() } just Runs

        // Simulate permission error matching the user's case
        every { statement.executeQuery(sql) } throws
            SnowflakeSQLException(
                "SQL compilation error:\n" +
                    "Table 'APXT_REDLINING__CONTRACT_AGREEMENT__HISTORY' already exists, " +
                    "but current role has no privileges on it. " +
                    "If this is unexpected and you cannot resolve this problem, " +
                    "contact your system administrator. " +
                    "ACCOUNTADMIN role may be required to manage the privileges on the object."
            )
        every { connection.close() } just Runs

        val exception = assertThrows<ConfigErrorException> { client.execute(sql) }

        // Verify the error message was wrapped as ConfigErrorException with original message
        assertTrue(exception.message!!.contains("current role has no privileges on it"))
        // Verify the cause is the original SnowflakeSQLException
        assertTrue(exception.cause is SnowflakeSQLException)
    }

    @Test
    fun testExecuteWithNonPermissionError() {
        val connection = mockk<Connection>()
        val statement = mockk<Statement>()
        val sql = "SELECT * FROM nonexistent_table"

        every { dataSource.connection } returns connection
        every { connection.createStatement() } returns statement
        every { statement.close() } just Runs

        // Simulate non-permission error (e.g., table not found)
        every { statement.executeQuery(sql) } throws
            SnowflakeSQLException("Table 'NONEXISTENT_TABLE' does not exist")
        every { connection.close() } just Runs

        // Non-permission errors should be thrown as-is, not wrapped
        val exception = assertThrows<SnowflakeSQLException> { client.execute(sql) }

        assertEquals("Table 'NONEXISTENT_TABLE' does not exist", exception.message)
    }

    @Test
    fun testCreateNamespaceWithPermissionError() {
        val namespace = "test_namespace"
        val sql = "CREATE SCHEMA test_namespace"

        every { sqlGenerator.createNamespace(namespace) } returns sql

        // Mock for schema check - returns false (schema doesn't exist)
        val schemaCheckResultSet =
            mockk<ResultSet> {
                every { next() } returns true
                every { getBoolean("SCHEMA_EXISTS") } returns false
                every { close() } just Runs
            }

        val preparedStatement =
            mockk<PreparedStatement>(relaxed = true) {
                every { executeQuery() } returns schemaCheckResultSet
                every { close() } just Runs
            }

        val statement =
            mockk<Statement> {
                every { executeQuery(any()) } throws
                    SnowflakeSQLException(
                        "Schema 'TEST_NAMESPACE' already exists, but current role has no privileges on it"
                    )
                every { close() } just Runs
            }

        val connection =
            mockk<Connection> {
                every { createStatement() } returns statement
                every { prepareStatement(any()) } returns preparedStatement
                every { close() } just Runs
            }

        every { dataSource.connection } returns connection

        runBlocking {
            val exception = assertThrows<ConfigErrorException> { client.createNamespace(namespace) }

            assertTrue(exception.message!!.contains("current role has no privileges on it"))
            assertTrue(exception.cause is SnowflakeSQLException)
        }
    }
}
