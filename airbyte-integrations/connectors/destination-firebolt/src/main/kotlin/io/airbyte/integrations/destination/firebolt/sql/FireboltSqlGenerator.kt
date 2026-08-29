/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.sql

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import jakarta.inject.Singleton

@Singleton
class FireboltSqlGenerator {

    companion object {
        private val EXTRACTED_AT_COLUMN_NAME = quoteIdentifier(COLUMN_NAME_AB_EXTRACTED_AT)
        private val DELETED_AT_COLUMN_NAME = quoteIdentifier(CDC_DELETED_AT_COLUMN)

        internal fun quoteIdentifier(identifier: String): String =
            FireboltSqlEscapeUtils.quoteIdentifier(identifier)

        /** Airbyte meta columns and their Firebolt target types. */
        internal val META_COLUMNS: Map<String, ColumnType> =
            linkedMapOf(
                COLUMN_NAME_AB_RAW_ID to ColumnType(FireboltDataType.TEXT.typeName, false),
                COLUMN_NAME_AB_EXTRACTED_AT to ColumnType(FireboltDataType.TIMESTAMPTZ.typeName, false),
                COLUMN_NAME_AB_META to ColumnType(FireboltDataType.TEXT.typeName, false),
                COLUMN_NAME_AB_GENERATION_ID to ColumnType(FireboltDataType.BIGINT.typeName, false),
            )
    }

    /** Generates a CREATE SCHEMA statement. */
    fun createNamespace(namespace: String): String =
        "CREATE SCHEMA IF NOT EXISTS ${quoteIdentifier(namespace)}"

    /** Generates a query to check if a schema exists. */
    fun namespaceExists(namespace: String): String =
        """
            |SELECT EXISTS(
            |    SELECT 1 FROM information_schema.schemata
            |    WHERE schema_name = '${FireboltSqlEscapeUtils.escapeSqlString(namespace)}'
            |)
        """.trimMargin()

    /** Generates a query to check if a table exists. */
    fun tableExists(tableName: TableName): String =
        """
            |SELECT EXISTS(
            |    SELECT 1 FROM information_schema.tables
            |    WHERE table_schema = '${FireboltSqlEscapeUtils.escapeSqlString(tableName.namespace)}'
            |    AND table_name = '${FireboltSqlEscapeUtils.escapeSqlString(tableName.name)}'
            |)
        """.trimMargin()

    /** Generates a CREATE TABLE statement for a stream. */
    fun createTable(stream: DestinationStream, tableName: TableName): String {
        val metaColumns = META_COLUMNS
        val userColumns = getUserColumns(stream)

        val columnDeclarations =
            buildList {
                metaColumns.forEach { (columnName, columnType) ->
                    val nullability = if (columnType.nullable) "" else " NOT NULL"
                    add("    ${quoteIdentifier(columnName)} ${columnType.type}$nullability")
                }
                userColumns.forEach { (columnName, columnType) ->
                    val nullability = if (columnType.nullable) "" else " NOT NULL"
                    add("    ${quoteIdentifier(columnName)} ${columnType.type}$nullability")
                }
            }
            .joinToString(",\n")

        return """
            |CREATE TABLE IF NOT EXISTS ${getFullyQualifiedName(tableName)} (
            |$columnDeclarations
            |)
        """.trimMargin()
    }

    fun dropTable(tableName: TableName): String =
        "DROP TABLE IF EXISTS ${getFullyQualifiedName(tableName)}"

    fun addColumn(tableName: TableName, columnName: String, columnType: String): String =
        "ALTER TABLE ${getFullyQualifiedName(tableName)} ADD COLUMN ${quoteIdentifier(columnName)} $columnType"

    fun countTable(tableName: TableName): String =
        "SELECT COUNT(*) AS \"total\" FROM ${getFullyQualifiedName(tableName)}"

    fun isTableNotEmpty(tableName: TableName): String =
        "SELECT EXISTS(SELECT 1 FROM ${getFullyQualifiedName(tableName)} LIMIT 1) AS \"not_empty\""

