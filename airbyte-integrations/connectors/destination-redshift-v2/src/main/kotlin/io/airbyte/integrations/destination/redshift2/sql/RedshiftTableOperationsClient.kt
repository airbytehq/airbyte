/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.sql

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import javax.sql.DataSource

/**
 * Redshift implementation of [TableOperationsClient].
 *
 * This is a combined SQL generator + executor (single-class pattern). It generates
 * Redshift-specific SQL and executes it against the database via [DataSource].
 *
 * All identifiers are double-quoted per Redshift/PostgreSQL convention.
 *
 * Interface methods ([createNamespace], [createTable], [dropTable], [countTable]) generate SQL
 * and execute it internally. Extra methods ([insertRow], [deleteByRawId], and the SQL-generation
 * overloads) return SQL strings for use with [java.sql.PreparedStatement] or manual execution.
 */
@Singleton
class RedshiftTableOperationsClient(
    private val dataSource: DataSource,
) : TableOperationsClient {
    private val log = KotlinLogging.logger {}

    // ================================================================
    // TableOperationsClient interface implementations
    // ================================================================

    // ---- Namespace ----

    /**
     * Creates a schema if it does not already exist.
     *
     * ```sql
     * CREATE SCHEMA IF NOT EXISTS "my_schema"
     * ```
     */
    override suspend fun createNamespace(namespace: String) {
        execute(createNamespaceSql(namespace))
    }

    // ---- Table DDL ----

    /**
     * Creates a table with the given schema and column mapping.
     *
     * Extracts [StreamTableSchema] from [stream] and delegates to [buildCreateTableSql]
     * for SQL generation. The [columnNameMapping] is not currently used (columns are taken
     * directly from the stream's final schema). The [replace] parameter is reserved for
     * future use.
     */
    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    ) {
        execute(buildCreateTableSql(tableName, stream.tableSchema))
    }

    /**
     * Drops a table if it exists.
     *
     * ```sql
     * DROP TABLE IF EXISTS "schema"."table"
     * ```
     */
    override suspend fun dropTable(tableName: TableName) {
        execute(dropTableSql(tableName))
    }

    /**
     * Returns the row count of a table, or null if the table doesn't exist or the query fails.
     */
    override suspend fun countTable(tableName: TableName): Long? {
        return try {
            executeQuery("SELECT count(1) FROM ${tableName.quoted()}".andLog()) { rs ->
                if (rs.next()) rs.getLong(1) else null
            }
        } catch (@Suppress("TooGenericExceptionCaught") e: Exception) {
            null
        }
    }

    // ---- Not yet implemented ----

    override suspend fun overwriteTable(
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        TODO("Not yet implemented")
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        TODO("Not yet implemented")
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        TODO("Not yet implemented")
    }

    // ================================================================
    // Extra methods — SQL generation
    // ================================================================

    /**
     * Returns the SQL string for creating a schema.
     * Use this when you need the raw SQL (e.g. in [RedshiftChecker][io.airbyte.integrations.destination.redshift2.check.RedshiftChecker]).
     */
    fun createNamespaceSql(namespace: String): String =
        """CREATE SCHEMA IF NOT EXISTS "$namespace"""".andLog()

    /**
     * Generates a CREATE TABLE IF NOT EXISTS statement from a [StreamTableSchema].
     *
     * This overload is useful when a [DestinationStream] is not available (e.g. in the
     * connection checker). Returns the SQL string for manual execution.
     *
     * Meta columns:
     * - `_airbyte_raw_id`        VARCHAR(36) NOT NULL
     * - `_airbyte_extracted_at`   TIMESTAMPTZ NOT NULL
     * - `_airbyte_meta`           SUPER NOT NULL
     * - `_airbyte_generation_id`  BIGINT NOT NULL
     *
     * User columns are derived from [StreamTableSchema.columnSchema.finalSchema],
     * with types and nullability from [ColumnType].
     */
    fun createTable(tableName: TableName, tableSchema: StreamTableSchema): String =
        buildCreateTableSql(tableName, tableSchema)

    /**
     * Returns the SQL string for dropping a table.
     * Use this when you need the raw SQL for manual execution.
     */
    fun dropTableSql(tableName: TableName): String =
        "DROP TABLE IF EXISTS ${tableName.quoted()}".andLog()

    /**
     * Returns the SQL string for a SELECT count query.
     * Use this when you need the raw SQL for manual execution.
     *
     * @param alias Optional column alias for the count result.
     */
    fun countTableSql(tableName: TableName, alias: String = ""): String {
        val aliasClause = if (alias.isNotEmpty()) " $alias" else ""
        return "SELECT count(1)$aliasClause FROM ${tableName.quoted()}".andLog()
    }

    /**
     * Generates a parameterized INSERT statement for use with [java.sql.PreparedStatement].
     *
     * The column list always starts with the four Airbyte meta columns, followed by
     * the provided user column names. Values are placeholder `?` markers.
     *
     * ```sql
     * INSERT INTO "schema"."table" ("_airbyte_raw_id", ..., "user_col") VALUES (?, ?, ...)
     * ```
     *
     * @param columnNames User-defined column names (excluding meta columns).
     */
    fun insertRow(tableName: TableName, columnNames: List<String>): String {
        val allColumns =
            listOf(
                COLUMN_NAME_AB_RAW_ID,
                COLUMN_NAME_AB_EXTRACTED_AT,
                COLUMN_NAME_AB_META,
                COLUMN_NAME_AB_GENERATION_ID,
            ) + columnNames

        val quotedColumns = allColumns.joinToString(", ") { "\"$it\"" }
        val placeholders = allColumns.joinToString(", ") { "?" }

        return "INSERT INTO ${tableName.quoted()} ($quotedColumns) VALUES ($placeholders)"
            .andLog()
    }

    /**
     * Generates a parameterized DELETE statement that removes a row by its
     * `_airbyte_raw_id` value. For use with [java.sql.PreparedStatement].
     *
     * ```sql
     * DELETE FROM "schema"."table" WHERE _airbyte_raw_id = ?
     * ```
     */
    fun deleteByRawId(tableName: TableName): String =
        "DELETE FROM ${tableName.quoted()} WHERE $COLUMN_NAME_AB_RAW_ID = ?".andLog()

    // ================================================================
    // Private helpers
    // ================================================================

    /** Builds the CREATE TABLE SQL from a [StreamTableSchema]. */
    private fun buildCreateTableSql(
        tableName: TableName,
        tableSchema: StreamTableSchema,
    ): String {
        val userColumns =
            tableSchema.columnSchema.finalSchema
                .map { (columnName, columnType) -> "\"$columnName\" ${columnType.typeDecl()}" }
                .joinToString(",\n    ")

        val userColumnBlock = if (userColumns.isNotEmpty()) ",\n    $userColumns" else ""

        return """
            |CREATE TABLE IF NOT EXISTS ${tableName.quoted()} (
            |    $COLUMN_NAME_AB_RAW_ID ${RedshiftSqlTypes.VARCHAR_36} NOT NULL,
            |    $COLUMN_NAME_AB_EXTRACTED_AT ${RedshiftSqlTypes.TIMESTAMPTZ} NOT NULL,
            |    $COLUMN_NAME_AB_META ${RedshiftSqlTypes.SUPER} NOT NULL,
            |    $COLUMN_NAME_AB_GENERATION_ID ${RedshiftSqlTypes.BIGINT} NOT NULL$userColumnBlock
            |)
            """
            .trimMargin()
            .andLog()
    }

    /** Executes a DDL/DML statement. */
    private fun execute(sql: String) {
        dataSource.connection.use { conn ->
            conn.createStatement().use { stmt ->
                stmt.execute(sql)
            }
        }
    }

    /** Executes a query and processes the result set. */
    private fun <T> executeQuery(
        sql: String,
        resultProcessor: (java.sql.ResultSet) -> T,
    ): T {
        return dataSource.connection.use { conn ->
            conn.createStatement().use { stmt ->
                stmt.executeQuery(sql).use { rs ->
                    resultProcessor(rs)
                }
            }
        }
    }

    /** Quotes a [TableName] as `"namespace"."name"` for Redshift SQL. */
    private fun TableName.quoted(): String = "\"$namespace\".\"$name\""

    /**
     * Renders a [ColumnType] as a Redshift type declaration.
     * Non-nullable columns get a `NOT NULL` constraint; nullable columns
     * are left unconstrained (Redshift columns are nullable by default).
     */
    private fun ColumnType.typeDecl(): String =
        if (nullable) type else "$type NOT NULL"

    /** Logs the SQL string at INFO level and returns it. */
    private fun String.andLog(): String {
        log.info { this }
        return this
    }
}
