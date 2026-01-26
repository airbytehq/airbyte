/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.client

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.postgres.schema.PostgresColumnManager
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.airbyte.integrations.destination.postgres.sql.COUNT_TOTAL_ALIAS
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
    private lateinit var columnManager: PostgresColumnManager

    private lateinit var postgresConfiguration: PostgresConfiguration

    companion object {
        private const val MOCK_SQL_QUERY = "MOCK_SQL_QUERY"
    }

    @BeforeEach
    fun setup() {
        dataSource = mockk()
        sqlGenerator = mockk()
        columnManager = mockk()
        postgresConfiguration = mockk()
        every { postgresConfiguration.legacyRawTablesOnly } returns false
        every { columnManager.getMetaColumnNames() } returns emptySet()
        client =
            PostgresAirbyteClient(dataSource, sqlGenerator, columnManager, postgresConfiguration)
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
        every { sqlGenerator.createTable(stream, tableName, true) } returns
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
        val columnNameMapping =
            ColumnNameMapping(mapOf("col1" to "targetCol1", "col2" to "targetCol2"))
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
        every { sqlGenerator.copyTable(any(), sourceTableName, targetTableName) } returns
            MOCK_SQL_QUERY

        runBlocking {
            client.copyTable(
                columnNameMapping = columnNameMapping,
                sourceTableName = sourceTableName,
                targetTableName = targetTableName
            )
            verify(exactly = 1) { mockConnection.close() }
            verify(exactly = 1) {
                // Verify that correct values (meta columns + mapped columns) are passed
                // meta columns are empty in setup
                sqlGenerator.copyTable(
                    match { it.containsAll(listOf("targetCol1", "targetCol2")) },
                    sourceTableName,
                    targetTableName
                )
            }
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
        every { sqlGenerator.upsertTable(stream, sourceTableName, targetTableName) } returns
            MOCK_SQL_QUERY

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
        every { resultSet.getString("is_nullable") } returns "YES" andThen "YES" andThen "YES"

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
        every { columnManager.getMetaColumnNames() } returns setOf(defaultColumnName)

        val result = client.getColumnsFromDb(tableName)

        val expectedColumns =
            mapOf("col1" to ColumnType("varchar", true), "col2" to ColumnType("bigint", true))

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
        every { resultSet.getString("is_nullable") } returns "YES" andThen "YES" andThen "YES"

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
        every { columnManager.getMetaColumnNames() } returns emptySet()

        val result = client.getColumnsFromDb(tableName)

        // Types should be normalized to internal representation
        val expectedColumns =
            mapOf(
                "col1" to ColumnType("varchar", true),
                "col2" to ColumnType("decimal", true),
                "col3" to ColumnType("timestamp with time zone", true)
            )

        assertEquals(expectedColumns, result)
    }

    @Test
    fun testGenerateSchemaChanges() {
        val columnsInDb =
            mapOf("col1" to ColumnType("text", true), "col2" to ColumnType("integer", true))
        val columnsInStream =
            mapOf("col2" to ColumnType("varchar", true), "col3" to ColumnType("boolean", true))

        val (added, deleted, modified) = client.generateSchemaChanges(columnsInDb, columnsInStream)

        assertEquals(1, added.size)
        assertEquals(ColumnType("boolean", true), added["col3"])

        assertEquals(1, deleted.size)
        assertEquals(ColumnType("text", true), deleted["col1"])

        assertEquals(1, modified.size)
        assertEquals(
            ColumnTypeChange(ColumnType("integer", true), ColumnType("varchar", true)),
            modified["col2"]
        )
    }

    @Test
    fun testGenerateSchemaChangesNoChanges() {
        val columns =
            mapOf("col1" to ColumnType("text", true), "col2" to ColumnType("integer", true))

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
        every { resultSet.getString("is_nullable") } returns "YES" andThen "YES"
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
            sqlGenerator.matchSchemas(any(), any(), any(), any(), any(), any(), any(), any())
        } returns MOCK_SQL_QUERY

        // no column changes - mock stream's pre-computed table schema to return same columns as DB
        every { columnManager.getMetaColumnNames() } returns emptySet()
        val finalSchema =
            mapOf("col1" to ColumnType("text", true), "col2" to ColumnType("integer", true))
        val columnSchema = ColumnSchema(emptyMap(), emptyMap(), finalSchema)
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { this@mockk.columnSchema } returns columnSchema
                every { this@mockk.getPrimaryKey() } returns emptyList()
                every { this@mockk.getCursor() } returns emptyList()
            }
        every { stream.tableSchema } returns streamTableSchema

        // no index changes
        every { sqlGenerator.getPrimaryKeysColumnNames(stream) } returns emptyList()
        every { sqlGenerator.getCursorColumnName(stream) } returns null

        runBlocking {
            client.ensureSchemaMatches(stream, tableName, columnNameMapping)
            verify(exactly = 1) {
                sqlGenerator.matchSchemas(
                    tableName = tableName,
                    columnsToAdd = emptyMap(),
                    columnsToRemove = emptyMap(),
                    columnsToModify = emptyMap(),
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

        // Mock getColumnsFromDb - table has col1 only
        val tableColumnsResultSet = mockk<ResultSet>()
        every { tableColumnsResultSet.next() } returns true andThen false
        every { tableColumnsResultSet.getString("column_name") } returns "col1"
        every { tableColumnsResultSet.getString("data_type") } returns "text"
        every { tableColumnsResultSet.getString("is_nullable") } returns "YES"
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
            sqlGenerator.matchSchemas(any(), any(), any(), any(), any(), any(), any(), any())
        } returns MOCK_SQL_QUERY

        every { columnManager.getMetaColumnNames() } returns emptySet()
        // Stream has col1 and col2 (col2 is new)
        val finalSchema =
            mapOf("col1" to ColumnType("text", true), "col2" to ColumnType("integer", true))
        val columnSchema = ColumnSchema(emptyMap(), emptyMap(), finalSchema)
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { this@mockk.columnSchema } returns columnSchema
                every { this@mockk.getPrimaryKey() } returns emptyList()
                every { this@mockk.getCursor() } returns emptyList()
            }
        every { stream.tableSchema } returns streamTableSchema

        every { sqlGenerator.getPrimaryKeysColumnNames(stream) } returns emptyList()
        every { sqlGenerator.getCursorColumnName(stream) } returns null

        runBlocking {
            client.ensureSchemaMatches(stream, tableName, columnNameMapping)
            verify(exactly = 1) {
                sqlGenerator.matchSchemas(
                    tableName = tableName,
                    columnsToAdd = mapOf("col2" to ColumnType("integer", true)),
                    columnsToRemove = emptyMap(),
                    columnsToModify = emptyMap(),
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
        every { resultSet.getString("is_nullable") } returns "YES"
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
            sqlGenerator.matchSchemas(any(), any(), any(), any(), any(), any(), any(), any())
        } returns MOCK_SQL_QUERY

        every { columnManager.getMetaColumnNames() } returns emptySet()
        val finalSchema = mapOf("col1" to ColumnType("text", true))
        val columnSchema = ColumnSchema(emptyMap(), emptyMap(), finalSchema)
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { this@mockk.columnSchema } returns columnSchema
                every { this@mockk.getPrimaryKey() } returns listOf(listOf("new_pk"))
                every { this@mockk.getCursor() } returns emptyList()
            }
        every { stream.tableSchema } returns streamTableSchema

        // primary key has changed
        every { sqlGenerator.getPrimaryKeysColumnNames(stream) } returns listOf("new_pk")
        every { sqlGenerator.getCursorColumnName(stream) } returns null

        runBlocking {
            client.ensureSchemaMatches(stream, tableName, columnNameMapping)
            verify(exactly = 1) {
                sqlGenerator.matchSchemas(
                    tableName = tableName,
                    columnsToAdd = emptyMap(),
                    columnsToRemove = emptyMap(),
                    columnsToModify = emptyMap(),
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
        every { resultSet.getString("is_nullable") } returns "YES"
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
            sqlGenerator.matchSchemas(any(), any(), any(), any(), any(), any(), any(), any())
        } returns MOCK_SQL_QUERY

        every { columnManager.getMetaColumnNames() } returns emptySet()
        val finalSchema = mapOf("col1" to ColumnType("text", true))
        val columnSchema = ColumnSchema(emptyMap(), emptyMap(), finalSchema)
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { this@mockk.columnSchema } returns columnSchema
                every { this@mockk.getPrimaryKey() } returns emptyList()
                every { this@mockk.getCursor() } returns listOf("new_cursor")
            }
        every { stream.tableSchema } returns streamTableSchema

        every { sqlGenerator.getPrimaryKeysColumnNames(stream) } returns emptyList()
        // cursor has changed
        every { sqlGenerator.getCursorColumnName(stream) } returns "new_cursor"

        runBlocking {
            client.ensureSchemaMatches(stream, tableName, columnNameMapping)
            verify(exactly = 1) {
                sqlGenerator.matchSchemas(
                    tableName = tableName,
                    columnsToAdd = emptyMap(),
                    columnsToRemove = emptyMap(),
                    columnsToModify = emptyMap(),
                    recreatePrimaryKeyIndex = false,
                    primaryKeyColumnNames = emptyList(),
                    recreateCursorIndex = true,
                    cursorColumnName = "new_cursor"
                )
            }
        }
    }

    @Test
    fun testEnsureSchemaMatchesWithAllChanges() {
        val stream = mockk<DestinationStream>()
        val tableName = TableName(namespace = "test_ns", name = "test_table")
        val columnNameMapping = mockk<ColumnNameMapping>(relaxed = true)

        // Mock getColumnsFromDb - table has col1 and old_col but not new_col
        val resultSet = mockk<ResultSet>()
        every { resultSet.next() } returns true andThen true andThen false
        every { resultSet.getString("column_name") } returns "col1" andThen "old_col"
        every { resultSet.getString("data_type") } returns "text" andThen "varchar"
        every { resultSet.getString("is_nullable") } returns "YES" andThen "YES"
        every { resultSet.close() } just Runs

        // Mock getPrimaryKeyIndexColumns
        val pkResultSet = mockk<ResultSet>()
        every { pkResultSet.next() } returns true andThen false
        every { pkResultSet.getString("column_name") } returns "old_pk"
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
            sqlGenerator.matchSchemas(any(), any(), any(), any(), any(), any(), any(), any())
        } returns MOCK_SQL_QUERY

        every { columnManager.getMetaColumnNames() } returns emptySet()
        // Stream has col1 and new_col but not old_col
        val finalSchema =
            mapOf("col1" to ColumnType("text", true), "new_col" to ColumnType("integer", true))
        val columnSchema = ColumnSchema(emptyMap(), emptyMap(), finalSchema)
        val streamTableSchema =
            mockk<StreamTableSchema> {
                every { this@mockk.columnSchema } returns columnSchema
                every { this@mockk.getPrimaryKey() } returns listOf(listOf("new_pk"))
                every { this@mockk.getCursor() } returns listOf("new_cursor")
            }
        every { stream.tableSchema } returns streamTableSchema

        every { sqlGenerator.getPrimaryKeysColumnNames(stream) } returns listOf("new_pk")
        every { sqlGenerator.getCursorColumnName(stream) } returns "new_cursor"

        runBlocking {
            client.ensureSchemaMatches(stream, tableName, columnNameMapping)
            verify(exactly = 1) {
                sqlGenerator.matchSchemas(
                    tableName = tableName,
                    columnsToAdd = mapOf("new_col" to ColumnType("integer", true)),
                    columnsToRemove = mapOf("old_col" to ColumnType("varchar", true)),
                    columnsToModify = emptyMap(),
                    recreatePrimaryKeyIndex = true,
                    primaryKeyColumnNames = listOf("new_pk"),
                    recreateCursorIndex = true,
                    cursorColumnName = "new_cursor"
                )
            }
        }
    }
}
