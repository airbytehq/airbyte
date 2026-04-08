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

/** Generates Redshift-specific SQL strings for table operations. All identifiers are double-quoted per Redshift/PostgreSQL convention. */
@Singleton
class RedshiftSqlGenerator {
    private val log = KotlinLogging.logger {}

    /** Generates `CREATE SCHEMA IF NOT EXISTS` SQL. */
    fun createNamespace(namespace: String): String =
        """CREATE SCHEMA IF NOT EXISTS "$namespace"""".andLog()

    /** Generates `CREATE TABLE IF NOT EXISTS` with Airbyte meta columns + user columns from [StreamTableSchema]. */
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

    /** Generates `DROP TABLE IF EXISTS` SQL. */
    fun dropTable(tableName: TableName): String =
        "DROP TABLE IF EXISTS ${tableName.quoted()}".andLog()

    /** Generates `SELECT count(1)` SQL. @param alias optional column alias for the count result. */
    fun countTable(tableName: TableName, alias: String = ""): String {
        val aliasClause = if (alias.isNotEmpty()) " $alias" else ""
        return "SELECT count(1)$aliasClause FROM ${tableName.quoted()}".andLog()
    }

    /** Generates a parameterized `INSERT INTO` with Airbyte meta columns + [columnNames]. For use with [java.sql.PreparedStatement]. */
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

    /** Generates a parameterized `DELETE` by `_airbyte_raw_id`. For use with [java.sql.PreparedStatement]. */
    fun deleteByRawId(tableName: TableName): String =
        "DELETE FROM ${tableName.quoted()} WHERE $COLUMN_NAME_AB_RAW_ID = ?".andLog()

    /** Quotes a [TableName] as `"namespace"."name"`. */
    private fun TableName.quoted(): String = "\"$namespace\".\"$name\""

    /** Renders a [ColumnType] as a Redshift type declaration, appending `NOT NULL` for non-nullable columns. */
    private fun ColumnType.typeDecl(): String =
        if (nullable) type else "$type NOT NULL"

    /** Logs the SQL string at INFO level and returns it. */
    private fun String.andLog(): String {
        log.info { this }
        return this
    }
}
