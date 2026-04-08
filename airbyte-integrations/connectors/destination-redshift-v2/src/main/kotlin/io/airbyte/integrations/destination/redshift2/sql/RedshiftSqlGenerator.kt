/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.sql

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

/**
 * Generates Redshift-specific SQL strings for table operations.
 *
 * This is a standalone SQL string generator (following the ClickHouse pattern).
 * It does not implement any CDK interface -- CDK integration happens at the
 * client layer (RedshiftAirbyteClient) which delegates SQL generation here.
 *
 * All identifiers are double-quoted per Redshift/PostgreSQL convention.
 */
@Singleton
class RedshiftSqlGenerator {
    private val log = KotlinLogging.logger {}

    // ---- Namespace ----

    /**
     * Generates SQL to create a schema if it does not already exist.
     *
     * ```sql
     * CREATE SCHEMA IF NOT EXISTS "my_schema"
     * ```
     */
    fun createNamespace(namespace: String): String =
        """CREATE SCHEMA IF NOT EXISTS "$namespace"""".andLog()

    // ---- Table DDL ----

    /**
     * Generates a CREATE TABLE IF NOT EXISTS statement with Airbyte meta columns
     * followed by user-defined columns from the stream schema.
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
    fun createTable(tableName: TableName, tableSchema: StreamTableSchema): String {
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

    /**
     * Generates a DROP TABLE IF EXISTS statement.
     *
     * ```sql
     * DROP TABLE IF EXISTS "schema"."table"
     * ```
     */
    fun dropTable(tableName: TableName): String =
        "DROP TABLE IF EXISTS ${tableName.quoted()}".andLog()

    // ---- Read ----

    /**
     * Generates a SELECT count query.
     *
     * ```sql
     * SELECT count(1) FROM "schema"."table"
     * ```
     *
     * @param alias Optional column alias for the count result.
     */
    fun countTable(tableName: TableName, alias: String = ""): String {
        val aliasClause = if (alias.isNotEmpty()) " $alias" else ""
        return "SELECT count(1)$aliasClause FROM ${tableName.quoted()}".andLog()
    }

    // ---- Write ----

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

    // ---- Delete ----

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

    // ---- Helpers ----

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
