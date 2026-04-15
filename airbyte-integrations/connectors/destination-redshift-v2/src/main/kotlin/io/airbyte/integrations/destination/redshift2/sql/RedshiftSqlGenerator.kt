/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.sql

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

/**
 * Generates Redshift-specific SQL strings for table operations. All identifiers are double-quoted
 * per Redshift/PostgreSQL convention.
 */
@Singleton
class RedshiftSqlGenerator {
    private val log = KotlinLogging.logger {}

    companion object {
        internal fun quoteIdentifier(identifier: String): String =
            RedshiftSqlEscapeUtils.quoteIdentifier(identifier)

        /** Airbyte meta columns and their Redshift-specific types. */
        internal val META_COLUMNS =
            linkedMapOf(
                Meta.COLUMN_NAME_AB_RAW_ID to
                    ColumnType(RedshiftDataType.VARCHAR_36.typeName, false),
                Meta.COLUMN_NAME_AB_EXTRACTED_AT to
                    ColumnType(RedshiftDataType.TIMESTAMPTZ.typeName, false),
                Meta.COLUMN_NAME_AB_META to ColumnType(RedshiftDataType.SUPER.typeName, false),
                Meta.COLUMN_NAME_AB_GENERATION_ID to
                    ColumnType(RedshiftDataType.BIGINT.typeName, false),
            )
    }

    fun createNamespace(namespace: String): String =
        "CREATE SCHEMA IF NOT EXISTS ${quoteIdentifier(namespace)};".andLog()

    fun dropTable(tableName: TableName): String =
        "DROP TABLE IF EXISTS ${getFullyQualifiedName(tableName)};".andLog()

    /** Simplified `CREATE TABLE` for check/test tables that don't have a `DestinationStream` */
    fun createTableForCheck(tableName: TableName, tableSchema: StreamTableSchema): String {
        val metaColumns = META_COLUMNS
        val userColumns = tableSchema.columnSchema.finalSchema

        val columnDeclarations =
            buildList {
                    metaColumns.forEach { (columnName, columnType) ->
                        val nullability = if (columnType.nullable) "" else " NOT NULL"
                        add("${quoteIdentifier(columnName)} ${columnType.type}$nullability")
                    }
                    userColumns.forEach { (columnName, columnType) ->
                        val nullability = if (columnType.nullable) "" else " NOT NULL"
                        add("${quoteIdentifier(columnName)} ${columnType.type}$nullability")
                    }
                }
                .joinToString(",\n    ")

        return """
            |CREATE TABLE IF NOT EXISTS ${getFullyQualifiedName(tableName)} (
            |    $columnDeclarations
            |);
        """
            .trimMargin()
            .andLog()
    }

    /** Generates an ALTER TABLE ADD COLUMN statement. */
    fun addColumn(tableName: TableName, columnName: String, columnType: String): String =
        "ALTER TABLE ${getFullyQualifiedName(tableName)} ADD COLUMN ${quoteIdentifier(columnName)} $columnType;".andLog()

    /** Generates `SELECT COUNT(*)` SQL with a fixed alias. */
    fun countTable(tableName: TableName): String =
        "SELECT COUNT(*) AS \"total\" FROM ${getFullyQualifiedName(tableName)};".andLog()

    /** Generates a parameterized `DELETE` by `_airbyte_raw_id`. */
    fun deleteByRawId(tableName: TableName): String =
        "DELETE FROM ${getFullyQualifiedName(tableName)} WHERE ${quoteIdentifier("_airbyte_raw_id")} = ?;".andLog()

    /** Generates a Redshift COPY command to load gzip CSV data from S3 */
    fun copyFromS3(
        tableName: TableName,
        s3Path: String,
        accessKeyId: String,
        secretAccessKey: String,
        region: String,
    ): String =
        """
            |COPY ${getFullyQualifiedName(tableName)}
            |FROM '$s3Path'
            |CREDENTIALS 'aws_access_key_id=$accessKeyId;aws_secret_access_key=$secretAccessKey'
            |CSV GZIP
            |REGION '$region'
            |TIMEFORMAT 'auto'
            |STATUPDATE OFF
            |IGNOREHEADER 1;
        """.trimMargin()

    /** Builds the fully qualified table name as `"namespace"."name"`. */
    private fun getFullyQualifiedName(tableName: TableName): String =
        "${getNamespace(tableName)}.${getName(tableName)}"

    private fun getNamespace(tableName: TableName): String =
        quoteIdentifier(tableName.namespace.ifBlank { "public" })

    private fun getName(tableName: TableName): String = quoteIdentifier(tableName.name)

    /** Logs the SQL string at INFO level and returns it. */
    private fun String.andLog(): String {
        log.info { this }
        return this
    }
}
