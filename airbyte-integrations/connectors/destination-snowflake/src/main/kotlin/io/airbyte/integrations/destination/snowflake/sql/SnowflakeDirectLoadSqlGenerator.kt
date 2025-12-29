/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.sql

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.util.UUIDGenerator
import io.airbyte.integrations.destination.snowflake.schema.SnowflakeColumnManager
import io.airbyte.integrations.destination.snowflake.schema.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.CdcDeletionMode
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.write.load.CSV_FIELD_SEPARATOR
import io.airbyte.integrations.destination.snowflake.write.load.CSV_LINE_DELIMITER
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

internal const val COUNT_TOTAL_ALIAS = "TOTAL"
internal const val NOT_NULL = "NOT NULL"

// Snowflake-compatible (uppercase) versions of the Airbyte meta column names
internal val SNOWFLAKE_AB_RAW_ID = COLUMN_NAME_AB_RAW_ID.toSnowflakeCompatibleName()
internal val SNOWFLAKE_AB_EXTRACTED_AT = COLUMN_NAME_AB_EXTRACTED_AT.toSnowflakeCompatibleName()
internal val SNOWFLAKE_AB_META = COLUMN_NAME_AB_META.toSnowflakeCompatibleName()
internal val SNOWFLAKE_AB_GENERATION_ID = COLUMN_NAME_AB_GENERATION_ID.toSnowflakeCompatibleName()
internal val SNOWFLAKE_AB_CDC_DELETED_AT_COLUMN = CDC_DELETED_AT_COLUMN.toSnowflakeCompatibleName()

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
    private val uuidGenerator: UUIDGenerator,
    private val config: SnowflakeConfiguration,
    private val columnManager: SnowflakeColumnManager,
) {
    fun countTable(tableName: TableName): String {
        return "SELECT COUNT(*) AS $COUNT_TOTAL_ALIAS FROM ${fullyQualifiedName(tableName)}".andLog()
    }

    fun createNamespace(namespace: String): String {
        return "CREATE SCHEMA IF NOT EXISTS ${fullyQualifiedNamespace(namespace)}".andLog()
    }

    fun createTable(
        tableName: TableName,
        tableSchema: StreamTableSchema,
        replace: Boolean
    ): String {
        val finalSchema = tableSchema.columnSchema.finalSchema
        val metaColumns = columnManager.getMetaColumns()

        // Build column declarations from the meta columns and user schema
        val columnDeclarations =
            buildList {
                    // Add Airbyte meta columns from the column manager
                    metaColumns.forEach { (columnName, columnType) ->
                        val nullability = if (columnType.nullable) "" else " NOT NULL"
                        add("${columnName.quote()} ${columnType.type}$nullability")
                    }

                    // Add user columns from the munged schema
                    finalSchema.forEach { (columnName, columnType) ->
                        val nullability = if (columnType.nullable) "" else " NOT NULL"
                        add("${columnName.quote()} ${columnType.type}$nullability")
                    }
                }
                .joinToString(",\n    ")

        // Snowflake supports CREATE OR REPLACE TABLE, which is simpler than drop+recreate
        val createOrReplace = if (replace) "CREATE OR REPLACE" else "CREATE"

        val createTableStatement =
            """
            |$createOrReplace TABLE ${fullyQualifiedName(tableName)} (
            |    $columnDeclarations
            |)
            """.trimMargin() // Something was tripping up trimIndent so we opt for trimMargin

        return createTableStatement.andLog()
    }

    fun showColumns(tableName: TableName): String =
        "SHOW COLUMNS IN TABLE ${fullyQualifiedName(tableName)}".andLog()

    fun copyTable(
        columnNames: Set<String>,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        val columnList = columnNames.joinToString(", ") { it.quote() }

        return """
            INSERT INTO ${fullyQualifiedName(targetTableName)} 
            (
                $columnList
            )
            SELECT
                $columnList
            FROM ${fullyQualifiedName(sourceTableName)}
            """
            .trimIndent()
            .andLog()
    }

    fun upsertTable(
        tableSchema: StreamTableSchema,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        val finalSchema = tableSchema.columnSchema.finalSchema

        // Build primary key matching condition
        val pks = tableSchema.getPrimaryKey().flatten()
        val pkEquivalent =
            if (pks.isNotEmpty()) {
                pks.joinToString(" AND ") { columnName ->
                    val targetTableColumnName = "target_table.${columnName.quote()}"
                    val newRecordColumnName = "new_record.${columnName.quote()}"
                    """($targetTableColumnName = $newRecordColumnName OR ($targetTableColumnName IS NULL AND $newRecordColumnName IS NULL))"""
                }
            } else {
                // If no primary key, we can't perform a meaningful upsert
                throw IllegalArgumentException("Cannot perform upsert without primary key")
            }

        // Build column lists for INSERT and UPDATE
        val allColumns = buildList {
            add(SNOWFLAKE_AB_RAW_ID)
            add(SNOWFLAKE_AB_EXTRACTED_AT)
            add(SNOWFLAKE_AB_META)
            add(SNOWFLAKE_AB_GENERATION_ID)
            addAll(finalSchema.keys)
        }

        val columnList: String = allColumns.joinToString(",\n  ") { it.quote() }
        val newRecordColumnList: String =
            allColumns.joinToString(",\n  ") { "new_record.${it.quote()}" }

        // Get deduped records from source
        val selectSourceRecords = selectDedupedRecords(tableSchema, sourceTableName)

        // Build cursor comparison for determining which record is newer
        val cursorComparison: String
        val cursor = tableSchema.getCursor().firstOrNull()
        if (cursor != null) {
            val targetTableCursor = "target_table.${cursor.quote()}"
            val newRecordCursor = "new_record.${cursor.quote()}"
            cursorComparison =
                """
                (
                  $targetTableCursor < $newRecordCursor
                  OR ($targetTableCursor = $newRecordCursor AND target_table."$SNOWFLAKE_AB_EXTRACTED_AT" < new_record."$SNOWFLAKE_AB_EXTRACTED_AT")
                  OR ($targetTableCursor IS NULL AND $newRecordCursor IS NULL AND target_table."$SNOWFLAKE_AB_EXTRACTED_AT" < new_record."$SNOWFLAKE_AB_EXTRACTED_AT")
                  OR ($targetTableCursor IS NULL AND $newRecordCursor IS $NOT_NULL)
                )
            """.trimIndent()
        } else {
            // No cursor - use extraction timestamp only
            cursorComparison =
                """target_table."$SNOWFLAKE_AB_EXTRACTED_AT" < new_record."$SNOWFLAKE_AB_EXTRACTED_AT""""
        }

        // Build column assignments for UPDATE
        val columnAssignments: String =
            allColumns.joinToString(",\n  ") { column ->
                "${column.quote()} = new_record.${column.quote()}"
            }

        // Handle CDC deletions based on mode
        val cdcDeleteClause: String
        val cdcSkipInsertClause: String
        if (
            finalSchema.containsKey(SNOWFLAKE_AB_CDC_DELETED_AT_COLUMN) &&
                config.cdcDeletionMode == CdcDeletionMode.HARD_DELETE
        ) {
            // Execute CDC deletions if there's already a record
            cdcDeleteClause =
                "WHEN MATCHED AND new_record.\"${SNOWFLAKE_AB_CDC_DELETED_AT_COLUMN}\" IS NOT NULL AND $cursorComparison THEN DELETE"
            // And skip insertion entirely if there's no matching record.
            // (This is possible if a single T+D batch contains both an insertion and deletion for
            // the same PK)
            cdcSkipInsertClause = "AND new_record.\"${SNOWFLAKE_AB_CDC_DELETED_AT_COLUMN}\" IS NULL"
        } else {
            cdcDeleteClause = ""
            cdcSkipInsertClause = ""
        }

        // Build the MERGE statement
        val mergeStatement =
            if (cdcDeleteClause.isNotEmpty()) {
                """
            |MERGE INTO ${fullyQualifiedName(targetTableName)} AS target_table
            |USING (
            |$selectSourceRecords
            |) AS new_record
            |ON $pkEquivalent
            |$cdcDeleteClause
            |WHEN MATCHED AND $cursorComparison THEN UPDATE SET
            |  $columnAssignments
            |WHEN NOT MATCHED $cdcSkipInsertClause THEN INSERT (
            |  $columnList
            |) VALUES (
            |  $newRecordColumnList
            |)
        """.trimMargin()
            } else {
                """
            |MERGE INTO ${fullyQualifiedName(targetTableName)} AS target_table
            |USING (
            |$selectSourceRecords
            |) AS new_record
            |ON $pkEquivalent
            |WHEN MATCHED AND $cursorComparison THEN UPDATE SET
            |  $columnAssignments
            |WHEN NOT MATCHED THEN INSERT (
            |  $columnList
            |) VALUES (
            |  $newRecordColumnList
            |)
        """.trimMargin()
            }

        return mergeStatement.andLog()
    }

    /**
     * Generates a SQL SELECT statement that extracts and deduplicates records from the source
     * table. Uses ROW_NUMBER() window function to select the most recent record per primary key.
     */
    private fun selectDedupedRecords(
        tableSchema: StreamTableSchema,
        sourceTableName: TableName
    ): String {
        val allColumns = buildList {
            add(SNOWFLAKE_AB_RAW_ID)
            add(SNOWFLAKE_AB_EXTRACTED_AT)
            add(SNOWFLAKE_AB_META)
            add(SNOWFLAKE_AB_GENERATION_ID)
            addAll(tableSchema.columnSchema.finalSchema.keys)
        }
        val columnList: String = allColumns.joinToString(",\n      ") { it.quote() }

        // Build the primary key list for partitioning
        val pks = tableSchema.getPrimaryKey().flatten()
        val pkList =
            if (pks.isNotEmpty()) {
                pks.joinToString(",") { it.quote() }
            } else {
                // Should not happen as we check this earlier, but handle it defensively
                throw IllegalArgumentException("Cannot deduplicate without primary key")
            }

        // Build cursor order clause for sorting within each partition
        val cursor = tableSchema.getCursor().firstOrNull()
        val cursorOrderClause =
            if (cursor != null) {
                "${cursor.quote()} DESC NULLS LAST,"
            } else {
                ""
            }

        return """
            |  WITH records AS (
            |    SELECT
            |      $columnList
            |    FROM ${fullyQualifiedName(sourceTableName)}
            |  ), numbered_rows AS (
            |    SELECT *, ROW_NUMBER() OVER (
            |      PARTITION BY $pkList ORDER BY $cursorOrderClause "$SNOWFLAKE_AB_EXTRACTED_AT" DESC
            |    ) AS row_number
            |    FROM records
            |  )
            |  SELECT $columnList
            |  FROM numbered_rows
            |  WHERE row_number = 1
        """
            .trimMargin()
            .andLog()
    }

    fun dropTable(tableName: TableName): String {
        return "DROP TABLE IF EXISTS ${fullyQualifiedName(tableName)}".andLog()
    }

    fun getGenerationId(
        tableName: TableName,
    ): String {
        return """
            SELECT "${columnManager.getGenerationIdColumnName()}"
            FROM ${fullyQualifiedName(tableName)}
            LIMIT 1
        """
            .trimIndent()
            .andLog()
    }

    fun createSnowflakeStage(tableName: TableName): String {
        val stageName = fullyQualifiedStageName(tableName)
        return "CREATE STAGE IF NOT EXISTS $stageName".andLog()
    }

    fun putInStage(tableName: TableName, tempFilePath: String): String {
        val stageName = fullyQualifiedStageName(tableName, true)
        return """
            PUT 'file://$tempFilePath' '@$stageName'
            AUTO_COMPRESS = FALSE
            SOURCE_COMPRESSION = GZIP
            OVERWRITE = TRUE
        """
            .trimIndent()
            .andLog()
    }

    fun copyFromStage(
        tableName: TableName,
        filename: String,
        columnNames: List<String>? = null
    ): String {
        val stageName = fullyQualifiedStageName(tableName, true)
        val columnList =
            columnNames?.let { names -> "(${names.joinToString(", ") { it.quote() }})" } ?: ""

        return """
            |COPY INTO ${fullyQualifiedName(tableName)}$columnList
            |FROM '@$stageName'
            |FILE_FORMAT = (
            |    TYPE = 'CSV'
            |    COMPRESSION = GZIP
            |    FIELD_DELIMITER = '$CSV_FIELD_SEPARATOR'
            |    RECORD_DELIMITER = '$CSV_LINE_DELIMITER'
            |    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            |    TRIM_SPACE = TRUE
            |    ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
            |    REPLACE_INVALID_CHARACTERS = TRUE
            |    ESCAPE = NONE
            |    ESCAPE_UNENCLOSED_FIELD = NONE
            |)
            |ON_ERROR = 'ABORT_STATEMENT'
            |PURGE = TRUE
            |files = ('$filename')
        """
            .trimMargin()
            .andLog()
    }

    fun swapTableWith(sourceTableName: TableName, targetTableName: TableName): String {
        return """
            ALTER TABLE ${fullyQualifiedName(sourceTableName)} SWAP WITH ${
            fullyQualifiedName(
                targetTableName,
            )
        }
        """
            .trimIndent()
            .andLog()
    }

    fun renameTable(sourceTableName: TableName, targetTableName: TableName): String {
        // Snowflake RENAME TO only accepts the table name, not a fully qualified name
        // The renamed table stays in the same schema
        return """
            ALTER TABLE ${fullyQualifiedName(sourceTableName)} RENAME TO ${
            fullyQualifiedName(
                targetTableName,
            )
        }
        """
            .trimIndent()
            .andLog()
    }

    fun describeTable(
        schemaName: String,
        tableName: String,
    ): String =
        """DESCRIBE TABLE ${fullyQualifiedName(TableName(schemaName, tableName))}""".andLog()

    fun alterTable(
        tableName: TableName,
        addedColumns: Map<String, ColumnType>,
        deletedColumns: Map<String, ColumnType>,
        modifiedColumns: Map<String, ColumnTypeChange>,
    ): Set<String> {
        val clauses = mutableSetOf<String>()
        val prettyTableName = fullyQualifiedName(tableName)
        addedColumns.forEach { (name, columnType) ->
            clauses.add(
                // Note that we intentionally don't set NOT NULL.
                // We're adding a new column, and we don't know what constitutes a reasonable
                // default value for preexisting records.
                // So we add the column as nullable.
                "ALTER TABLE $prettyTableName ADD COLUMN ${name.quote()} ${columnType.type};".andLog(),
            )
        }
        deletedColumns.forEach {
            clauses.add("ALTER TABLE $prettyTableName DROP COLUMN ${it.key.quote()};".andLog())
        }
        modifiedColumns.forEach { (name, typeChange) ->
            if (typeChange.originalType.type != typeChange.newType.type) {
                // If we're changing the actual column type, then we need to add a temp column,
                // cast the original column to that column, drop the original column,
                // and rename the temp column.
                val tempColumn = "${name}_${uuidGenerator.v4()}"
                clauses.add(
                    // As above: we add the column as nullable.
                    "ALTER TABLE $prettyTableName ADD COLUMN ${tempColumn.quote()} ${typeChange.newType.type};".andLog(),
                )
                clauses.add(
                    "UPDATE $prettyTableName SET ${tempColumn.quote()} = CAST(${name.quote()} AS ${typeChange.newType.type});".andLog(),
                )
                val backupColumn = "${tempColumn}_backup"
                clauses.add(
                    """
                    ALTER TABLE $prettyTableName
                    RENAME COLUMN "$name" TO "$backupColumn";
                    """.trimIndent(),
                )
                clauses.add(
                    """
                    ALTER TABLE $prettyTableName
                    RENAME COLUMN "$tempColumn" TO "$name";
                    """.trimIndent(),
                )
                clauses.add(
                    "ALTER TABLE $prettyTableName DROP COLUMN ${backupColumn.quote()};".andLog(),
                )
            } else if (!typeChange.originalType.nullable && typeChange.newType.nullable) {
                // If the type is unchanged, we can change a column from NOT NULL to nullable.
                // But we'll never do the reverse, because there's a decent chance that historical
                // records had null values.
                // Users can always manually ALTER COLUMN ... SET NOT NULL if they want.
                clauses.add(
                    """ALTER TABLE $prettyTableName ALTER COLUMN "$name" DROP NOT NULL;""".andLog(),
                )
            } else {
                log.info {
                    "Table ${tableName.toPrettyString()} column $name wants to change from nullable to non-nullable; ignoring this change."
                }
            }
        }
        return clauses
    }

    @VisibleForTesting
    fun fullyQualifiedName(tableName: TableName): String =
        combineParts(listOf(getDatabaseName(), tableName.namespace, tableName.name))

    @VisibleForTesting
    fun fullyQualifiedNamespace(namespace: String) =
        combineParts(listOf(getDatabaseName(), namespace))

    @VisibleForTesting
    fun fullyQualifiedStageName(tableName: TableName, escape: Boolean = false): String {
        val currentTableName =
            if (escape) {
                tableName.name
            } else {
                tableName.name
            }
        return combineParts(
            parts =
                listOf(
                    getDatabaseName(),
                    tableName.namespace,
                    "$STAGE_NAME_PREFIX$currentTableName",
                ),
            escape = escape,
        )
    }

    @VisibleForTesting
    internal fun combineParts(parts: List<String>, escape: Boolean = false): String =
        parts
            .map { if (escape) sqlEscape(it) else it }
            .joinToString(separator = ".") {
                if (!it.startsWith(QUOTE)) {
                    "$QUOTE$it$QUOTE"
                } else {
                    it
                }
            }

    private fun getDatabaseName() = config.database.toSnowflakeCompatibleName()
}
