/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.client

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
import io.airbyte.integrations.destination.databricksv2.sql.DatabricksSqlGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.ResultSet
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

@Singleton
class DatabricksAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: DatabricksSqlGenerator,
) : TableOperationsClient, TableSchemaEvolutionClient {

    override suspend fun createNamespace(namespace: String) {
        execute(sqlGenerator.createNamespace(namespace))
    }

    override suspend fun namespaceExists(namespace: String): Boolean =
        executeQuery(sqlGenerator.namespaceExists(namespace)) { rs ->
            rs.next() && rs.getBoolean("schema_exists")
        }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    ) {
        execute(sqlGenerator.createTable(tableName, stream.tableSchema, replace))
    }

    override suspend fun tableExists(table: TableName): Boolean =
        executeQuery(sqlGenerator.tableExists(table)) { rs ->
            rs.next() && rs.getBoolean("table_exists")
        }

    override suspend fun dropTable(tableName: TableName) {
        execute(sqlGenerator.dropTable(tableName))
    }

    override suspend fun countTable(tableName: TableName): Long? =
        try {
            executeQuery(sqlGenerator.countTable(tableName)) { rs ->
                if (rs.next()) rs.getLong(1) else 0L
            }
        } catch (_: Exception) {
            null
        }

    override suspend fun getGenerationId(tableName: TableName): Long =
        try {
            executeQuery(sqlGenerator.getGenerationId(tableName)) { rs ->
                if (rs.next()) rs.getLong(1) else 0L
            }
        } catch (e: Exception) {
            log.error(e) { "Failed to retrieve generation ID for ${tableName.toPrettyString()}" }
            0L
        }

    override suspend fun overwriteTable(
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        execute(sqlGenerator.overwriteTable(sourceTableName, targetTableName))
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        val columnNames = buildSet {
            addAll(sqlGenerator.getMetaColumnNames())
            addAll(columnNameMapping.values)
        }
        execute(sqlGenerator.copyTable(columnNames, sourceTableName, targetTableName))
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        execute(sqlGenerator.upsertTable(stream.tableSchema, sourceTableName, targetTableName))
    }

    override suspend fun discoverSchema(tableName: TableName): TableSchema {
        val columns =
            executeQuery(sqlGenerator.getTableSchema(tableName)) { rs ->
                val result = mutableMapOf<String, ColumnType>()
                val allColumnNames = mutableSetOf<String>()

                while (rs.next()) {
                    val name = rs.getString("column_name")
                    val type = rs.getString("data_type")
                    val nullable = rs.getString("is_nullable") == "YES"
                    allColumnNames.add(name)

                    // Filter out Airbyte meta columns — only return user columns
                    if (name !in COLUMN_NAMES) {
                        result[name] = ColumnType(type, nullable)
                    }
                }

                // Validate that all required meta columns exist
                if (!allColumnNames.containsAll(COLUMN_NAMES)) {
                    val missing = COLUMN_NAMES - allColumnNames
                    throw ConfigErrorException(
                        "Table ${tableName.toPrettyString()} is missing Airbyte meta columns: " +
                            "$missing. Airbyte can only sync to Airbyte-managed tables."
                    )
                }

                result
            }

        return TableSchema(columns)
    }

    override fun computeSchema(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
    ): TableSchema = TableSchema(stream.tableSchema.columnSchema.finalSchema)

    override suspend fun applyChangeset(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        tableName: TableName,
        expectedColumns: TableColumns,
        columnChangeset: ColumnChangeset,
    ) {
        if (!columnChangeset.isNoop()) {
            log.info { "Applying schema changes to ${tableName.toPrettyString()}:" }
            log.info { "  Added: ${columnChangeset.columnsToAdd.keys}" }
            log.info { "  Dropped: ${columnChangeset.columnsToDrop.keys}" }
            log.info { "  Modified: ${columnChangeset.columnsToChange.keys}" }
            execute(sqlGenerator.alterTable(tableName, columnChangeset))
        }
    }

    private fun execute(sql: String) {
        dataSource.connection.use { conn -> conn.createStatement().use { it.execute(sql) } }
    }

    private fun <T> executeQuery(sql: String, handler: (ResultSet) -> T): T =
        dataSource.connection.use { conn ->
            conn.createStatement().use { stmt -> stmt.executeQuery(sql).use { rs -> handler(rs) } }
        }
}