    fun getGenerationId(tableName: TableName): String =
        """
            |SELECT ${quoteIdentifier(COLUMN_NAME_AB_GENERATION_ID)}
            |FROM ${getFullyQualifiedName(tableName)}
            |LIMIT 1
        """.trimMargin()

    /** Inserts all rows from the source table into the target table. */
    fun copyTable(sourceTableName: TableName, targetTableName: TableName): String =
        """
            |INSERT INTO ${getFullyQualifiedName(targetTableName)}
            |SELECT * FROM ${getFullyQualifiedName(sourceTableName)}
        """.trimMargin()

    /** Drops the target table and renames the source table to the target name. */
    fun overwriteTable(sourceTableName: TableName, targetTableName: TableName): String =
        """
            |DROP TABLE IF EXISTS ${getFullyQualifiedName(targetTableName)};
            |ALTER TABLE ${getFullyQualifiedName(sourceTableName)} RENAME TO ${quoteIdentifier(targetTableName.name)};
        """.trimMargin()

    /**
     * Generates a MERGE-based upsert from the source (temp) table into the target table.
     *
     * The source is first deduplicated by primary key, keeping the latest row by cursor then
     * extracted_at. CDC hard deletes are applied when _ab_cdc_deleted_at is present.
     */
    fun upsertTable(stream: DestinationStream, sourceTableName: TableName, targetTableName: TableName): String {
        val importType = stream.tableSchema.importType as Dedupe

        if (importType.primaryKey.isEmpty()) {
            throw IllegalArgumentException("Cannot perform upsert without primary key")
        }

        val primaryKeyColumns = getPrimaryKeysColumnNamesQuoted(stream)
        val cursorColumn = getCursorColumnNameQuoted(stream)
        val allColumns = getTargetColumnNamesForStream(stream)

        val cdcHardDeleteEnabled =
            stream.tableSchema.columnSchema.inputSchema.containsKey(CDC_DELETED_AT_COLUMN)

        val dedupedSource =
            """
                |SELECT ${allColumns.joinToString(", ")}
                |FROM (
                |    SELECT *,
                |        ROW_NUMBER() OVER (
                |            PARTITION BY ${primaryKeyColumns.joinToString(", ")}
                |            ORDER BY
                |                ${cursorColumn?.let { "$it DESC NULLS LAST," } ?: ""} $EXTRACTED_AT_COLUMN_NAME DESC
                |        ) AS _airbyte_row_num
                |    FROM ${getFullyQualifiedName(sourceTableName)}
                |) AS _airbyte_dedup
                |WHERE _airbyte_row_num = 1
            """.trimMargin()

        val onCondition = primaryKeyColumns.joinToString(" AND ") { pk ->
            "t.$pk = s.$pk"
        }

        val matchedClauses =
            buildList {
                if (cdcHardDeleteEnabled) {
                    add(
                        """
                            |WHEN MATCHED AND s.$DELETED_AT_COLUMN_NAME IS NOT NULL THEN DELETE
                        """.trimMargin()
                    )
                }
                val cursorComparison = cursorColumn?.let {
                    buildCursorComparison(it, "t", "s")
                } ?: "t.$EXTRACTED_AT_COLUMN_NAME < s.$EXTRACTED_AT_COLUMN_NAME"
                add(
                    """
                        |WHEN MATCHED AND ($cursorComparison) THEN
                        |    UPDATE SET *
                    """.trimMargin()
                )
            }
            .joinToString("\n")

        val notMatchedClause =
            if (cdcHardDeleteEnabled) {
                """
                    |WHEN NOT MATCHED AND s.$DELETED_AT_COLUMN_NAME IS NULL THEN
                    |    INSERT *
                """.trimMargin()
            } else {
                """
                    |WHEN NOT MATCHED THEN
                    |    INSERT *
                """.trimMargin()
            }

        return """
            |MERGE INTO ${getFullyQualifiedName(targetTableName)} AS t
            |USING (
            |$dedupedSource
            |) AS s
            |ON $onCondition
            |$matchedClauses
            |$notMatchedClause
        """.trimMargin()
    }

