/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.sql

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import javax.sql.DataSource

internal const val COUNT_TOTAL_ALIAS = "total"
internal const val CSV_FIELD_DELIMITER = ","
internal const val CSV_RECORD_DELIMITER = "\n"
internal const val QUOTE: String = "\""
internal const val STAGE_FORMAT_NAME: String = "airbyte_csv_format"
internal const val STAGE_NAME_PREFIX = "airbyte_stage_"
internal val FILE_FORMAT_STATEMENT =
    """
            CREATE OR REPLACE FILE FORMAT $STAGE_FORMAT_NAME
            TYPE = 'CSV'
            FIELD_DELIMITER = '$CSV_FIELD_DELIMITER'
            FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            TRIM_SPACE = TRUE
            ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
            REPLACE_INVALID_CHARACTERS = TRUE
        """.trimIndent()

private val log = KotlinLogging.logger {}

@Singleton
class SnowflakeDirectLoadSqlGenerator(
    private val dataSource: DataSource,
    private val columnUtils: SnowflakeColumnUtils,
) {

    /**
     * This extension is here to avoid writing `.also { log.info { it }}` for every returned string
     * we want to log
     */
    private fun String.andLog(): String {
        log.info { this }
        return this
    }

    fun countTable(tableName: TableName): String {
        return "SELECT COUNT(*) AS \"$COUNT_TOTAL_ALIAS\" FROM ${tableName.toPrettyString(quote=QUOTE)}".andLog()
    }

    fun createNamespace(namespace: String): String {
        return "CREATE SCHEMA IF NOT EXISTS \"$namespace\"".andLog()
    }

    fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ): String {
        val columnDeclarations =
            columnUtils
                .columnsAndTypes(stream.schema.asColumns(), columnNameMapping)
                .joinToString(",\n")

        // Snowflake supports CREATE OR REPLACE TABLE, which is simpler than drop+recreate
        val createOrReplace = if (replace) "CREATE OR REPLACE" else "CREATE"

        val createTableStatement =
            """
            $createOrReplace TABLE ${tableName.toPrettyString(quote=QUOTE)} (
                $columnDeclarations
            )
        """.trimIndent()

        return createTableStatement.andLog()
    }

    fun showColumns(tableName: TableName): String =
        "SHOW COLUMNS IN TABLE ${tableName.toPrettyString(quote=QUOTE)};"

    fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        val columnNames =
            DEFAULT_COLUMNS.map { it.columnName }.joinToString(",") { "\"$it\"" } +
                columnNameMapping
                    .map { (_, actualName) -> actualName }
                    .joinToString(",") { "\"$it\"" }

        return """
            INSERT INTO ${targetTableName.toPrettyString(quote=QUOTE)}
            (
                $columnNames
            )
            SELECT
                $columnNames
            FROM ${sourceTableName.toPrettyString(quote=QUOTE)}
            """
            .trimIndent()
            .andLog()
    }

    fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        val importType = stream.importType as Dedupe

        // Build primary key matching condition
        val pkEquivalent =
            if (importType.primaryKey.isNotEmpty()) {
                importType.primaryKey.joinToString(" AND ") { fieldPath ->
                    val fieldName = fieldPath.first()
                    val columnName = columnNameMapping[fieldName] ?: fieldName
                    """(target_table."$columnName" = new_record."$columnName" OR (target_table."$columnName" IS NULL AND new_record."$columnName" IS NULL))"""
                }
            } else {
                // If no primary key, we can't perform a meaningful upsert
                throw IllegalArgumentException("Cannot perform upsert without primary key")
            }

        // Build column lists for INSERT and UPDATE
        val columnList: String =
            columnUtils
                .columnsAndTypes(
                    columns = stream.schema.asColumns(),
                    columnNameMapping = columnNameMapping
                )
                .map { it.columnName }
                .joinToString(",\n") { "\"$it\"" }

        val newRecordColumnList: String =
            columnUtils
                .columnsAndTypes(
                    columns = stream.schema.asColumns(),
                    columnNameMapping = columnNameMapping
                )
                .map { it.columnName }
                .joinToString(",\n") { "new_record.\"$it\"" }

        // Get deduped records from source
        val selectSourceRecords = selectDedupedRecords(stream, sourceTableName, columnNameMapping)

        // Build cursor comparison for determining which record is newer
        val cursorComparison: String
        if (importType.cursor.isNotEmpty()) {
            val cursorFieldName = importType.cursor.first()
            val cursorColumnName = columnNameMapping[cursorFieldName] ?: cursorFieldName
            val cursor = "\"$cursorColumnName\""
            cursorComparison =
                """
                (
                  target_table.$cursor < new_record.$cursor
                  OR (target_table.$cursor = new_record.$cursor AND target_table."$COLUMN_NAME_AB_EXTRACTED_AT" < new_record."$COLUMN_NAME_AB_EXTRACTED_AT")
                  OR (target_table.$cursor IS NULL AND new_record.$cursor IS NULL AND target_table."$COLUMN_NAME_AB_EXTRACTED_AT" < new_record."$COLUMN_NAME_AB_EXTRACTED_AT")
                  OR (target_table.$cursor IS NULL AND new_record.$cursor IS NOT NULL)
                )
            """.trimIndent()
        } else {
            // No cursor - use extraction timestamp only
            cursorComparison =
                """target_table."$COLUMN_NAME_AB_EXTRACTED_AT" < new_record."$COLUMN_NAME_AB_EXTRACTED_AT""""
        }

        // Build column assignments for UPDATE
        val columnAssignments: String =
            stream.schema.asColumns().keys.joinToString(",\n") { fieldName ->
                val column = columnNameMapping[fieldName] ?: fieldName
                "\"$column\" = new_record.\"$column\""
            }

        // Build the MERGE statement
        val mergeStatement =
            """
            MERGE INTO ${targetTableName.toPrettyString(QUOTE)} AS target_table
            USING (
              $selectSourceRecords
            ) AS new_record
            ON $pkEquivalent
            WHEN MATCHED AND $cursorComparison THEN UPDATE SET
              $columnAssignments
            WHEN NOT MATCHED THEN INSERT (
              $columnList
            ) VALUES (
              $newRecordColumnList
            )
        """.trimIndent()

        return mergeStatement.andLog()
    }

    /**
     * Generates a SQL SELECT statement that extracts and deduplicates records from the source
     * table. Uses ROW_NUMBER() window function to select the most recent record per primary key.
     */
    private fun selectDedupedRecords(
        stream: DestinationStream,
        sourceTableName: TableName,
        columnNameMapping: ColumnNameMapping
    ): String {
        val columnList: String =
            stream.schema.asColumns().keys.joinToString(",\n") { fieldName ->
                val columnName = columnNameMapping[fieldName] ?: fieldName
                "\"$columnName\""
            }

        val importType = stream.importType as Dedupe

        // Build the primary key list for partitioning
        val pkList =
            if (importType.primaryKey.isNotEmpty()) {
                importType.primaryKey.joinToString(",") { fieldPath ->
                    val columnName = columnNameMapping[fieldPath.first()] ?: fieldPath.first()
                    "\"$columnName\""
                }
            } else {
                // Should not happen as we check this earlier, but handle it defensively
                throw IllegalArgumentException("Cannot deduplicate without primary key")
            }

        // Build cursor order clause for sorting within each partition
        val cursorOrderClause =
            if (importType.cursor.isNotEmpty()) {
                val columnName =
                    columnNameMapping[importType.cursor.first()] ?: importType.cursor.first()
                "\"$columnName\" DESC NULLS LAST,"
            } else {
                ""
            }

        return """
            WITH records AS (
              SELECT
                $columnList
              FROM ${sourceTableName.toPrettyString(QUOTE)}
            ), numbered_rows AS (
              SELECT *, ROW_NUMBER() OVER (
                PARTITION BY $pkList ORDER BY $cursorOrderClause "$COLUMN_NAME_AB_EXTRACTED_AT" DESC
              ) AS row_number
              FROM records
            )
            SELECT $columnList
            FROM numbered_rows
            WHERE row_number = 1
        """
            .trimIndent()
            .andLog()
    }

    fun dropTable(tableName: TableName): String {
        return "DROP TABLE IF EXISTS ${tableName.toPrettyString(QUOTE)}".andLog()
    }

    fun dropStage(tableName: TableName): String {
        return "DROP STAGE IF EXISTS ${buildSnowflakeStageName(tableName)}".andLog()
    }

    fun getGenerationId(
        tableName: TableName,
        alias: String = "",
    ): String {
        val aliasClause = if (alias.isNotEmpty()) " AS $alias" else ""
        return """
            SELECT "$COLUMN_NAME_AB_GENERATION_ID"$aliasClause 
            FROM ${tableName.toPrettyString(QUOTE)} 
            LIMIT 1
        """
            .trimIndent()
            .andLog()
    }

    fun createFileFormat(): String = FILE_FORMAT_STATEMENT.andLog()

    private fun buildSnowflakeStageName(tableName: TableName): String {
        return "$STAGE_NAME_PREFIX${tableName.name}"
    }

    fun createSnowflakeStage(tableName: TableName): String {
        val stageName = buildSnowflakeStageName(tableName)
        return """
            CREATE OR REPLACE STAGE $stageName
                FILE_FORMAT = $STAGE_FORMAT_NAME;
        """
            .trimIndent()
            .andLog()
    }

    fun putInStage(tableName: TableName, tempFilePath: String): String {
        val stageName = buildSnowflakeStageName(tableName)
        return """
            PUT 'file://$tempFilePath' @$stageName
            AUTO_COMPRESS = TRUE
            OVERWRITE = TRUE
        """
            .trimIndent()
            .andLog()
    }

    fun copyFromStage(tableName: TableName): String {
        val stageName = buildSnowflakeStageName(tableName)

        return """
            COPY INTO ${tableName.toPrettyString(quote=QUOTE)}
            FROM @$stageName
            FILE_FORMAT = $STAGE_FORMAT_NAME
            ON_ERROR = 'ABORT_STATEMENT'
        """
            .trimIndent()
            .andLog()
    }
}
