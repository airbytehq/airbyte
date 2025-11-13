/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.client

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableColumns
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAMES
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.mysql_v2.spec.MysqlConfiguration
import io.airbyte.integrations.destination.mysql_v2.sql.MysqlColumnUtils
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.SQLException
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

@Singleton
class MysqlAirbyteClient(
    val dataSource: DataSource,
    private val sqlGenerator: MysqlSqlGenerator,
    private val columnUtils: MysqlColumnUtils,
    private val config: MysqlConfiguration,
) : TableOperationsClient, TableSchemaEvolutionClient {

    // ========================================
    // TableOperationsClient Implementation
    // ========================================

    override suspend fun createNamespace(namespace: String) {
        execute(sqlGenerator.createNamespace(namespace))
    }

    override suspend fun namespaceExists(namespace: String): Boolean {
        return try {
            dataSource.connection.use { connection ->
                val statement = connection.createStatement()
                statement.use {
                    val resultSet = it.executeQuery(sqlGenerator.namespaceExists(namespace))
                    resultSet.next()
                }
            }
        } catch (e: SQLException) {
            log.debug(e) { "Failed to check if namespace exists: $namespace" }
            false
        }
    }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    ) {
        execute(sqlGenerator.createTable(stream, tableName, columnNameMapping, replace))
    }

    override suspend fun tableExists(table: TableName): Boolean {
        return try {
            dataSource.connection.use { connection ->
                val statement = connection.createStatement()
                statement.use {
                    val resultSet = it.executeQuery(
                        """
                        SELECT TABLE_NAME
                        FROM INFORMATION_SCHEMA.TABLES
                        WHERE TABLE_SCHEMA = '${table.namespace}'
                          AND TABLE_NAME = '${table.name}'
                        """.trimIndent()
                    )
                    resultSet.next()
                }
            }
        } catch (e: SQLException) {
            log.debug(e) { "Failed to check if table exists: ${table.toPrettyString()}" }
            false
        }
    }

    override suspend fun dropTable(tableName: TableName) {
        execute(sqlGenerator.dropTable(tableName))
    }

    override suspend fun countTable(tableName: TableName): Long? {
        return try {
            dataSource.connection.use { connection ->
                val statement = connection.createStatement()
                statement.use {
                    val resultSet = it.executeQuery(sqlGenerator.countTable(tableName))
                    if (resultSet.next()) {
                        resultSet.getLong("count")
                    } else {
                        0L
                    }
                }
            }
        } catch (e: SQLException) {
            log.debug(e) { "Table ${tableName.toPrettyString()} does not exist. Returning null..." }
            null
        }
    }

    override suspend fun getGenerationId(tableName: TableName): Long {
        return try {
            dataSource.connection.use { connection ->
                val statement = connection.createStatement()
                statement.use {
                    val resultSet = it.executeQuery(sqlGenerator.getGenerationId(tableName))
                    if (resultSet.next()) {
                        resultSet.getLong("generation_id")
                    } else {
                        0L
                    }
                }
            }
        } catch (e: SQLException) {
            log.error(e) { "Failed to retrieve the generation ID for ${tableName.toPrettyString()}" }
            0L
        }
    }

    override suspend fun overwriteTable(
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        val statements = sqlGenerator.overwriteTable(sourceTableName, targetTableName)
        statements.forEach { sql ->
            execute(sql)
        }
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        execute(sqlGenerator.copyTable(columnNameMapping, sourceTableName, targetTableName))
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        val statements = sqlGenerator.upsertTable(stream, columnNameMapping, sourceTableName, targetTableName)
        statements.forEach { sql ->
            execute(sql)
        }
    }

    // ========================================
    // TableSchemaEvolutionClient Implementation
    // ========================================

    override suspend fun discoverSchema(tableName: TableName): TableSchema {
        return try {
            dataSource.connection.use { connection ->
                val statement = connection.createStatement()
                statement.use {
                    val resultSet = it.executeQuery(
                        """
                        SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = '${tableName.namespace}'
                          AND TABLE_NAME = '${tableName.name}'
                        ORDER BY ORDINAL_POSITION
                        """.trimIndent()
                    )

                    val columns = mutableMapOf<String, ColumnType>()
                    val airbyteColumns = mutableSetOf<String>()

                    while (resultSet.next()) {
                        val columnName = resultSet.getString("COLUMN_NAME")
                        val columnType = resultSet.getString("COLUMN_TYPE")
                        val isNullable = resultSet.getString("IS_NULLABLE") == "YES"

                        // Track Airbyte columns separately
                        if (columnName in COLUMN_NAMES) {
                            airbyteColumns.add(columnName)
                        } else {
                            // Only include user columns in the schema
                            columns[columnName] = ColumnType(type = columnType, nullable = isNullable)
                        }
                    }

                    // Verify all Airbyte columns are present
                    val hasAllAirbyteColumns = airbyteColumns.containsAll(COLUMN_NAMES)
                    if (!hasAllAirbyteColumns) {
                        val message = "The target table ($tableName) already exists in the destination, but does not contain Airbyte's internal columns. Airbyte can only sync to Airbyte-controlled tables. To fix this error, you must either delete the target table or add a prefix in the connection configuration."
                        log.error { message }
                        throw ConfigErrorException(message)
                    }

                    log.info { "Discovered schema for ${tableName.toPrettyString()}: ${columns.size} user columns" }
                    TableSchema(columns)
                }
            }
        } catch (e: ConfigErrorException) {
            throw e
        } catch (e: SQLException) {
            log.error(e) { "Failed to discover schema for ${tableName.toPrettyString()}" }
            throw ConfigErrorException("Failed to discover schema for table ${tableName.toPrettyString()}", e)
        }
    }

    override fun computeSchema(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
    ): TableSchema {
        val importType = stream.importType

        // Extract primary key columns if this is a dedupe stream
        val primaryKeyColumns = if (importType is Dedupe) {
            importType.primaryKey.map { fieldPath -> columnNameMapping[fieldPath.first()]!! }.toSet()
        } else {
            emptySet()
        }

        // Extract cursor column if this is a dedupe stream
        val cursorColumn: Set<String> = if (importType is Dedupe) {
            if (importType.cursor.size > 1) {
                throw ConfigErrorException(
                    "Only top-level cursors are supported. Got ${importType.cursor}"
                )
            }
            importType.cursor.mapNotNull { fieldPath ->
                val fieldName: String = (fieldPath as List<String>).first()
                columnNameMapping[fieldName]
            }.toSet()
        } else {
            emptySet()
        }

        // Generate expected schema from stream
        val columns = stream.schema
            .asColumns()
            .filter { (name, _) -> name !in COLUMN_NAMES }
            .map { (fieldName, field) ->
                val mysqlColumnName = columnNameMapping[fieldName]!!

                // Primary key and cursor columns are non-nullable
                val nullable = field.nullable &&
                    !primaryKeyColumns.contains(mysqlColumnName) &&
                    !cursorColumn.contains(mysqlColumnName)

                val dialectType = columnUtils.toDialectType(field.type)

                mysqlColumnName to ColumnType(
                    type = dialectType,
                    nullable = nullable,
                )
            }
            .toMap()

        log.info { "Computed schema for stream ${stream.mappedDescriptor}: ${columns.size} columns" }
        return TableSchema(columns)
    }

    override suspend fun applyChangeset(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        tableName: TableName,
        expectedColumns: TableColumns,
        columnChangeset: ColumnChangeset,
    ) {
        if (columnChangeset.isNoop()) {
            log.info { "No schema changes needed for ${tableName.toPrettyString()}" }
            return
        }

        log.info { "Applying schema changes to ${tableName.toPrettyString()}" }
        log.info { "Columns to add: ${columnChangeset.columnsToAdd.keys}" }
        log.info { "Columns to drop: ${columnChangeset.columnsToDrop.keys}" }
        log.info { "Columns to change: ${columnChangeset.columnsToChange.keys}" }

        val alterStatements = sqlGenerator.alterTable(
            tableName,
            columnChangeset.columnsToAdd,
            columnChangeset.columnsToDrop,
            columnChangeset.columnsToChange,
        )

        alterStatements.forEach { sql ->
            execute(sql)
        }

        log.info { "Successfully applied ${alterStatements.size} schema change(s) to ${tableName.toPrettyString()}" }
    }

    // ========================================
    // Additional Methods
    // ========================================

    /**
     * Describes the columns in a table, returning an ordered map of column names to types.
     * This is used by the aggregate factory to build insert statements.
     */
    fun describeTable(tableName: TableName): LinkedHashMap<String, String> {
        return try {
            dataSource.connection.use { connection ->
                val statement = connection.createStatement()
                statement.use {
                    val resultSet = it.executeQuery(
                        """
                        SELECT COLUMN_NAME
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_SCHEMA = '${tableName.namespace}'
                          AND TABLE_NAME = '${tableName.name}'
                        ORDER BY ORDINAL_POSITION
                        """.trimIndent()
                    )

                    val columns = linkedMapOf<String, String>()
                    while (resultSet.next()) {
                        val columnName = resultSet.getString("COLUMN_NAME")
                        columns[columnName] = columnName
                    }
                    columns
                }
            }
        } catch (e: SQLException) {
            log.error(e) { "Failed to describe table ${tableName.toPrettyString()}" }
            throw ConfigErrorException(
                "Failed to describe table ${tableName.toPrettyString()}: ${e.message}",
                e
            )
        }
    }

    // ========================================
    // Private Helper Methods
    // ========================================

    private fun execute(sql: String) {
        try {
            dataSource.connection.use { connection ->
                val statement = connection.createStatement()
                statement.use {
                    it.execute(sql)
                }
            }
        } catch (e: SQLException) {
            log.error(e) { "Failed to execute SQL: $sql" }
            handleMysqlException(e)
        }
    }

    private fun handleMysqlException(e: SQLException): Nothing {
        val errorMessage = e.message?.lowercase() ?: ""

        when {
            errorMessage.contains("access denied") ||
            errorMessage.contains("permission denied") -> {
                throw ConfigErrorException(
                    "Permission denied. Please check your MySQL user has the required privileges: ${e.message}",
                    e
                )
            }
            errorMessage.contains("unknown database") -> {
                throw ConfigErrorException(
                    "Database does not exist: ${e.message}",
                    e
                )
            }
            errorMessage.contains("table") && errorMessage.contains("doesn't exist") -> {
                throw ConfigErrorException(
                    "Table does not exist: ${e.message}",
                    e
                )
            }
            errorMessage.contains("duplicate column") -> {
                throw ConfigErrorException(
                    "Column already exists: ${e.message}",
                    e
                )
            }
            else -> {
                // Re-throw as ConfigErrorException with context
                throw ConfigErrorException(
                    "MySQL error: ${e.message}",
                    e
                )
            }
        }
    }
}