    /**
     * Generates a transaction to evolve the table schema.
     * For now this only adds missing columns; type coercions are left as a later TODO.
     */
    fun matchSchemas(
        tableName: TableName,
        columnsToAdd: Map<String, ColumnType>,
        columnsToModify: Map<String, ColumnTypeChange>,
    ): String {
        val addClauses =
            columnsToAdd.entries.joinToString(",\n") { (name, type) ->
                "    ADD COLUMN ${quoteIdentifier(name)} ${type.type}"
            }

        return if (addClauses.isNotEmpty()) {
            """
                |ALTER TABLE ${getFullyQualifiedName(tableName)}
                |$addClauses
            """.trimMargin()
        } else {
            "SELECT 1"
        }
    }

    /** Generates a COPY FROM statement to load a gzip CSV from S3. */
    fun copyFromS3(
        tableName: TableName,
        s3Path: String,
        accessKeyId: String,
        secretAccessKey: String,
    ): String =
        """
            |COPY INTO ${getFullyQualifiedName(tableName)}
            |FROM '${FireboltSqlEscapeUtils.escapeSqlString(s3Path)}'
            |WITH (
            |    TYPE = CSV,
            |    HEADER = TRUE
            |)
            |CREDENTIALS = (
            |    AWS_ACCESS_KEY_ID = '${FireboltSqlEscapeUtils.escapeSqlString(accessKeyId)}',
            |    AWS_SECRET_ACCESS_KEY = '${FireboltSqlEscapeUtils.escapeSqlString(secretAccessKey)}'
            |)
        """.trimMargin()

    /** Generates a query to retrieve column metadata from information_schema. */
    fun getTableSchema(tableName: TableName): String =
        """
            |SELECT column_name, data_type, is_nullable
            |FROM information_schema.columns
            |WHERE table_schema = '${FireboltSqlEscapeUtils.escapeSqlString(tableName.namespace)}'
            |    AND table_name = '${FireboltSqlEscapeUtils.escapeSqlString(tableName.name)}'
            |ORDER BY ordinal_position
        """.trimMargin()

    // ================================================================
    // Internal helpers
    // ================================================================

    private fun getUserColumns(stream: DestinationStream): Map<String, ColumnType> =
        stream.tableSchema.columnSchema.finalSchema

    private fun getFullyQualifiedName(tableName: TableName): String =
        "${quoteIdentifier(tableName.namespace)}.${quoteIdentifier(tableName.name)}"

    private fun getTargetColumnNamesForStream(stream: DestinationStream): List<String> {
        val meta = META_COLUMNS.keys.map { quoteIdentifier(it) }
        val user = getUserColumns(stream).keys.map { quoteIdentifier(it) }
        return meta + user
    }

    private fun getPrimaryKeysColumnNamesQuoted(stream: DestinationStream): List<String> =
        stream.tableSchema.getPrimaryKey().flatten().map { quoteIdentifier(it) }

    private fun getCursorColumnNameQuoted(stream: DestinationStream): String? =
        stream.tableSchema.getCursor().firstOrNull()?.let { quoteIdentifier(it) }

    private fun buildCursorComparison(cursorColumn: String, targetAlias: String, sourceAlias: String): String =
        """
            |$targetAlias.$cursorColumn < $sourceAlias.$cursorColumn
            |    OR ($targetAlias.$cursorColumn = $sourceAlias.$cursorColumn AND $targetAlias.$EXTRACTED_AT_COLUMN_NAME < $sourceAlias.$EXTRACTED_AT_COLUMN_NAME)
            |    OR ($targetAlias.$cursorColumn IS NULL AND $sourceAlias.$cursorColumn IS NOT NULL)
            |    OR ($targetAlias.$cursorColumn IS NULL AND $sourceAlias.$cursorColumn IS NULL AND $targetAlias.$EXTRACTED_AT_COLUMN_NAME < $sourceAlias.$EXTRACTED_AT_COLUMN_NAME)
        """.trimMargin()
}
