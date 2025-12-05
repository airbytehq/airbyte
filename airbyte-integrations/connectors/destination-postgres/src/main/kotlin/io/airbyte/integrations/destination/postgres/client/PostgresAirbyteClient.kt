/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.client

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.TableColumns
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.airbyte.integrations.destination.postgres.sql.COUNT_TOTAL_ALIAS
import io.airbyte.integrations.destination.postgres.sql.Column
import io.airbyte.integrations.destination.postgres.sql.PostgresColumnUtils
import io.airbyte.integrations.destination.postgres.sql.PostgresDirectLoadSqlGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.ResultSet
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

@Singleton
class PostgresAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: PostgresDirectLoadSqlGenerator,
    private val postgresColumnUtils: PostgresColumnUtils,
    private val postgresConfiguration: PostgresConfiguration
) : TableSchemaEvolutionClient, TableOperationsClient {

    companion object {
        private const val COLUMN_NAME_COLUMN = "column_name"
    }

    override suspend fun countTable(tableName: TableName): Long? =
        try {
            executeQuery(sqlGenerator.countTable(tableName)) { resultSet ->
                if (resultSet.next()) {
                    resultSet.getLong(COUNT_TOTAL_ALIAS)
                } else {
                    0L
                }
            }
        } catch (e: Exception) {
            log.debug(e) {
                "Table ${tableName.namespace}.${tableName.name} does not exist. Returning a null count to signal a missing table."
            }
            null
        }

    override suspend fun createNamespace(namespace: String) {
        try {
            execute(sqlGenerator.createNamespace(namespace))
        } catch (e: org.postgresql.util.PSQLException) {
            // Handle race condition when multiple connections try to create the same schema
            // PostgreSQL's CREATE SCHEMA IF NOT EXISTS can still fail with unique constraint
            // violation
            // if two sessions try to create it simultaneously
            if (
                e.message?.contains("pg_namespace_nspname_index") == true ||
                    e.message?.contains("already exists") == true
            ) {
                log.debug(e) { "Schema $namespace already exists (race condition), ignoring error" }
            } else {
                throw e
            }
        }
    }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ) {
        val (createTableSql, createIndexesSql) =
            sqlGenerator.createTable(stream, tableName, columnNameMapping, replace)
        execute(createTableSql)
        try {
            execute(createIndexesSql)
        } catch (e: org.postgresql.util.PSQLException) {
            // Handle race condition when multiple connections try to create indexes with the same
            // truncated name (PostgreSQL truncates identifiers to 63 characters)
            if (
                e.message?.contains("pg_class_relname_nsp_index") == true ||
                    e.message?.contains("already exists") == true
            ) {
                log.debug(e) {
                    "Index already exists for table ${tableName.namespace}.${tableName.name} (race condition), ignoring error"
                }
            } else {
                throw e
            }
        }
    }

    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        execute(sqlGenerator.overwriteTable(sourceTableName, targetTableName))
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        execute(sqlGenerator.copyTable(columnNameMapping, sourceTableName, targetTableName))
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        execute(
            sqlGenerator.upsertTable(stream, columnNameMapping, sourceTableName, targetTableName)
        )
    }

    override suspend fun dropTable(tableName: TableName) {
        execute(sqlGenerator.dropTable(tableName))
    }

    override suspend fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ) {
        val columnsInDb = getColumnsFromDb(tableName)
        val defaultColumnNames = postgresColumnUtils.defaultColumns().map { it.columnName }.toSet()
        val columnsInStream =
            postgresColumnUtils
                .getTargetColumns(stream, columnNameMapping)
                .filter { it.columnName !in defaultColumnNames }
                .toSet()
        val (addedColumns, deletedColumns, modifiedColumns) =
            generateSchemaChanges(columnsInDb, columnsInStream)

        log.info { "Summary of the table alterations:" }
        log.info { "Added columns: $addedColumns" }
        log.info { "Deleted columns: $deletedColumns" }
        log.info { "Modified columns: $modifiedColumns" }

        // In raw tables mode, skip primary key and cursor indexes since those columns don't exist
        // (they're stored in _airbyte_data JSONB)
        val isRawTablesMode = postgresConfiguration.legacyRawTablesOnly
        execute(
            sqlGenerator.matchSchemas(
                tableName = tableName,
                columnsToAdd = addedColumns,
                columnsToRemove = deletedColumns,
                columnsToModify = modifiedColumns,
                columnsInDb = columnsInDb,
                recreatePrimaryKeyIndex =
                    !isRawTablesMode &&
                        shouldRecreatePrimaryKeyIndex(stream, tableName, columnNameMapping),
                primaryKeyColumnNames =
                    postgresColumnUtils.getPrimaryKeysColumnNames(stream, columnNameMapping),
                recreateCursorIndex =
                    !isRawTablesMode &&
                        shouldRecreateCursorIndex(stream, tableName, columnNameMapping),
                cursorColumnName =
                    postgresColumnUtils.getCursorColumnName(stream, columnNameMapping),
            )
        )
    }

    override suspend fun discoverSchema(tableName: TableName): TableSchema {
        TODO("Not yet implemented")
    }

    override fun computeSchema(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): TableSchema {
        TODO("Not yet implemented")
    }

    override suspend fun applyChangeset(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        tableName: TableName,
        expectedColumns: TableColumns,
        columnChangeset: ColumnChangeset
    ) {
        TODO("Not yet implemented")
    }

    /**
     * Checks if the primary key index matches the current stream configuration. If the primary keys
     * have changed (detected by comparing columns in the index), then this will return true,
     * otherwise returns false.
     *
     * This function will also return false if the stream doesn't have any primary keys
     */
    private fun shouldRecreatePrimaryKeyIndex(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ): Boolean {
        val streamPrimaryKeys =
            postgresColumnUtils.getPrimaryKeysColumnNames(stream, columnNameMapping)
        if (streamPrimaryKeys.isEmpty()) return false

        val existingPrimaryKeyIndexColumns = getPrimaryKeyIndexColumns(tableName)

        return (existingPrimaryKeyIndexColumns != streamPrimaryKeys).also { shouldRecreate ->
            if (shouldRecreate) {
                log.info {
                    "Primary key columns changed from $existingPrimaryKeyIndexColumns to $streamPrimaryKeys"
                }
            } else {
                log.info { "Primary keys unchanged, no need to (re)create index" }
            }
        }
    }

    private fun getPrimaryKeyIndexColumns(tableName: TableName): List<String> =
        getIndexColumns(sqlGenerator.getPrimaryKeyIndexColumns(tableName))

    private fun getCursorIndexColumn(tableName: TableName): String? =
        getIndexColumns(sqlGenerator.getCursorIndexColumn(tableName)).firstOrNull()

    private fun getIndexColumns(sql: String): List<String> =
        executeQuery(sql) { resultSet ->
            val columns = mutableListOf<String>()
            while (resultSet.next()) {
                columns.add(resultSet.getString(COLUMN_NAME_COLUMN))
            }
            columns
        }

    /**
     * Checks if the cursor index matches the current stream configuration. If the cursor has
     * changed (detected by comparing columns in the index), then this will return true, otherwise
     * returns false.
     *
     * This function will also return false if the stream doesn't have a cursor
     */
    private fun shouldRecreateCursorIndex(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ): Boolean {
        val streamCursor =
            postgresColumnUtils.getCursorColumnName(stream, columnNameMapping) ?: return false

        val existingCursorIndexColumn = getCursorIndexColumn(tableName)

        return (existingCursorIndexColumn != streamCursor).also { shouldRecreate ->
            if (shouldRecreate) {
                log.info {
                    "Cursor column changed from $existingCursorIndexColumn to $streamCursor"
                }
            } else {
                log.info { "Cursor unchanged, no need to (re)create index" }
            }
        }
    }

    internal fun getColumnsFromDb(tableName: TableName): Set<Column> =
        executeQuery(sqlGenerator.getTableSchema(tableName)) { rs ->
            val columnsInDb: MutableSet<Column> = mutableSetOf()
            val defaultColumnNames =
                postgresColumnUtils.defaultColumns().map { it.columnName }.toSet()
            while (rs.next()) {
                val columnName = rs.getString(COLUMN_NAME_COLUMN)

                // Filter out airbyte columns
                if (defaultColumnNames.contains(columnName)) {
                    continue
                }
                val dataType = rs.getString("data_type")

                columnsInDb.add(Column(columnName, normalizePostgresType(dataType)))
            }

            columnsInDb
        }

    /**
     * Normalizes PostgreSQL type names from information_schema to match internal type names.
     *
     * PostgreSQL's information_schema.columns.data_type returns standardized SQL type names that
     * differ from the type names used in DDL statements and internal representations:
     * - "character varying" -> "varchar"
     * - "numeric" -> "decimal"
     * - "timestamp without time zone" -> "timestamp"
     * - "time without time zone" -> "time"
     * - "timestamp with time zone" -> "timestamp with time zone" (no change)
     * - etc.
     */
    private fun normalizePostgresType(postgresType: String): String =
        when (postgresType) {
            "character varying" -> "varchar"
            "numeric" -> "decimal"
            "timestamp without time zone" -> "timestamp"
            "time without time zone" -> "time"
            else -> postgresType
        }

    internal fun generateSchemaChanges(
        columnsInDb: Set<Column>,
        columnsInStream: Set<Column>
    ): Triple<Set<Column>, Set<Column>, Set<Column>> {
        val addedColumns =
            columnsInStream
                .filter { it.columnName !in columnsInDb.map { col -> col.columnName } }
                .toSet()
        val deletedColumns =
            columnsInDb
                .filter { it.columnName !in columnsInStream.map { col -> col.columnName } }
                .toSet()
        val commonColumns =
            columnsInStream
                .filter { it.columnName in columnsInDb.map { col -> col.columnName } }
                .toSet()
        val modifiedColumns =
            commonColumns
                .filter {
                    val dbType =
                        columnsInDb
                            .find { column -> it.columnName == column.columnName }
                            ?.columnTypeName
                    it.columnTypeName != dbType
                }
                .toSet()
        return Triple(addedColumns, deletedColumns, modifiedColumns)
    }

    override suspend fun getGenerationId(tableName: TableName): Long =
        try {
            executeQuery(sqlGenerator.getGenerationId(tableName)) { resultSet ->
                if (resultSet.next()) {
                    resultSet.getLong(COLUMN_NAME_AB_GENERATION_ID)
                } else {
                    log.warn { "No generation ID found for table $tableName, returning 0" }
                    0L
                }
            }
        } catch (e: Exception) {
            log.error(e) { "Failed to retrieve the generation ID for table $tableName" }
            0L
        }

    fun describeTable(tableName: TableName): List<String> =
        executeQuery(sqlGenerator.getTableSchema(tableName)) { resultSet ->
            val columns = mutableListOf<String>()
            while (resultSet.next()) {
                // TODO: extract column_name as a constant
                columns.add(resultSet.getString(COLUMN_NAME_COLUMN))
            }
            columns
        }

    fun copyFromCsv(tableName: TableName, filePath: String) {
        dataSource.connection.use { connection ->
            val copyManager =
                connection.unwrap(org.postgresql.core.BaseConnection::class.java).getCopyAPI()
            val sql = sqlGenerator.copyFromCsv(tableName)
            java.io.FileInputStream(filePath).use { fileInputStream ->
                copyManager.copyIn(sql, fileInputStream)
            }
        }
    }

    private fun execute(query: String) {
        log.info { query.trimIndent() }
        dataSource.connection.use { connection ->
            connection.createStatement().use { it.execute(query) }
        }
    }

    private fun <T> executeQuery(query: String, resultProcessor: (ResultSet) -> T): T {
        log.info { query.trimIndent() }
        return dataSource.connection.use { connection ->
            connection.createStatement().use {
                it.executeQuery(query).use { resultSet -> resultProcessor(resultSet) }
            }
        }
    }
}
