/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.client

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.cdk.load.component.TableColumns
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAMES
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.postgres.schema.PostgresColumnManager
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.airbyte.integrations.destination.postgres.sql.COUNT_TOTAL_ALIAS
import io.airbyte.integrations.destination.postgres.sql.PostgresDirectLoadSqlGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.ResultSet
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

@Singleton
@SuppressFBWarnings(
    value = ["SQL_NONCONSTANT_STRING_PASSED_TO_EXECUTE"],
    justification =
        "There is little chance of SQL injection. There is also little need for statement reuse. The basic statement is more readable than the prepared statement."
)
class PostgresAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: PostgresDirectLoadSqlGenerator,
    private val columnManager: PostgresColumnManager,
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

    override suspend fun namespaceExists(namespace: String): Boolean {
        return executeQuery(
            """
            SELECT EXISTS(
                SELECT 1 FROM information_schema.schemata
                WHERE schema_name = '$namespace'
            )
            """
        ) { rs -> rs.next() && rs.getBoolean(1) }
    }

    override suspend fun tableExists(table: TableName): Boolean {
        return executeQuery(
            """
            SELECT EXISTS(
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = '${table.namespace}'
                AND table_name = '${table.name}'
            )
            """
        ) { rs -> rs.next() && rs.getBoolean(1) }
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
            sqlGenerator.createTable(stream, tableName, replace)
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
        val metaColumnNames = columnManager.getMetaColumnNames()
        val targetColumnNames =
            if (postgresConfiguration.legacyRawTablesOnly == true) {
                metaColumnNames
            } else {
                metaColumnNames + columnNameMapping.values
            }
        execute(
            sqlGenerator.copyTable(targetColumnNames.toList(), sourceTableName, targetTableName)
        )
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        execute(sqlGenerator.upsertTable(stream, sourceTableName, targetTableName))
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
        // In raw tables mode, finalSchema contains just {_airbyte_data -> JSONB}
        // In typed mode, finalSchema contains the mapped user columns
        val columnsInStream = stream.tableSchema.columnSchema.finalSchema

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
                recreatePrimaryKeyIndex =
                    !isRawTablesMode &&
                        shouldRecreatePrimaryKeyIndex(stream, tableName),
                primaryKeyColumnNames = sqlGenerator.getPrimaryKeysColumnNames(stream),
                recreateCursorIndex =
                    !isRawTablesMode &&
                        shouldRecreateCursorIndex(stream, tableName),
                cursorColumnName = sqlGenerator.getCursorColumnName(stream),
            )
        )
    }

    override suspend fun discoverSchema(tableName: TableName): TableSchema {
        val columnsInDb = getColumnsFromDbForDiscovery(tableName)
        val hasAllAirbyteColumns = columnsInDb.keys.containsAll(COLUMN_NAMES)

        if (!hasAllAirbyteColumns) {
            val message =
                "The target table ($tableName) already exists in the destination, but does not contain Airbyte's internal columns. Airbyte can only sync to Airbyte-controlled tables. To fix this error, you must either delete the target table or add a prefix in the connection configuration in order to sync to a separate table in the destination."
            log.error { message }
            throw ConfigErrorException(message)
        }

        // Filter out Airbyte columns
        val userColumns = columnsInDb.filterKeys { it !in COLUMN_NAMES }
        return TableSchema(userColumns)
    }

    override fun computeSchema(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): TableSchema {
        return TableSchema(stream.tableSchema.columnSchema.finalSchema)
    }

    override suspend fun applyChangeset(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        tableName: TableName,
        expectedColumns: TableColumns,
        columnChangeset: ColumnChangeset
    ) {
        if (
            columnChangeset.columnsToAdd.isNotEmpty() ||
                columnChangeset.columnsToDrop.isNotEmpty() ||
                columnChangeset.columnsToChange.isNotEmpty()
        ) {
            log.info { "Summary of the table alterations:" }
            log.info { "Added columns: ${columnChangeset.columnsToAdd}" }
            log.info { "Deleted columns: ${columnChangeset.columnsToDrop}" }
            log.info { "Modified columns: ${columnChangeset.columnsToChange}" }

            execute(
                sqlGenerator.matchSchemas(
                    tableName = tableName,
                    columnsToAdd = columnChangeset.columnsToAdd,
                    columnsToRemove = columnChangeset.columnsToDrop,
                    columnsToModify = columnChangeset.columnsToChange,
                    recreatePrimaryKeyIndex = false,
                    primaryKeyColumnNames = emptyList(),
                    recreateCursorIndex = false,
                    cursorColumnName = null,
                )
            )
        }
    }

    /**
     * Gets columns from the database including their types for schema discovery. Unlike
     * [getColumnsFromDb], this returns all columns including Airbyte metadata columns.
     */
    private fun getColumnsFromDbForDiscovery(tableName: TableName): Map<String, ColumnType> =
        executeQuery(sqlGenerator.getTableSchema(tableName)) { rs ->
            val columnsInDb: MutableMap<String, ColumnType> = mutableMapOf()
            while (rs.next()) {
                val columnName = rs.getString(COLUMN_NAME_COLUMN)
                val dataType = rs.getString("data_type")
                // PostgreSQL's information_schema always returns 'YES' or 'NO' for is_nullable
                val isNullable = rs.getString("is_nullable") == "YES"

                columnsInDb[columnName] = ColumnType(normalizePostgresType(dataType), isNullable)
            }

            columnsInDb
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
    ): Boolean {
        val streamPrimaryKeys = sqlGenerator.getPrimaryKeysColumnNames(stream)
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
    ): Boolean {
        val streamCursor = sqlGenerator.getCursorColumnName(stream) ?: return false

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

    internal fun getColumnsFromDb(tableName: TableName): Map<String, ColumnType> =
        executeQuery(sqlGenerator.getTableSchema(tableName)) { rs ->
            val columnsInDb = mutableMapOf<String, ColumnType>()
            val defaultColumnNames = columnManager.getMetaColumnNames()
            while (rs.next()) {
                val columnName = rs.getString(COLUMN_NAME_COLUMN)

                // Filter out airbyte columns
                if (defaultColumnNames.contains(columnName)) {
                    continue
                }
                val dataType = rs.getString("data_type")
                val isNullable = rs.getString("is_nullable") == "YES"

                columnsInDb[columnName] = ColumnType(normalizePostgresType(dataType), isNullable)
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
        columnsInDb: Map<String, ColumnType>,
        columnsInStream: Map<String, ColumnType>
    ): Triple<Map<String, ColumnType>, Map<String, ColumnType>, Map<String, ColumnTypeChange>> {
        val addedColumns = columnsInStream.filterKeys { it !in columnsInDb.keys }
        val deletedColumns = columnsInDb.filterKeys { it !in columnsInStream.keys }

        val modifiedColumns = mutableMapOf<String, ColumnTypeChange>()
        columnsInStream.forEach { (name, streamType) ->
            val dbType = columnsInDb[name]
            if (dbType != null && dbType.type != streamType.type) {
                modifiedColumns[name] =
                    ColumnTypeChange(originalType = dbType, newType = streamType)
            }
        }

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
        try {
            dataSource.connection.use { connection ->
                connection.createStatement().use { it.execute(query) }
            }
        } catch (e: org.postgresql.util.PSQLException) {
            // Handle dependent objects error (e.g., views depending on tables/columns)
            // PostgreSQL error code 2BP01 = DEPENDENT_OBJECTS_STILL_EXIST
            if (e.sqlState == "2BP01" || e.message?.contains("depends on") == true) {
                val cascadeOptionMessage =
                    if (postgresConfiguration.dropCascade == true) {
                        "The 'Drop tables with CASCADE' option is already enabled, but the operation still failed. " +
                            "This can happen when views have complex dependencies that CASCADE cannot automatically resolve."
                    } else {
                        "You can enable the 'Drop tables with CASCADE' option in the destination configuration to automatically drop dependent objects. " +
                            "WARNING: This will delete all data in dependent objects (views, etc.)."
                    }
                val message =
                    "Failed to modify table because other database objects (such as views or rules) depend on it. " +
                        "Original error: ${e.message}\n\n" +
                        "$cascadeOptionMessage\n\n" +
                        "If the CASCADE option doesn't work or you want more control, you can manually drop the dependent views before running the sync, " +
                        "then recreate them afterward. To find dependent views, you can run: " +
                        "SELECT dependent_ns.nspname, dependent_view.relname FROM pg_depend " +
                        "JOIN pg_rewrite ON pg_depend.objid = pg_rewrite.oid " +
                        "JOIN pg_class as dependent_view ON pg_rewrite.ev_class = dependent_view.oid " +
                        "JOIN pg_namespace dependent_ns ON dependent_view.relnamespace = dependent_ns.oid " +
                        "WHERE pg_depend.refobjid = 'your_schema.your_table'::regclass;"
                log.error { message }
                throw ConfigErrorException(message, e)
            }
            throw e
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
