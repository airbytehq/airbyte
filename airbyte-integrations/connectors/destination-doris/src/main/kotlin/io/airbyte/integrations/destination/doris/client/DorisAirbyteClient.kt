/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.client

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableColumns
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAMES
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.sql.Connection

private val log = KotlinLogging.logger {}

@Singleton
class DorisAirbyteClient(
    @Named("dorisJdbcConnection") private val connection: Connection,
    private val sqlGenerator: DorisSqlGenerator,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : TableOperationsClient, TableSchemaEvolutionClient {

    override suspend fun createNamespace(namespace: String) {
        execute(sqlGenerator.createNamespace(namespace))
    }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ) {
        val sql = sqlGenerator.createTable(tableName, stream.tableSchema, replace)
        // createTable may contain multiple statements (DROP + CREATE) when replace=true
        sql.split(";").filter { it.isNotBlank() }.forEach { execute(it.trim()) }
    }

    override suspend fun dropTable(tableName: TableName) {
        execute(sqlGenerator.dropTable(tableName))
    }

    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        // Doris does not support EXCHANGE TABLES; use DROP + RENAME
        execute(sqlGenerator.dropTable(targetTableName))
        execute(sqlGenerator.renameTable(sourceTableName, targetTableName))
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        val columnNames = columnNameMapping.values.toSet()
        execute(sqlGenerator.copyTable(columnNames, sourceTableName, targetTableName))
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        // Doris UNIQUE KEY model handles dedup natively via INSERT INTO SELECT.
        // When inserting into a UNIQUE KEY table, rows with duplicate keys are replaced.
        val columnNames = columnNameMapping.values.toSet()
        execute(sqlGenerator.copyTable(columnNames, sourceTableName, targetTableName))
    }

    override suspend fun discoverSchema(tableName: TableName): TableSchema {
        val columns = mutableMapOf<String, ColumnType>()

        connection.createStatement().use { stmt ->
            stmt.executeQuery(
                    "SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE " +
                        "FROM information_schema.COLUMNS " +
                        "WHERE TABLE_SCHEMA = '${tableName.namespace}' " +
                        "AND TABLE_NAME = '${tableName.name}' " +
                        "ORDER BY ORDINAL_POSITION"
                )
                .use { rs ->
                    while (rs.next()) {
                        val colName = rs.getString("COLUMN_NAME")
                        val colType = rs.getString("COLUMN_TYPE").uppercase()
                        val nullable = rs.getString("IS_NULLABLE") == "YES"

                        if (colName !in COLUMN_NAMES) {
                            columns[colName] = ColumnType(mapDorisTypeToInternal(colType), nullable)
                        }
                    }
                }
        }

        val hasAllAirbyteColumns =
            connection.createStatement().use { stmt ->
                val rs =
                    stmt.executeQuery(
                        "SELECT COLUMN_NAME FROM information_schema.COLUMNS " +
                            "WHERE TABLE_SCHEMA = '${tableName.namespace}' " +
                            "AND TABLE_NAME = '${tableName.name}'"
                    )
                val existingColumns = mutableSetOf<String>()
                while (rs.next()) {
                    existingColumns.add(rs.getString("COLUMN_NAME"))
                }
                existingColumns.containsAll(COLUMN_NAMES)
            }

        if (!hasAllAirbyteColumns) {
            throw ConfigErrorException(
                "The target table ($tableName) already exists but does not contain Airbyte's internal columns."
            )
        }

        return TableSchema(columns)
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
        columnChangeset: ColumnChangeset,
    ) {
        if (columnChangeset.isNoop()) return

        // Check if PK/dedup changes require table recreation
        val anyNullabilityChange =
            columnChangeset.columnsToChange.values.any {
                it.originalType.nullable != it.newType.nullable
            } || columnChangeset.columnsToDrop.values.any { !it.nullable }

        if (anyNullabilityChange) {
            log.info { "Detected deduplication change for table $tableName, recreating table" }
            applyDeduplicationChanges(stream, tableName, columnChangeset)
        } else {
            // Doris ALTER TABLE only supports one operation per statement
            val sql = sqlGenerator.alterTable(columnChangeset, tableName)
            sql.split(";\n").filter { it.isNotBlank() }.forEach { execute(it.trim()) }
        }
    }

    private suspend fun applyDeduplicationChanges(
        stream: DestinationStream,
        properTableName: TableName,
        columnChangeset: ColumnChangeset,
    ) {
        val tempTableName = tempTableNameGenerator.generate(properTableName)
        execute(sqlGenerator.createNamespace(tempTableName.namespace))
        val createSql = sqlGenerator.createTable(tempTableName, stream.tableSchema, true)
        createSql.split(";").filter { it.isNotBlank() }.forEach { execute(it.trim()) }

        val columnNames =
            columnChangeset.columnsToChange.keys + columnChangeset.columnsToRetain.keys
        execute(sqlGenerator.copyTable(columnNames, properTableName, tempTableName))
        overwriteTable(tempTableName, properTableName)
    }

    override suspend fun countTable(tableName: TableName): Long? {
        return try {
            connection.createStatement().use { stmt ->
                stmt.executeQuery(sqlGenerator.countTable(tableName, "cnt")).use { rs ->
                    if (rs.next()) rs.getLong("cnt") else null
                }
            }
        } catch (_: Exception) {
            null
        }
    }

    override suspend fun getGenerationId(tableName: TableName): Long {
        return try {
            connection.createStatement().use { stmt ->
                stmt.executeQuery(sqlGenerator.getGenerationId(tableName, "generation")).use { rs ->
                    if (rs.next()) rs.getLong("generation") else 0L
                }
            }
        } catch (e: Exception) {
            log.error(e) { "Failed to retrieve the generation Id" }
            0L
        }
    }

    override suspend fun namespaceExists(namespace: String): Boolean {
        return try {
            connection.createStatement().use { stmt ->
                stmt.executeQuery(
                        "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = '$namespace'"
                    )
                    .use { rs -> rs.next() }
            }
        } catch (_: Exception) {
            false
        }
    }

    override suspend fun tableExists(table: TableName): Boolean {
        return try {
            connection.createStatement().use { stmt ->
                stmt.executeQuery(
                        "SELECT TABLE_NAME FROM information_schema.TABLES " +
                            "WHERE TABLE_SCHEMA = '${table.namespace}' AND TABLE_NAME = '${table.name}'"
                    )
                    .use { rs -> rs.next() }
            }
        } catch (_: Exception) {
            false
        }
    }

    private fun execute(sql: String) {
        connection.createStatement().use { stmt -> stmt.execute(sql) }
    }

    private fun mapDorisTypeToInternal(dorisType: String): String {
        return when {
            dorisType.startsWith("DATETIME") -> DorisSqlTypes.DATETIME
            dorisType.startsWith("DECIMAL") -> DorisSqlTypes.DECIMAL
            dorisType.startsWith("VARCHAR") || dorisType == "TEXT" || dorisType == "STRING" ->
                DorisSqlTypes.STRING
            dorisType == "BIGINT" || dorisType == "INT" || dorisType == "LARGEINT" ->
                DorisSqlTypes.BIGINT
            dorisType == "BOOLEAN" || dorisType == "TINYINT" -> DorisSqlTypes.BOOLEAN
            dorisType == "DATE" -> DorisSqlTypes.DATE
            dorisType == "JSON" || dorisType == "JSONB" -> DorisSqlTypes.JSON
            dorisType == "DOUBLE" || dorisType == "FLOAT" -> DorisSqlTypes.DECIMAL
            else -> DorisSqlTypes.STRING
        }
    }
}
