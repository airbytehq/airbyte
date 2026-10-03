/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.client

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableColumns
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.redshift_v2.sql.COUNT_TOTAL_ALIAS
import io.airbyte.integrations.destination.redshift_v2.sql.RedshiftColumnUtils
import io.airbyte.integrations.destination.redshift_v2.sql.RedshiftSqlGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.ResultSet
import java.sql.SQLException
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

@Singleton
@SuppressFBWarnings(value = ["NP_NONNULL_PARAM_VIOLATION"], justification = "kotlin coroutines")
class RedshiftAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: RedshiftSqlGenerator,
    private val columnUtils: RedshiftColumnUtils,
) : TableOperationsClient, TableSchemaEvolutionClient {

    private val airbyteColumnNames = columnUtils.getFormattedDefaultColumnNames(false).toSet()

    override suspend fun countTable(tableName: TableName): Long? =
        try {
            dataSource.connection.use { connection ->
                connection.createStatement().use { statement ->
                    val resultSet = statement.executeQuery(sqlGenerator.countTable(tableName))
                    if (resultSet.next()) {
                        resultSet.getLong(COUNT_TOTAL_ALIAS)
                    } else {
                        0L
                    }
                }
            }
        } catch (e: SQLException) {
            log.debug(e) {
                "Table ${tableName.toPrettyString()} does not exist. Returning null count."
            }
            null
        }

    override suspend fun tableExists(table: TableName): Boolean = countTable(table) != null

    override suspend fun namespaceExists(namespace: String): Boolean {
        return dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                val resultSet = statement.executeQuery(sqlGenerator.namespaceExists(namespace))
                resultSet.next()
            }
        }
    }

    override suspend fun createNamespace(namespace: String) {
        try {
            if (!namespaceExists(namespace)) {
                execute(sqlGenerator.createNamespace(namespace))
            }
        } catch (e: SQLException) {
            handleRedshiftPermissionError(e)
        }
    }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ) {
        execute(sqlGenerator.createTable(stream, tableName, columnNameMapping, replace))
    }

    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        log.info {
            "overwriteTable: source=${sourceTableName.toPrettyString()}, target=${targetTableName.toPrettyString()}"
        }

        // Redshift doesn't support ALTER TABLE SET SCHEMA, so we need different approaches
        // depending on whether source and target are in the same schema
        if (sourceTableName.namespace == targetTableName.namespace) {
            // Same schema: simple rename
            execute(sqlGenerator.dropTable(targetTableName))
            execute(sqlGenerator.renameTable(sourceTableName, targetTableName))
        } else {
            // Cross-schema: use ALTER TABLE APPEND approach
            // 1. Drop target if exists
            execute(sqlGenerator.dropTable(targetTableName))
            // 2. Create empty target table with same schema as source
            execute(sqlGenerator.createTableLike(sourceTableName, targetTableName))
            // 3. Move data from source to target using ALTER TABLE APPEND
            execute(sqlGenerator.appendTable(sourceTableName, targetTableName))
            // 4. Drop the now-empty source table
            execute(sqlGenerator.dropTable(sourceTableName))
        }
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
        log.info {
            "upsertTable: source=${sourceTableName.toPrettyString()}, target=${targetTableName.toPrettyString()}"
        }
        // Execute all upsert statements (DELETE + INSERT pattern)
        sqlGenerator
            .upsertTable(stream, columnNameMapping, sourceTableName, targetTableName)
            .forEach { execute(it) }
    }

    override suspend fun dropTable(tableName: TableName) {
        execute(sqlGenerator.dropTable(tableName))
    }

    override suspend fun getGenerationId(tableName: TableName): Long =
        try {
            dataSource.connection.use { connection ->
                connection.createStatement().use { statement ->
                    val resultSet = statement.executeQuery(sqlGenerator.getGenerationId(tableName))
                    if (resultSet.next()) {
                        resultSet.getLong(columnUtils.getGenerationIdColumnName())
                    } else {
                        log.info {
                            "No generation ID found for table ${tableName.toPrettyString()}, returning 0"
                        }
                        0L
                    }
                }
            }
        } catch (e: SQLException) {
            handleRedshiftPermissionError(e)
        }

    /**
     * Normalize Redshift data type names to canonical forms. Redshift uses various synonyms for the
     * same types:
     * - CHARACTER VARYING -> VARCHAR
     * - TIMESTAMP WITH TIME ZONE -> TIMESTAMPTZ
     * - TIMESTAMP WITHOUT TIME ZONE -> TIMESTAMP
     * - TIME WITH TIME ZONE -> TIMETZ
     * - TIME WITHOUT TIME ZONE -> TIME
     * - DOUBLE PRECISION -> DOUBLE
     */
    private fun normalizeRedshiftType(dataType: String): String {
        return when (dataType.uppercase().trim()) {
            "CHARACTER VARYING" -> "VARCHAR"
            "CHARACTER" -> "CHAR"
            "TIMESTAMP WITH TIME ZONE" -> "TIMESTAMPTZ"
            "TIMESTAMP WITHOUT TIME ZONE" -> "TIMESTAMP"
            "TIME WITH TIME ZONE" -> "TIMETZ"
            "TIME WITHOUT TIME ZONE" -> "TIME"
            "DOUBLE PRECISION" -> "DOUBLE"
            "INT8",
            "INT64" -> "BIGINT"
            "INT4",
            "INT32" -> "INTEGER"
            "INT2",
            "INT16" -> "SMALLINT"
            "FLOAT8" -> "DOUBLE"
            "FLOAT4" -> "REAL"
            "BOOL" -> "BOOLEAN"
            else -> dataType.uppercase()
        }
    }

    internal fun getColumnsFromStream(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): Map<String, ColumnType> =
        stream.schema
            .asColumns()
            .mapNotNull { (fieldName, fieldType) ->
                val columnName = columnNameMapping[fieldName] ?: fieldName
                if (columnName in airbyteColumnNames) {
                    null
                } else {
                    val rawType = columnUtils.toDialectType(fieldType.type)
                    // Strip size specifier (e.g., VARCHAR(65535) -> VARCHAR) to match
                    // getColumnsFromDb
                    val baseType = rawType.takeWhile { it != '(' }
                    val type = normalizeRedshiftType(baseType)
                    columnName to ColumnType(type, fieldType.nullable)
                }
            }
            .toMap()

    // ========================================
    // TableSchemaEvolutionClient IMPLEMENTATION
    // ========================================

    override suspend fun discoverSchema(tableName: TableName): TableSchema {
        try {
            val sql = sqlGenerator.describeTable(tableName.namespace, tableName.name)
            dataSource.connection.use { connection ->
                connection.createStatement().use { statement ->
                    val resultSet = statement.executeQuery(sql)
                    val columnsInDb = mutableMapOf<String, ColumnType>()

                    while (resultSet.next()) {
                        val columnName = resultSet.getString("column_name")
                        if (airbyteColumnNames.contains(columnName)) {
                            continue
                        }
                        val rawDataType =
                            resultSet.getString("data_type").uppercase().takeWhile { char ->
                                char != '('
                            }
                        val dataType = normalizeRedshiftType(rawDataType)
                        val nullable = resultSet.getString("is_nullable") == "YES"

                        columnsInDb[columnName] = ColumnType(dataType, nullable)
                    }
                    return TableSchema(columnsInDb)
                }
            }
        } catch (e: SQLException) {
            handleRedshiftPermissionError(e)
        }
    }

    override fun computeSchema(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): TableSchema {
        // Compute schema from stream.schema directly, not from stream.tableSchema
        // which is a mock in tests (emptyTableSchema)
        return TableSchema(getColumnsFromStream(stream, columnNameMapping))
    }

    override suspend fun applyChangeset(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        tableName: TableName,
        expectedColumns: TableColumns,
        columnChangeset: ColumnChangeset,
    ) {
        if (
            columnChangeset.columnsToAdd.isNotEmpty() ||
                columnChangeset.columnsToDrop.isNotEmpty() ||
                columnChangeset.columnsToChange.isNotEmpty()
        ) {
            log.info { "Summary of the table alterations for ${tableName.toPrettyString()}:" }
            log.info { "Added columns: ${columnChangeset.columnsToAdd}" }
            log.info { "Deleted columns: ${columnChangeset.columnsToDrop}" }
            log.info { "Modified columns: ${columnChangeset.columnsToChange}" }

            sqlGenerator
                .alterTable(
                    tableName,
                    columnChangeset.columnsToAdd,
                    columnChangeset.columnsToDrop,
                    columnChangeset.columnsToChange,
                )
                .forEach { execute(it) }
        }
    }

    internal fun execute(query: String): ResultSet =
        try {
            dataSource.connection.use { connection ->
                connection.createStatement().use { statement ->
                    // Use execute() instead of executeQuery() to handle both
                    // SELECT (returns results) and INSERT/UPDATE/DDL (no results)
                    val hasResultSet = statement.execute(query)
                    if (hasResultSet) {
                        statement.resultSet
                    } else {
                        // Return empty result set for statements without results
                        connection.createStatement().executeQuery("SELECT 1 WHERE 1=0")
                    }
                }
            }
        } catch (e: SQLException) {
            handleRedshiftPermissionError(e)
        }

    private fun handleRedshiftPermissionError(e: SQLException): Nothing {
        val errorMessage = e.message?.lowercase() ?: ""
        when {
            errorMessage.contains("permission denied") ||
                errorMessage.contains("insufficient privileges") -> {
                throw ConfigErrorException(e.message ?: "Permission error", e)
            }
            else -> throw e
        }
    }
}
