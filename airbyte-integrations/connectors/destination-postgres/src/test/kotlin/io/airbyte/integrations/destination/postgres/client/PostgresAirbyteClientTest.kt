/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.client

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.airbyte.integrations.destination.postgres.sql.COUNT_TOTAL_ALIAS
import io.airbyte.integrations.destination.postgres.sql.Column
import io.airbyte.integrations.destination.postgres.sql.PostgresColumnUtils
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
    private lateinit var postgresColumnUtils: PostgresColumnUtils
    private lateinit var postgresConfiguration: PostgresConfiguration

    companion object {
        private const val MOCK_SQL_QUERY = "MOCK_SQL_QUERY"
    }

    @BeforeEach
    fun setup() {
        dataSource = mockk()
        sqlGenerator = mockk()
        postgresColumnUtils = mockk()
        postgresConfiguration = mockk()
        every { postgresConfiguration.legacyRawTablesOnly } returns false
        client =
            PostgresAirbyteClient(
                dataSource,
                sqlGenerator,
                postgresColumnUtils,
                postgresConfiguration
            )
    }

    @Test
    fun testCountTable() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val resultSet =
            mockk<ResultSet> {
                every { next() } returns true
                every { getLong(COUNT_TOTAL_ALIAS) } returns 42L
                every { close() } just Runs
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

        val resultSet =
            mockk<ResultSet> {
                every { next() } returns false
                every { close() } just Runs
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
            assertEquals(0L, result)
            verify(exactly = 1) { mockConnection.close() }
        }
    }

    @Test
    fun testCountMissingTable() {
        val tableName = TableName(namespace = "namespace", name = "name")
        val statement =
            mockk<Statement> {
                every { executeQuery(any()) } throws SQLException("table does not exist")
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
        every { sqlGenerator.createTable(stream, tableName, columnNameMapping, true) } returns
            Pair(MOCK_SQL_QUERY, "CREATE INDEX IF NOT EXISTS idx ON table (col);")

        runBlocking {
            client.createTable(
                stream = stream,
                tableName = tableName,
                columnNameMapping = columnNameMapping,
                replace = true
            )
            verify(exactly = 2) { statement.execute(any()) }
            verify(exactly = 2) { mockConnection.close() }
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
        every { sqlGenerator.overwriteTable(sourceTableName, targetTableName) } returns
            MOCK_SQL_QUERY

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
        every {
            sqlGenerator.copyTable(columnNameMapping, sourceTableName, targetTableName)
        } returns MOCK_SQL_QUERY

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
        every {
            sqlGenerator.upsertTable(stream, columnNameMapping, sourceTableName, targetTableName)
        } returns MOCK_SQL_QUERY

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
                every { close() } just Runs
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
                every { close() } just Runs
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
        verify(exactly = 1) { mockConnection.close() }
    }

    @Test
    fun testGetColumnsFromDb() {
        val tableName = TableName(namespace = "test_namespace", name = "test_table")
        val resultSet = mockk<ResultSet>()
        every { resultSet.next() } returns true andThen true andThen true andThen false
        every { resultSet.close() } just Runs
        val defaultColumnName = "default_column_name"
        every { resultSet.getString("column_name") } returns
            "col1" andThen
            defaultColumnName andThen
            "col2"
        every { resultSet.getString("data_type") } returns "varchar" andThen "bigint"

        val statement =
            mockk<Statement> {
                every { executeQuery(MOCK_SQL_QUERY) } returns resultSet
                every { close() } just Runs
            }

        val connection = mockk<Connection>()
        every { connection.createStatement() } returns statement
        every { connection.close() } just Runs

        every { dataSource.connection } returns connection
        every { sqlGenerator.getTableSchema(tableName) } returns MOCK_SQL_QUERY
        every { postgresColumnUtils.defaultColumns() } returns
            listOf(Column(defaultColumnName, "varchar"))

        val result = client.getColumnsFromDb(tableName)

        val expectedColumns = setOf(Column("col1", "varchar"), Column("col2", "bigint"))

        assertEquals(expectedColumns, result)
    }

    @Test
    fun testGetColumnsFromDbWithPostgresTypeNormalization() {
        val tableName = TableName(namespace = "test_namespace", name = "test_table")
        val resultSet = mockk<ResultSet>()
        every { resultSet.next() } returns true andThen true andThen true andThen false
        every { resultSet.close() } just Runs
        every { resultSet.getString("column_name") } returns "col1" andThen "col2" andThen "col3"
        // PostgreSQL returns "character varying" and "numeric" from information_schema
        every { resultSet.getString("data_type") } returns
            "character varying" andThen
            "numeric" andThen
            "timestamp with time zone"

        val statement =
            mockk<Statement> {
                every { executeQuery(MOCK_SQL_QUERY) } returns resultSet
                every { close() } just Runs
            }

        val connection = mockk<Connection>()
        every { connection.createStatement() } returns statement
        every { connection.close() } just Runs

        every { dataSource.connection } returns connection
        every { sqlGenerator.getTableSchema(tableName) } returns MOCK_SQL_QUERY
        every { postgresColumnUtils.defaultColumns() } returns emptyList()

        val result = client.getColumnsFromDb(tableName)

        // Types should be normalized to internal representation
        val expectedColumns =
            setOf(
                Column("col1", "varchar"),
                Column("col2", "decimal"),
                Column("col3", "timestamp with time zone")
            )

        assertEquals(expectedColumns, result)
    }

    @Test
    fun testGenerateSchemaChanges() {
        val column1 = Column("col1", "text")
        val column2 = Column("col2", "integer")
        val column2Modified = Column("col2", "varchar")
        val newColumn = Column("col3", "boolean")
        val columnsInDb = setOf(column1, column2)
        val columnsInStream = setOf(column2Modified, newColumn)

        val (added, deleted, modified) = client.generateSchemaChanges(columnsInDb, columnsInStream)

        assertEquals(1, added.size)
        assertEquals(newColumn.columnName, added.first().columnName)
        assertEquals(newColumn.columnTypeName, added.first().columnTypeName)

        assertEquals(1, deleted.size)
        assertEquals(column1.columnName, deleted.first().columnName)
        assertEquals(column1.columnTypeName, deleted.first().columnTypeName)

        assertEquals(1, modified.size)
        assertEquals(column2Modified.columnName, modified.first().columnName)
        assertEquals(column2Modified.columnTypeName, modified.first().columnTypeName)
    }

    @Test
    fun testGenerateSchemaChangesNoChanges() {
        val columns = setOf(Column("col1", "text"), Column("col2", "integer"))

        val (added, deleted, modified) = client.generateSchemaChanges(columns, columns)

        assertEquals(0, added.size)
        assertEquals(0, deleted.size)
        assertEquals(0, modified.size)
    }

    @Test
    fun testEnsureSchemaMatchesWithNoChanges() {
        val stream = mockk<DestinationStream>()
        val tableName = TableName(namespace = "test_ns", name = "test_table")
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)

        // Mock getColumnsFromDb
        val resultSet = mockk<ResultSet>()
        every { resultSet.next() } returns true andThen true andThen false
        every { resultSet.getString("column_name") } returns "col1" andThen "col2"
        every { resultSet.getString("data_type") } returns "text" andThen "integer"
        every { resultSet.close() } just Runs

        // Mock getPrimaryKeyIndexColumns
        val pkResultSet = mockk<ResultSet>()
        every { pkResultSet.next() } returns false
        every { pkResultSet.close() } just Runs

        // Mock getCursorIndexColumn
        val cursorResultSet = mockk<ResultSet>()
        every { cursorResultSet.next() } returns false
        every { cursorResultSet.close() } just Runs

        val statement =
            mockk<Statement> {
                every { executeQuery(any()) } returns
                    resultSet andThen
                    pkResultSet andThen
                    cursorResultSet
                every { execute(any()) } returns true
                every { close() } just Runs
            }

        val connection = mockk<Connection>()
        every { connection.createStatement() } returns statement
        every { connection.close() } just Runs

        every { dataSource.connection } returns connection
        every { sqlGenerator.getTableSchema(tableName) } returns MOCK_SQL_QUERY
        every { sqlGenerator.getPrimaryKeyIndexColumns(tableName) } returns MOCK_SQL_QUERY
        every { sqlGenerator.getCursorIndexColumn(tableName) } returns MOCK_SQL_QUERY
        every {
            sqlGenerator.matchSchemas(any(), any(), any(), any(), any(), any(), any(), any(), any())
        } returns MOCK_SQL_QUERY

        // no column changes
        every { postgresColumnUtils.defaultColumns() } returns emptyList()
        every { postgresColumnUtils.getTargetColumns(stream, columnNameMapping) } returns
            listOf(Column("col1", "text"), Column("col2", "integer"))

        // no index changes
        every { postgresColumnUtils.getPrimaryKeysColumnNames(stream, columnNameMapping) } returns
            emptyList()
        every { postgresColumnUtils.getCursorColumnName(stream, columnNameMapping) } returns null

        runBlocking {
            client.ensureSchemaMatches(stream, tableName, columnNameMapping)
            verify(exactly = 1) {
                sqlGenerator.matchSchemas(
                    tableName = tableName,
                    columnsToAdd = emptySet(),
                    columnsToRemove = emptySet(),
                    columnsToModify = emptySet(),
                    columnsInDb = any(),
                    recreatePrimaryKeyIndex = false,
                    primaryKeyColumnNames = emptyList(),
                    recreateCursorIndex = false,
                    cursorColumnName = null
                )
            }
        }
    }

    @Test
    fun testEnsureSchemaMatchesWithColumnChanges() {
        val stream = mockk<DestinationStream>()
        val tableName = TableName(namespace = "test_ns", name = "test_table")
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)

        // Mock getColumnsFromDb
        val tableColumnsResultSet = mockk<ResultSet>()
        every { tableColumnsResultSet.next() } returns true andThen false
        every { tableColumnsResultSet.getString("column_name") } returns "col1"
        every { tableColumnsResultSet.getString("data_type") } returns "text"
        every { tableColumnsResultSet.close() } just Runs

        // Mock getPrimaryKeyIndexColumns
        val pkResultSet = mockk<ResultSet>()
        every { pkResultSet.next() } returns false
        every { pkResultSet.close() } just Runs

        // Mock getCursorIndexColumn
        val cursorResultSet = mockk<ResultSet>()
        every { cursorResultSet.next() } returns false
        every { cursorResultSet.close() } just Runs

        val statement =
            mockk<Statement> {
                every { executeQuery(any()) } returns
                    tableColumnsResultSet andThen
                    pkResultSet andThen
                    cursorResultSet
                every { execute(any()) } returns true
                every { close() } just Runs
            }

        val connection = mockk<Connection>()
        every { connection.createStatement() } returns statement
        every { connection.close() } just Runs

        every { dataSource.connection } returns connection
        every { sqlGenerator.getTableSchema(tableName) } returns MOCK_SQL_QUERY
        every { sqlGenerator.getPrimaryKeyIndexColumns(tableName) } returns MOCK_SQL_QUERY
        every { sqlGenerator.getCursorIndexColumn(tableName) } returns MOCK_SQL_QUERY
        every {
            sqlGenerator.matchSchemas(any(), any(), any(), any(), any(), any(), any(), any(), any())
        } returns MOCK_SQL_QUERY

        every { postgresColumnUtils.defaultColumns() } returns emptyList()
        every { postgresColumnUtils.getTargetColumns(stream, columnNameMapping) } returns
            listOf(Column("col1", "text"), Column("col2", "integer"))

        every { postgresColumnUtils.getPrimaryKeysColumnNames(stream, columnNameMapping) } returns
            emptyList()
        every { postgresColumnUtils.getCursorColumnName(stream, columnNameMapping) } returns null

        runBlocking {
            client.ensureSchemaMatches(stream, tableName, columnNameMapping)
            verify(exactly = 1) {
                sqlGenerator.matchSchemas(
                    tableName = tableName,
                    columnsToAdd = setOf(Column("col2", "integer")),
                    columnsToRemove = emptySet(),
                    columnsToModify = emptySet(),
                    columnsInDb = any(),
                    recreatePrimaryKeyIndex = false,
                    primaryKeyColumnNames = emptyList(),
                    recreateCursorIndex = false,
                    cursorColumnName = null
                )
            }
        }
    }

    @Test
    fun testEnsureSchemaMatchesWithPrimaryKeyIndexRecreation() {
        val stream = mockk<DestinationStream>()
        val tableName = TableName(namespace = "test_ns", name = "test_table")
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)

        // Mock getColumnsFromDb
        val resultSet = mockk<ResultSet>()
        every { resultSet.next() } returns true andThen false
        every { resultSet.getString("column_name") } returns "col1"
        every { resultSet.getString("data_type") } returns "text"
        every { resultSet.close() } just Runs

        // Mock getPrimaryKeyIndexColumns
        val pkResultSet = mockk<ResultSet>()
        every { pkResultSet.next() } returns true andThen false
        every { pkResultSet.getString("column_name") } returns "old_pk"
        every { pkResultSet.close() } just Runs

        // Mock getCursorIndexColumn
        val cursorResultSet = mockk<ResultSet>()
        every { cursorResultSet.next() } returns false
        every { cursorResultSet.close() } just Runs

        val statement =
            mockk<Statement> {
                every { executeQuery(any()) } returns
                    resultSet andThen
                    pkResultSet andThen
                    cursorResultSet
                every { execute(any()) } returns true
                every { close() } just Runs
            }

        val connection = mockk<Connection>()
        every { connection.createStatement() } returns statement
        every { connection.close() } just Runs

        every { dataSource.connection } returns connection
        every { sqlGenerator.getTableSchema(tableName) } returns MOCK_SQL_QUERY
        every { sqlGenerator.getPrimaryKeyIndexColumns(tableName) } returns MOCK_SQL_QUERY
        every { sqlGenerator.getCursorIndexColumn(tableName) } returns MOCK_SQL_QUERY
        every {
            sqlGenerator.matchSchemas(any(), any(), any(), any(), any(), any(), any(), any(), any())
        } returns MOCK_SQL_QUERY

        every { postgresColumnUtils.defaultColumns() } returns emptyList()
        every { postgresColumnUtils.getTargetColumns(stream, columnNameMapping) } returns
            listOf(Column("col1", "text"))

        // primary key has changed
        every { postgresColumnUtils.getPrimaryKeysColumnNames(stream, columnNameMapping) } returns
            listOf("new_pk")
        every { postgresColumnUtils.getCursorColumnName(stream, columnNameMapping) } returns null

        runBlocking {
            client.ensureSchemaMatches(stream, tableName, columnNameMapping)
            verify(exactly = 1) {
                sqlGenerator.matchSchemas(
                    tableName = tableName,
                    columnsToAdd = emptySet(),
                    columnsToRemove = emptySet(),
                    columnsToModify = emptySet(),
                    columnsInDb = any(),
                    recreatePrimaryKeyIndex = true,
                    primaryKeyColumnNames = listOf("new_pk"),
                    recreateCursorIndex = false,
                    cursorColumnName = null
                )
            }
        }
    }

    @Test
    fun testEnsureSchemaMatchesWithCursorIndexRecreation() {
        val stream = mockk<DestinationStream>()
        val tableName = TableName(namespace = "test_ns", name = "test_table")
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)

        // Mock getColumnsFromDb
        val resultSet = mockk<ResultSet>()
        every { resultSet.next() } returns true andThen false
        every { resultSet.getString("column_name") } returns "col1"
        every { resultSet.getString("data_type") } returns "text"
        every { resultSet.close() } just Runs

        // Mock getPrimaryKeyIndexColumns
        val pkResultSet = mockk<ResultSet>()
        every { pkResultSet.next() } returns false
        every { pkResultSet.close() } just Runs

        // Mock getCursorIndexColumn
        val cursorResultSet = mockk<ResultSet>()
        every { cursorResultSet.next() } returns true andThen false
        every { cursorResultSet.getString("column_name") } returns "old_cursor"
        every { cursorResultSet.close() } just Runs

        val statement =
            mockk<Statement> {
                every { executeQuery(any()) } returns
                    resultSet andThen
                    pkResultSet andThen
                    cursorResultSet
                every { execute(any()) } returns true
                every { close() } just Runs
            }

        val connection = mockk<Connection>()
        every { connection.createStatement() } returns statement
        every { connection.close() } just Runs

        every { dataSource.connection } returns connection
        every { sqlGenerator.getTableSchema(tableName) } returns MOCK_SQL_QUERY
        every { sqlGenerator.getPrimaryKeyIndexColumns(tableName) } returns MOCK_SQL_QUERY
        every { sqlGenerator.getCursorIndexColumn(tableName) } returns MOCK_SQL_QUERY
        every {
            sqlGenerator.matchSchemas(any(), any(), any(), any(), any(), any(), any(), any(), any())
        } returns MOCK_SQL_QUERY

        every { postgresColumnUtils.defaultColumns() } returns emptyList()
        every { postgresColumnUtils.getTargetColumns(stream, columnNameMapping) } returns
            listOf(Column("col1", "text"))

        every { postgresColumnUtils.getPrimaryKeysColumnNames(stream, columnNameMapping) } returns
            emptyList()
        // cursor has changed
        every { postgresColumnUtils.getCursorColumnName(stream, columnNameMapping) } returns
            "new_cursor"

        runBlocking {
            client.ensureSchemaMatches(stream, tableName, columnNameMapping)
            verify(exactly = 1) {
                sqlGenerator.matchSchemas(
                    tableName = tableName,
                    columnsToAdd = emptySet(),
                    columnsToRemove = emptySet(),
                    columnsToModify = emptySet(),
                    columnsInDb = any(),
                    recreatePrimaryKeyIndex = false,
                    primaryKeyColumnNames = emptyList(),
                    recreateCursorIndex = true,
                    cursorColumnName = "new_cursor"
                )
            }
        }
    }

    @Test
    fun testEnsureSchemaMatchesInRawTablesModeSkipsIndexRecreation() {
        // In raw tables mode, primary key and cursor indexes should NOT be recreated
        // because user-defined columns don't exist (they're stored in _airbyte_data JSONB)
        every { postgresConfiguration.legacyRawTablesOnly } returns true

        val stream = mockk<DestinationStream>()
        val tableName = TableName(namespace = "test_ns", name = "test_table")
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)

        // Mock getColumnsFromDb - returns empty since raw tables mode doesn't have user columns
        val resultSet = mockk<ResultSet>()
        every { resultSet.next() } returns false
        every { resultSet.close() } just Runs

        val statement =
            mockk<Statement> {
                every { executeQuery(any()) } returns resultSet
                every { execute(any()) } returns true
                every { close() } just Runs
            }

        val connection = mockk<Connection>()
        every { connection.createStatement() } returns statement
        every { connection.close() } just Runs

        every { dataSource.connection } returns connection
        every { sqlGenerator.getTableSchema(tableName) } returns MOCK_SQL_QUERY
        every {
            sqlGenerator.matchSchemas(any(), any(), any(), any(), any(), any(), any(), any(), any())
        } returns MOCK_SQL_QUERY

        every { postgresColumnUtils.defaultColumns() } returns emptyList()
        every { postgresColumnUtils.getTargetColumns(stream, columnNameMapping) } returns
            emptyList()

        // Even though the stream has primary keys and cursor defined, they should be ignored
        // in raw tables mode
        every { postgresColumnUtils.getPrimaryKeysColumnNames(stream, columnNameMapping) } returns
            listOf("ad_group_id")
        every { postgresColumnUtils.getCursorColumnName(stream, columnNameMapping) } returns
            "updated_at"

        runBlocking {
            client.ensureSchemaMatches(stream, tableName, columnNameMapping)
            // Verify that recreatePrimaryKeyIndex and recreateCursorIndex are both false
            // even though primary keys and cursor are defined in the stream
            verify(exactly = 1) {
                sqlGenerator.matchSchemas(
                    tableName = tableName,
                    columnsToAdd = emptySet(),
                    columnsToRemove = emptySet(),
                    columnsToModify = emptySet(),
                    columnsInDb = any(),
                    recreatePrimaryKeyIndex = false, // Should be false in raw tables mode
                    primaryKeyColumnNames = listOf("ad_group_id"),
                    recreateCursorIndex = false, // Should be false in raw tables mode
                    cursorColumnName = "updated_at"
                )
            }
        }
    }

    @Test
    fun testEnsureSchemaMatchesInRawTablesModeWithPrimaryKeyChanges() {
        // Even when primary keys have changed, raw tables mode should skip index recreation
        every { postgresConfiguration.legacyRawTablesOnly } returns true

        val stream = mockk<DestinationStream>()
        val tableName = TableName(namespace = "test_ns", name = "test_table")
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)

        // Mock getColumnsFromDb
        val resultSet = mockk<ResultSet>()
        every { resultSet.next() } returns false
        every { resultSet.close() } just Runs

        val statement =
            mockk<Statement> {
                every { executeQuery(any()) } returns resultSet
                every { execute(any()) } returns true
                every { close() } just Runs
            }

        val connection = mockk<Connection>()
        every { connection.createStatement() } returns statement
        every { connection.close() } just Runs

        every { dataSource.connection } returns connection
        every { sqlGenerator.getTableSchema(tableName) } returns MOCK_SQL_QUERY
        every {
            sqlGenerator.matchSchemas(any(), any(), any(), any(), any(), any(), any(), any(), any())
        } returns MOCK_SQL_QUERY

        every { postgresColumnUtils.defaultColumns() } returns emptyList()
        every { postgresColumnUtils.getTargetColumns(stream, columnNameMapping) } returns
            emptyList()

        // Primary keys are defined - would normally trigger index recreation
        every { postgresColumnUtils.getPrimaryKeysColumnNames(stream, columnNameMapping) } returns
            listOf("new_pk_column")
        every { postgresColumnUtils.getCursorColumnName(stream, columnNameMapping) } returns null

        runBlocking {
            client.ensureSchemaMatches(stream, tableName, columnNameMapping)
            // recreatePrimaryKeyIndex should be false because we're in raw tables mode,
            // even though primary keys are defined
            verify(exactly = 1) {
                sqlGenerator.matchSchemas(
                    tableName = tableName,
                    columnsToAdd = emptySet(),
                    columnsToRemove = emptySet(),
                    columnsToModify = emptySet(),
                    columnsInDb = any(),
                    recreatePrimaryKeyIndex = false,
                    primaryKeyColumnNames = listOf("new_pk_column"),
                    recreateCursorIndex = false,
                    cursorColumnName = null
                )
            }
        }
    }
}
