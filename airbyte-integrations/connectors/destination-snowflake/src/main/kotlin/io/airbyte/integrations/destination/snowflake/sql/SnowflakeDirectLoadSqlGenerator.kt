/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.sql

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.cdk.load.util.UUIDGenerator
import io.airbyte.integrations.destination.snowflake.db.ColumnDefinition
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.CdcDeletionMode
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.write.load.CSV_FIELD_SEPARATOR
import io.airbyte.integrations.destination.snowflake.write.load.CSV_LINE_DELIMITER
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

internal const val COUNT_TOTAL_ALIAS = "TOTAL"

private val log = KotlinLogging.logger {}

/**
 * This extension is here to avoid writing `.also { log.info { it }}` for every returned string we
 * want to log
 */
fun String.andLog(): String {
    log.info { this.trim() }
    return this
}

@Singleton
class SnowflakeDirectLoadSqlGenerator(
    private val columnUtils: SnowflakeColumnUtils,
    private val uuidGenerator: UUIDGenerator,
    private val snowflakeConfiguration: SnowflakeConfiguration,
    private val snowflakeSqlNameUtils: SnowflakeSqlNameUtils,
) {
    fun countTable(tableName: TableName): String {
        return "SELECT COUNT(*) AS $COUNT_TOTAL_ALIAS FROM ${snowflakeSqlNameUtils.fullyQualifiedName(tableName)}".andLog()
    }

    fun createNamespace(namespace: String): String {
        return "CREATE SCHEMA IF NOT EXISTS ${snowflakeSqlNameUtils.fullyQualifiedNamespace(namespace)}".andLog()
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
            $createOrReplace TABLE ${snowflakeSqlNameUtils.fullyQualifiedName(tableName)} (
                $columnDeclarations
            )
        """.trimIndent()

        return createTableStatement.andLog()
    }

    fun showColumns(tableName: TableName): String =
        "SHOW COLUMNS IN TABLE ${snowflakeSqlNameUtils.fullyQualifiedName(tableName)}".andLog()

    fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        val columnNames = columnUtils.getColumnNames(columnNameMapping)

        return """
            INSERT INTO ${snowflakeSqlNameUtils.fullyQualifiedName(targetTableName)} 
            (
                $columnNames
            )
            SELECT
                $columnNames
            FROM ${snowflakeSqlNameUtils.fullyQualifiedName(sourceTableName)}
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
                    val targetTableColumnName = "target_table.${columnName.quote()}"
                    val newRecordColumnName = "new_record.${columnName.quote()}"
                    """($targetTableColumnName = $newRecordColumnName OR ($targetTableColumnName IS NULL AND $newRecordColumnName IS NULL))"""
                }
            } else {
                // If no primary key, we can't perform a meaningful upsert
                throw IllegalArgumentException("Cannot perform upsert without primary key")
            }

        // Build column lists for INSERT and UPDATE
        val columnList: String =
            columnUtils
                .getFormattedColumnNames(
                    columns = stream.schema.asColumns(),
                    columnNameMapping = columnNameMapping,
                    quote = false,
                )
                .joinToString(
                    ",\n",
                ) {
                    it.quote()
                }

        val newRecordColumnList: String =
            columnUtils
                .getFormattedColumnNames(
                    columns = stream.schema.asColumns(),
                    columnNameMapping = columnNameMapping,
                    quote = false,
                )
                .joinToString(",\n") { "new_record.${it.quote()}" }

        // Get deduped records from source
        val selectSourceRecords = selectDedupedRecords(stream, sourceTableName, columnNameMapping)

        // Build cursor comparison for determining which record is newer
        val cursorComparison: String
        if (importType.cursor.isNotEmpty()) {
            val cursorFieldName = importType.cursor.first()
            val cursor = (columnNameMapping[cursorFieldName] ?: cursorFieldName)
            val targetTableCursor = "target_table.${cursor.quote()}"
            val newRecordCursor = "new_record.${cursor.quote()}"
            cursorComparison =
                """
                (
                  $targetTableCursor < $newRecordCursor
                  OR ($targetTableCursor = $newRecordCursor AND target_table."${COLUMN_NAME_AB_EXTRACTED_AT.toSnowflakeCompatibleName()}" < new_record."${COLUMN_NAME_AB_EXTRACTED_AT.toSnowflakeCompatibleName()}")
                  OR ($targetTableCursor IS NULL AND $newRecordCursor IS NULL AND target_table."${COLUMN_NAME_AB_EXTRACTED_AT.toSnowflakeCompatibleName()}" < new_record."${COLUMN_NAME_AB_EXTRACTED_AT.toSnowflakeCompatibleName()}")
                  OR ($targetTableCursor IS NULL AND $newRecordCursor IS $NOT_NULL)
                )
            """.trimIndent()
        } else {
            // No cursor - use extraction timestamp only
            cursorComparison =
                """target_table."${COLUMN_NAME_AB_EXTRACTED_AT.toSnowflakeCompatibleName()}" < new_record."${COLUMN_NAME_AB_EXTRACTED_AT.toSnowflakeCompatibleName()}""""
        }

        // Build column assignments for UPDATE
        val columnAssignments: String =
            columnUtils
                .getFormattedColumnNames(
                    columns = stream.schema.asColumns(),
                    columnNameMapping = columnNameMapping,
                    quote = false,
                )
                .joinToString(",\n") { column ->
                    "${column.quote()} = new_record.${column.quote()}"
                }

        // Handle CDC deletions based on mode
        val cdcDeleteClause: String
        val cdcSkipInsertClause: String
        if (
            stream.schema.asColumns().containsKey(CDC_DELETED_AT_COLUMN) &&
                snowflakeConfiguration.cdcDeletionMode == CdcDeletionMode.HARD_DELETE
        ) {
            // Execute CDC deletions if there's already a record
            cdcDeleteClause =
                "WHEN MATCHED AND new_record.\"${CDC_DELETED_AT_COLUMN.toSnowflakeCompatibleName()}\" IS NOT NULL AND $cursorComparison THEN DELETE"
            // And skip insertion entirely if there's no matching record.
            // (This is possible if a single T+D batch contains both an insertion and deletion for
            // the same PK)
            cdcSkipInsertClause =
                "AND new_record.\"${CDC_DELETED_AT_COLUMN.toSnowflakeCompatibleName()}\" IS NULL"
        } else {
            cdcDeleteClause = ""
            cdcSkipInsertClause = ""
        }

        // Build the MERGE statement
        val mergeStatement =
            if (cdcDeleteClause.isNotEmpty()) {
                """
            MERGE INTO ${snowflakeSqlNameUtils.fullyQualifiedName(targetTableName)} AS target_table
            USING (
              $selectSourceRecords
            ) AS new_record
            ON $pkEquivalent
            $cdcDeleteClause
            WHEN MATCHED AND $cursorComparison THEN UPDATE SET
              $columnAssignments
            WHEN NOT MATCHED $cdcSkipInsertClause THEN INSERT (
              $columnList
            ) VALUES (
              $newRecordColumnList
            )
        """.trimIndent()
            } else {
                """
            MERGE INTO ${snowflakeSqlNameUtils.fullyQualifiedName(targetTableName)} AS target_table
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
            }

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
            columnUtils
                .getFormattedColumnNames(
                    columns = stream.schema.asColumns(),
                    columnNameMapping = columnNameMapping,
                    quote = false,
                )
                .joinToString(
                    ",\n",
                ) {
                    it.quote()
                }
        val importType = stream.importType as Dedupe

        // Build the primary key list for partitioning
        val pkList =
            if (importType.primaryKey.isNotEmpty()) {
                importType.primaryKey.joinToString(",") { fieldPath ->
                    (columnNameMapping[fieldPath.first()] ?: fieldPath.first()).quote()
                }
            } else {
                // Should not happen as we check this earlier, but handle it defensively
                throw IllegalArgumentException("Cannot deduplicate without primary key")
            }

        // Build cursor order clause for sorting within each partition
        val cursorOrderClause =
            if (importType.cursor.isNotEmpty()) {
                val columnName =
                    (columnNameMapping[importType.cursor.first()] ?: importType.cursor.first())
                        .quote()
                "$columnName DESC NULLS LAST,"
            } else {
                ""
            }

        return """
            WITH records AS (
              SELECT
                $columnList
              FROM ${snowflakeSqlNameUtils.fullyQualifiedName(sourceTableName)}
            ), numbered_rows AS (
              SELECT *, ROW_NUMBER() OVER (
                PARTITION BY $pkList ORDER BY $cursorOrderClause "${COLUMN_NAME_AB_EXTRACTED_AT.toSnowflakeCompatibleName()}" DESC
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
        return "DROP TABLE IF EXISTS ${snowflakeSqlNameUtils.fullyQualifiedName(tableName)}".andLog()
    }

    fun getGenerationId(
        tableName: TableName,
    ): String {
        return """
            SELECT "${columnUtils.getGenerationIdColumnName()}"
            FROM ${snowflakeSqlNameUtils.fullyQualifiedName(tableName)}
            LIMIT 1
        """
            .trimIndent()
            .andLog()
    }

    fun createSnowflakeStage(tableName: TableName): String {
        val stageName = snowflakeSqlNameUtils.fullyQualifiedStageName(tableName)
        return "CREATE STAGE IF NOT EXISTS $stageName".andLog()
    }

    fun putInStage(tableName: TableName, tempFilePath: String): String {
        val stageName = snowflakeSqlNameUtils.fullyQualifiedStageName(tableName, true)
        return """
            PUT 'file://$tempFilePath' '@$stageName'
            AUTO_COMPRESS = FALSE
            SOURCE_COMPRESSION = GZIP
            OVERWRITE = TRUE
        """
            .trimIndent()
            .andLog()
    }

    fun copyFromStage(tableName: TableName, filename: String): String {
        val stageName = snowflakeSqlNameUtils.fullyQualifiedStageName(tableName, true)

        return """
            COPY INTO ${snowflakeSqlNameUtils.fullyQualifiedName(tableName)}
            FROM '@$stageName'
            FILE_FORMAT = (
                TYPE = 'CSV'
                COMPRESSION = GZIP
                FIELD_DELIMITER = '$CSV_FIELD_SEPARATOR'
                RECORD_DELIMITER = '$CSV_LINE_DELIMITER'
                FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                TRIM_SPACE = TRUE
                ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
                REPLACE_INVALID_CHARACTERS = TRUE
                ESCAPE = NONE
                ESCAPE_UNENCLOSED_FIELD = NONE
            )
            ON_ERROR = 'ABORT_STATEMENT'
            PURGE = TRUE
            files = ('$filename')
        """
            .trimIndent()
            .andLog()
    }

    fun swapTableWith(sourceTableName: TableName, targetTableName: TableName): String {
        return """
            ALTER TABLE ${snowflakeSqlNameUtils.fullyQualifiedName(sourceTableName)} SWAP WITH ${snowflakeSqlNameUtils.fullyQualifiedName(targetTableName)}
        """
            .trimIndent()
            .andLog()
    }

    fun renameTable(sourceTableName: TableName, targetTableName: TableName): String {
        // Snowflake RENAME TO only accepts the table name, not a fully qualified name
        // The renamed table stays in the same schema
        return """
            ALTER TABLE ${snowflakeSqlNameUtils.fullyQualifiedName(sourceTableName)} RENAME TO ${snowflakeSqlNameUtils.fullyQualifiedName(targetTableName)}
        """
            .trimIndent()
            .andLog()
    }

    fun describeTable(
        schemaName: String,
        tableName: String,
    ): String =
        """DESCRIBE TABLE ${snowflakeSqlNameUtils.fullyQualifiedName(TableName(schemaName, tableName))}""".andLog()

    fun alterTable(
        tableName: TableName,
        addedColumns: Set<ColumnDefinition>,
        deletedColumns: Set<ColumnDefinition>,
        modifiedColumns: Set<ColumnDefinition>,
    ): Set<String> {
        val clauses = mutableSetOf<String>()
        val prettyTableName = snowflakeSqlNameUtils.fullyQualifiedName(tableName)
        addedColumns.forEach {
            clauses.add(
                "ALTER TABLE $prettyTableName ADD COLUMN ${it.name.quote()} ${it.type};".andLog()
            )
        }
        deletedColumns.forEach {
            clauses.add("ALTER TABLE $prettyTableName DROP COLUMN ${it.name.quote()};".andLog())
        }
        modifiedColumns.forEach {
            val tempColumn = "${it.name}_${uuidGenerator.v4()}"
            clauses.add(
                "ALTER TABLE $prettyTableName ADD COLUMN ${tempColumn.quote()} ${it.type};".andLog()
            )
            clauses.add(
                "UPDATE $prettyTableName SET ${tempColumn.quote()} = CAST(${it.name.quote()} AS ${it.type});".andLog()
            )
            val backupColumn = "${tempColumn}_backup"
            clauses.add(
                """ALTER TABLE $prettyTableName
                RENAME COLUMN "${it.name}" TO "$backupColumn";
            """.trimIndent()
            )
            clauses.add(
                """ALTER TABLE $prettyTableName
                RENAME COLUMN "$tempColumn" TO "${it.name}";
            """.trimIndent()
            )
            clauses.add(
                "ALTER TABLE $prettyTableName DROP COLUMN ${backupColumn.quote()};".andLog()
            )
        }
        return clauses
    }
}
