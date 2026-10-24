/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.client

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableColumns
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAMES
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.SQLException
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

@Singleton
class MySQLAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: MySQLSqlGenerator,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : TableOperationsClient, TableSchemaEvolutionClient {

    // ========================================
    // NAMESPACE OPERATIONS
    // ========================================

    override suspend fun createNamespace(namespace: String) {
        execute(sqlGenerator.createNamespace(namespace))
    }

    override suspend fun namespaceExists(namespace: String): Boolean {
        return dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                val rs = statement.executeQuery(sqlGenerator.namespaceExists(namespace))
                rs.next()
            }
        }
    }

    // ========================================
    // TABLE OPERATIONS
    // ========================================

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ) {
        val sql = sqlGenerator.createTable(stream, tableName, columnNameMapping, replace)
        // Handle DROP and CREATE separately if replace is true
        if (replace) {
            execute(sqlGenerator.dropTable(tableName))
        }
        execute(sql.substringAfter(";\n").ifEmpty { sql })
    }

    override suspend fun dropTable(tableName: TableName) {
        execute(sqlGenerator.dropTable(tableName))
    }

    override suspend fun tableExists(table: TableName): Boolean {
        return countTable(table) != null
    }

    override suspend fun countTable(tableName: TableName): Long? {
        return try {
            dataSource.connection.use { connection ->
                connection.createStatement().use { statement ->
                    val rs = statement.executeQuery(sqlGenerator.countTable(tableName))
                    if (rs.next()) rs.getLong(1) else 0L
                }
            }
        } catch (e: SQLException) {
            log.debug(e) { "Table ${tableName.namespace}.${tableName.name} does not exist" }
            null
        }
    }

    override suspend fun getGenerationId(tableName: TableName): Long {
        return try {
            dataSource.connection.use { connection ->
                connection.createStatement().use { statement ->
                    val rs = statement.executeQuery(sqlGenerator.getGenerationId(tableName))
                    if (rs.next()) {
                        rs.getLong(1)
                    } else {
                        0L
                    }
                }
            }
        } catch (e: SQLException) {
            log.debug(e) { "Failed to retrieve generation ID, returning 0" }
            0L
        }
    }

    // ========================================
    // OVERWRITE AND COPY OPERATIONS
    // ========================================

    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        // Drop target table first, then rename source to target
        // This is not atomic but avoids temp table name collisions
        try {
            // Drop target table if it exists
            if (tableExists(targetTableName)) {
                execute(sqlGenerator.dropTable(targetTableName))
            }
            // Rename source to target
            execute(sqlGenerator.renameTable(sourceTableName, targetTableName))
        } catch (e: SQLException) {
            log.error(e) { "Failed to overwrite table" }
            throw e
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
        // upsertFromTable returns multiple statements separated by semicolons
        // Execute each statement separately within a transaction
        val statements = sqlGenerator.upsertFromTable(stream, columnNameMapping, sourceTableName, targetTableName)
            .split(";")
            .map { it.trim() }
            .filter { it.isNotEmpty() }

        dataSource.connection.use { connection ->
            connection.autoCommit = false
            try {
                statements.forEach { sql ->
                    connection.createStatement().use { statement ->
                        log.info { "Executing: $sql" }
                        statement.execute(sql)
                    }
                }
                connection.commit()
            } catch (e: Exception) {
                connection.rollback()
                throw e
            }
        }
    }

    // ========================================
    // SCHEMA EVOLUTION
    // ========================================

    override suspend fun discoverSchema(tableName: TableName): TableSchema {
        return dataSource.connection.use { connection ->
            val rs = connection.metaData.getColumns(
                tableName.namespace,
                null,
                tableName.name,
                null
            )

            val columns = mutableMapOf<String, ColumnType>()
            while (rs.next()) {
                val columnName = rs.getString("COLUMN_NAME")
                if (columnName !in COLUMN_NAMES) {
                    val typeName = rs.getString("TYPE_NAME")
                    val nullable = rs.getString("IS_NULLABLE") == "YES"
                    columns[columnName] = ColumnType(typeName, nullable)
                }
            }

            if (columns.isEmpty()) {
                val hasAllAirbyteColumns = dataSource.connection.use { conn ->
                    val colRs = conn.metaData.getColumns(tableName.namespace, null, tableName.name, null)
                    val existingCols = mutableListOf<String>()
                    while (colRs.next()) {
                        existingCols.add(colRs.getString("COLUMN_NAME"))
                    }
                    COLUMN_NAMES.all { it in existingCols }
                }

                if (!hasAllAirbyteColumns) {
                    throw ConfigErrorException(
                        "The target table (${tableName.namespace}.${tableName.name}) already exists but does not contain Airbyte's internal columns."
                    )
                }
            }

            TableSchema(columns)
        }
    }

    override fun computeSchema(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): TableSchema {
        val importType = stream.importType
        val primaryKey = if (importType is Dedupe) {
            sqlGenerator.extractPks(importType.primaryKey, columnNameMapping).toSet()
        } else {
            emptySet()
        }

        return TableSchema(
            stream.schema
                .asColumns()
                .map { (fieldName, fieldType) ->
                    val mysqlColumnName = columnNameMapping[fieldName]!!
                    val nullable = !primaryKey.contains(mysqlColumnName)
                    val type = fieldType.type.toDialectType()
                    mysqlColumnName to ColumnType(type = type, nullable = nullable)
                }
                .toMap()
        )
    }

    override suspend fun applyChangeset(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        tableName: TableName,
        expectedColumns: TableColumns,
        columnChangeset: ColumnChangeset,
    ) {
        if (!columnChangeset.isNoop()) {
            execute(sqlGenerator.alterTable(columnChangeset, tableName))
        }
    }

    // ========================================
    // HELPER METHODS
    // ========================================

    private fun execute(sql: String) {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement.execute(sql)
            }
        }
    }
}
