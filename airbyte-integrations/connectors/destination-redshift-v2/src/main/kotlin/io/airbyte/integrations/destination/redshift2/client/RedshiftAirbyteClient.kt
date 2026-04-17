/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.client

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableColumns
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAMES
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.redshift2.sql.RedshiftSqlGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.ResultSet
import java.sql.SQLException
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

private const val COUNT_TOTAL_ALIAS = "total"
private const val COLUMN_NAME_COLUMN = "column_name"

@Singleton
class RedshiftAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: RedshiftSqlGenerator
) : TableSchemaEvolutionClient, TableOperationsClient {

    override suspend fun createNamespace(namespace: String) {
        try {
            execute(sqlGenerator.createNamespace(namespace))
        } catch (e: SQLException) {
            // Swallow race condition where concurrent connections both try CREATE SCHEMA IF NOT
            // EXISTS
            if (e.message?.contains("already exists") != true) {
                throw e
            }
        }
    }

    override suspend fun namespaceExists(namespace: String): Boolean =
        executeQuery(sqlGenerator.namespaceExists(namespace)) { rs ->
            rs.next() && rs.getBoolean(1)
        }

    override suspend fun tableExists(table: TableName): Boolean =
        executeQuery(sqlGenerator.tableExists(table)) { rs -> rs.next() && rs.getBoolean(1) }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ) {
        execute(sqlGenerator.createTable(stream, tableName, replace))
    }

    override suspend fun dropTable(tableName: TableName) {
        execute(sqlGenerator.dropTable(tableName))
    }

    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        execute(sqlGenerator.overwriteTable(sourceTableName, targetTableName))
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        val metaColumnNames = getMetaColumnNames()
        val targetColumnNames = (metaColumnNames + columnNameMapping.values).toList()
        execute(sqlGenerator.copyTable(targetColumnNames, sourceTableName, targetTableName))
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        execute(sqlGenerator.upsertTable(stream, sourceTableName, targetTableName))
    }

    override suspend fun countTable(tableName: TableName): Long? =
        try {
            executeQuery(sqlGenerator.countTable(tableName)) { rs ->
                if (rs.next()) {
                    rs.getLong(COUNT_TOTAL_ALIAS)
                } else {
                    0L
                }
            }
        } catch (e: SQLException) {
            log.debug(e) {
                "Table ${tableName.namespace}.${tableName.name} does not exist. " +
                    "Count returning null to signal a missing table."
            }
            null
        }

    override suspend fun getGenerationId(tableName: TableName): Long =
        try {
            executeQuery(sqlGenerator.getGenerationId(tableName)) { rs ->
                if (rs.next()) {
                    rs.getLong(COLUMN_NAME_AB_GENERATION_ID)
                } else {
                    log.warn { "No generation ID found for table $tableName, returning 0" }
                    0L
                }
            }
        } catch (e: SQLException) {
            log.error(e) { "Failed to retrieve the generation ID for table $tableName" }
            0L
        }

    override suspend fun discoverSchema(tableName: TableName): TableSchema {
        val columnsInDb = getColumnsFromDbForDiscovery(tableName)
        val hasAllAirbyteColumns = columnsInDb.keys.containsAll(COLUMN_NAMES)

        if (!hasAllAirbyteColumns) {
            val message =
                "The target table (${tableName.namespace}.${tableName.name}) already exists " +
                    "in the destination, but does not contain Airbyte's internal columns. " +
                    "Airbyte can only sync to Airbyte-controlled tables. To fix this error, " +
                    "you must either delete the target table or add a prefix in the connection " +
                    "configuration in order to sync to a separate table in the destination."
            log.error { message }
            throw ConfigErrorException(message)
        }

        // Filter out Airbyte meta columns — return only user columns
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
        if (columnChangeset.isNoop()) {
            return
        }

        log.info { "Summary of table alterations for ${tableName.namespace}.${tableName.name}:" }
        log.info { "  Added columns: ${columnChangeset.columnsToAdd}" }
        log.info { "  Dropped columns: ${columnChangeset.columnsToDrop}" }
        log.info { "  Modified columns: ${columnChangeset.columnsToChange}" }

        execute(
            sqlGenerator.matchSchemas(
                tableName = tableName,
                columnsToAdd = columnChangeset.columnsToAdd,
                columnsToRemove = columnChangeset.columnsToDrop,
                columnsToModify = columnChangeset.columnsToChange
            )
        )
    }

    // ================================================================
    // Internal helpers
    // ================================================================

    internal fun getMetaColumnNames(): Set<String> = RedshiftSqlGenerator.META_COLUMNS.keys

    /**
     * Queries `information_schema.columns` for all columns in a table, including Airbyte meta
     * columns. Used by [discoverSchema] for schema evolution.
     */
    private fun getColumnsFromDbForDiscovery(tableName: TableName): Map<String, ColumnType> =
        executeQuery(sqlGenerator.getTableSchema(tableName)) { rs ->
            val columns: MutableMap<String, ColumnType> = mutableMapOf()
            while (rs.next()) {
                val columnName = rs.getString(COLUMN_NAME_COLUMN)
                val dataType = rs.getString("data_type")
                val isNullable = rs.getString("is_nullable") == "YES"
                columns[columnName] = ColumnType(normalizeRedshiftType(dataType), isNullable)
            }
            columns
        }

    /**
     * Normalizes Redshift type names from `information_schema.columns.data_type` to match the
     * internal type names used in DDL statements. Verified against a real Redshift cluster.
     *
     * Precision/scale/length are ignored: all varchars normalize to `varchar(65535)` and all
     * numerics normalize to `numeric(38,9)`
     */
    internal fun normalizeRedshiftType(redshiftType: String): String =
        when (redshiftType) {
            "character varying" -> "varchar(65535)"
            "numeric" -> "numeric(38,9)"
            "timestamp without time zone" -> "timestamp"
            "timestamp with time zone" -> "timestamptz"
            "time without time zone" -> "time"
            "time with time zone" -> "timetz"
            else -> redshiftType
        }

    /** Executes a SQL statement (DDL or DML) against Redshift */
    internal fun execute(query: String) {
        log.info { query.trimIndent() }
        try {
            dataSource.connection.use { connection ->
                connection.createStatement().use { it.execute(query) }
            }
        } catch (e: SQLException) {
            // PostgreSQL/Redshift error code 2BP01 = DEPENDENT_OBJECTS_STILL_EXIST
            if (e.sqlState == "2BP01" || e.message?.contains("depends on") == true) {
                val message =
                    "Failed to modify table because other database objects (such as views " +
                        "or rules) depend on it. Original error: ${e.message}\n\n" +
                        "You can manually drop the dependent views before running the sync, " +
                        "then recreate them afterward. To find dependent views, run:\n" +
                        "SELECT dependent_ns.nspname, dependent_view.relname " +
                        "FROM pg_depend " +
                        "JOIN pg_rewrite ON pg_depend.objid = pg_rewrite.oid " +
                        "JOIN pg_class AS dependent_view " +
                        "ON pg_rewrite.ev_class = dependent_view.oid " +
                        "JOIN pg_namespace dependent_ns " +
                        "ON dependent_view.relnamespace = dependent_ns.oid " +
                        "WHERE pg_depend.refobjid = 'your_schema.your_table'::regclass;"
                log.error { message }
                throw ConfigErrorException(message, e)
            }
            throw e
        }
    }

    /** Executes a SQL query and processes the [ResultSet] with the given [resultProcessor]. */
    private fun <T> executeQuery(query: String, resultProcessor: (ResultSet) -> T): T {
        log.info { query.trimIndent() }
        return dataSource.connection.use { connection ->
            connection.createStatement().use {
                it.executeQuery(query).use { resultSet -> resultProcessor(resultSet) }
            }
        }
    }
}
