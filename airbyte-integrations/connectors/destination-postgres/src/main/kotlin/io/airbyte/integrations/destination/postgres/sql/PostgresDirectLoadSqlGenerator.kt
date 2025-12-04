/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.sql

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.postgres.spec.CdcDeletionMode
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import jakarta.inject.Singleton
import kotlin.collections.forEach

internal const val COUNT_TOTAL_ALIAS = "total"

@Singleton
class PostgresDirectLoadSqlGenerator(
    private val postgresColumnUtils: PostgresColumnUtils,
    private val postgresConfiguration: PostgresConfiguration
) {

    private val dropTableSuffix: String =
        if (postgresConfiguration.dropCascade == true) " CASCADE" else ""

    companion object {
        private const val DEDUPED_TABLE_ALIAS = "deduped_source"
        private val EXTRACTED_AT_COLUMN_NAME = quoteIdentifier(COLUMN_NAME_AB_EXTRACTED_AT)
        private val DELETED_AT_COLUMN_NAME = quoteIdentifier(CDC_DELETED_AT_COLUMN)

        private fun quoteIdentifier(identifier: String) = "\"${identifier}\""
    }

    /**
     * Returns a pair of (createTableSql, createIndexesSql). The table creation is wrapped in a
     * transaction while indexes are created separately to handle potential race conditions when
     * multiple streams create indexes with similar truncated names.
     */
    fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ): Pair<String, String> {
        val columnDeclarations =
            postgresColumnUtils.getTargetColumns(stream, columnNameMapping).joinToString(",\n") {
                it.toSQLString()
            }
        val dropTableIfExistsStatement =
            if (replace) "DROP TABLE IF EXISTS ${getFullyQualifiedName(tableName)}$dropTableSuffix;"
            else ""
        val createTableSql =
            """
            BEGIN TRANSACTION;
            $dropTableIfExistsStatement
            CREATE TABLE IF NOT EXISTS ${getFullyQualifiedName(tableName)} (
                $columnDeclarations
            );
            COMMIT;
            """
        val createIndexesSql = createIndexes(stream, tableName, columnNameMapping)
        return Pair(createTableSql, createIndexesSql)
    }

    /**
     * Generates index creation statements for a table based on the stream's configuration.
     *
     * Creates up to three indexes:
     * - Primary key index (if dedupe stream with primary keys, not in raw tables mode)
     * - Cursor index (if dedupe stream with cursor field, not in raw tables mode)
     * - Extracted_at index (always created for all streams)
     *
     * In legacyRawTablesOnly mode, primary key and cursor indexes are skipped because user-defined
     * columns don't exist at the table level (they're stored in _airbyte_data JSONB).
     */
    private fun createIndexes(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ): String {
        // In raw tables mode, skip primary key and cursor indexes since those columns don't exist
        val primaryKeyIndexStatement =
            if (postgresConfiguration.legacyRawTablesOnly) {
                ""
            } else {
                val primaryKeyColumnNames = getPrimaryKeysColumnNames(stream, columnNameMapping)
                createPrimaryKeyIndexStatement(primaryKeyColumnNames, tableName)
            }
        val cursorIndexStatement =
            if (postgresConfiguration.legacyRawTablesOnly) {
                ""
            } else {
                val cursorColumnName = getCursorColumnName(stream, columnNameMapping)
                createCursorIndexStatement(cursorColumnName, tableName)
            }
        val extractedAtIndexStatement =
            "CREATE INDEX IF NOT EXISTS ${getExtractedAtIndexName(tableName)} ON ${getFullyQualifiedName(tableName)} ($EXTRACTED_AT_COLUMN_NAME);"

        return """
            $primaryKeyIndexStatement
            $cursorIndexStatement
            $extractedAtIndexStatement
        """
    }

    private fun getPrimaryKeysColumnNames(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ) =
        postgresColumnUtils.getPrimaryKeysColumnNames(stream, columnNameMapping).map {
            quoteIdentifier(it)
        }

    private fun getPrimaryKeysColumnNames(
        importType: Dedupe,
        columnNameMapping: ColumnNameMapping
    ) =
        postgresColumnUtils.getPrimaryKeysColumnNames(importType, columnNameMapping).map {
            quoteIdentifier(it)
        }

    private fun getCursorColumnName(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ) =
        postgresColumnUtils.getCursorColumnName(stream, columnNameMapping)?.let {
            quoteIdentifier(it)
        }

    private fun getCursorColumnName(cursor: List<String>, columnNameMapping: ColumnNameMapping) =
        postgresColumnUtils.getCursorColumnName(cursor, columnNameMapping)?.let {
            quoteIdentifier(it)
        }

    internal fun recreatePrimaryKeyIndex(
        primaryKeyColumnNames: List<String>,
        tableName: TableName
    ): String {
        val dropPrimaryKeyIndexStatement =
            dropIndex(
                indexName = getPrimaryKeyIndexName(tableName),
                schema = getNamespace(tableName)
            )

        val primaryKeyIndexStatement =
            createPrimaryKeyIndexStatement(primaryKeyColumnNames, tableName)

        return """
            $dropPrimaryKeyIndexStatement
            $primaryKeyIndexStatement
        """
    }

    private fun createPrimaryKeyIndexStatement(
        primaryKeyColumnNames: List<String>,
        tableName: TableName
    ): String {
        return primaryKeyColumnNames
            .takeIf { it.isNotEmpty() }
            ?.let {
                "CREATE INDEX IF NOT EXISTS ${getPrimaryKeyIndexName(tableName)} ON ${getFullyQualifiedName(tableName)} (${it.joinToString(", ")});"
            }
            ?: ""
    }

    internal fun recreateCursorIndex(cursorColumnName: String?, tableName: TableName): String {
        val dropCursorIndexStatement =
            dropIndex(indexName = getCursorIndexName(tableName), schema = getNamespace(tableName))
        val cursorIndexStatement = createCursorIndexStatement(cursorColumnName, tableName)

        return """
            $dropCursorIndexStatement
            $cursorIndexStatement
        """
    }

    private fun createCursorIndexStatement(
        cursorColumnName: String?,
        tableName: TableName
    ): String {
        return cursorColumnName?.let {
            "CREATE INDEX IF NOT EXISTS ${getCursorIndexName(tableName)} ON ${getFullyQualifiedName(tableName)} ($it);"
        }
            ?: ""
    }

    private fun getPrimaryKeyIndexName(tableName: TableName): String =
        quoteIdentifier(postgresColumnUtils.getPrimaryKeyIndexName(tableName))

    private fun getCursorIndexName(tableName: TableName): String =
        quoteIdentifier(postgresColumnUtils.getCursorIndexName(tableName))

    private fun getExtractedAtIndexName(tableName: TableName): String =
        quoteIdentifier(postgresColumnUtils.getExtractedAtIndexName(tableName))

    fun overwriteTable(sourceTableName: TableName, targetTableName: TableName): String {
        return """
            BEGIN TRANSACTION;
            DROP TABLE IF EXISTS ${getFullyQualifiedName(targetTableName)}$dropTableSuffix;
            ALTER TABLE ${getFullyQualifiedName(sourceTableName)} RENAME TO ${getName(targetTableName)};
            COMMIT;
            """
    }

    fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        val columnNames = getTargetColumnNames(columnNameMapping).joinToString(",")
        return """
            INSERT INTO ${getFullyQualifiedName(targetTableName)} ($columnNames)
            SELECT $columnNames
            FROM ${getFullyQualifiedName(sourceTableName)};
            """
    }

    private fun getTargetColumnNames(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): List<String> {
        return postgresColumnUtils.getTargetColumns(stream, columnNameMapping).map {
            getTargetColumnName(it.columnName, columnNameMapping)
        }
    }

    private fun getTargetColumnNames(columnNameMapping: ColumnNameMapping): List<String> =
        getDefaultColumnNames() +
            columnNameMapping.map { (_, targetName) -> quoteIdentifier(targetName) }

    private fun getTargetColumnName(
        streamColumnName: String,
        columnNameMapping: ColumnNameMapping
    ): String {
        return quoteIdentifier(
            postgresColumnUtils.getTargetColumnName(streamColumnName, columnNameMapping)
        )
    }

    private fun getDefaultColumnNames(): List<String> =
        postgresColumnUtils.defaultColumns().map { quoteIdentifier(it.columnName) }

    /**
     * Generates an SQL statement that upserts (merge) data from a source staging table into a
     * target table.
     *
     * The generated SQL performs the following operations in a single statement:
     * 1. **Deduplication CTE**: Deduplicates the source data based on primary keys
     * 2. **CDC Delete CTE**: If CDC hard delete is enabled and the stream contains CDC deleted
     * records,
     * ```
     *    this CTE deletes rows from the target table.
     * ```
     * 3. **Update CTE**: Updates existing rows in the target table with newer data from the source
     * 4. **Insert Statement**: Inserts new rows from the source that don't exist in the target
     * table.
     *
     * @throws IllegalArgumentException if the stream's import type does not contain a primary key.
     */
    fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        val importType = stream.importType as Dedupe

        if (importType.primaryKey.isEmpty()) {
            throw IllegalArgumentException("Cannot perform upsert without primary key")
        }

        val primaryKeyTargetColumns = getPrimaryKeysColumnNames(importType, columnNameMapping)
        val cursorTargetColumn = getCursorColumnName(importType.cursor, columnNameMapping)
        val allTargetColumns = getTargetColumnNames(stream, columnNameMapping)

        val selectDedupedQuery =
            selectDeduped(
                primaryKeyTargetColumns,
                cursorTargetColumn,
                allTargetColumns,
                sourceTableName
            )

        val cdcHardDeleteEnabled =
            stream.schema.asColumns().containsKey(CDC_DELETED_AT_COLUMN) &&
                postgresConfiguration.cdcDeletionMode == CdcDeletionMode.HARD_DELETE

        val cdcDeleteQuery =
            cdcDelete(
                DEDUPED_TABLE_ALIAS,
                cursorTargetColumn,
                targetTableName,
                primaryKeyTargetColumns,
                cdcHardDeleteEnabled
            )

        val updateExistingRowsQuery =
            updateExistingRows(
                DEDUPED_TABLE_ALIAS,
                targetTableName,
                allTargetColumns,
                primaryKeyTargetColumns,
                cursorTargetColumn,
                cdcHardDeleteEnabled
            )

        val insertNewRowsQuery =
            insertNewRows(
                DEDUPED_TABLE_ALIAS,
                targetTableName,
                allTargetColumns,
                primaryKeyTargetColumns,
                cdcHardDeleteEnabled
            )

        return """
            WITH $DEDUPED_TABLE_ALIAS AS (
              $selectDedupedQuery
            ),

            $cdcDeleteQuery

            updates AS (
              $updateExistingRowsQuery
            )

            $insertNewRowsQuery
            """
    }

    /**
     * Generates an INSERT statement that adds new rows from the deduplicated source that don't
     * exist in the target.
     *
     * Uses NOT EXISTS to check for existing records by primary key. If CDC hard delete is enabled,
     * filters out records marked as deleted.
     */
    @VisibleForTesting
    internal fun insertNewRows(
        dedupTableAlias: String,
        targetTableName: TableName,
        allTargetColumns: List<String>,
        primaryKeyTargetColumns: List<String>,
        cdcHardDeleteEnabled: Boolean
    ): String {
        val primaryKeysConditions =
            primaryKeyTargetColumns.joinToString(" AND ") { primaryKey ->
                "${getFullyQualifiedName(targetTableName)}.$primaryKey = $dedupTableAlias.$primaryKey"
            }

        val skipCdcDeletedClause =
            if (cdcHardDeleteEnabled) "AND $dedupTableAlias.$DELETED_AT_COLUMN_NAME IS NULL" else ""

        return """
            INSERT INTO ${getFullyQualifiedName(targetTableName)} (
              ${allTargetColumns.joinToString(",\n  ")}
            )
            SELECT
              ${allTargetColumns.joinToString(",\n  ") }
            FROM $dedupTableAlias
            WHERE
              NOT EXISTS (
                SELECT 1
                FROM ${getFullyQualifiedName(targetTableName)}
                WHERE $primaryKeysConditions
              )
              $skipCdcDeletedClause
        """
    }

    /**
     * Generates an UPDATE statement that updates existing rows in the target with newer data from
     * the source.
     *
     * Rows are matched by primary key and only updated if the source data is newer (determined by
     * cursor or extracted_at comparison). If CDC hard delete is enabled, skips records marked as
     * deleted.
     */
    @VisibleForTesting
    internal fun updateExistingRows(
        dedupTableAlias: String,
        targetTableName: TableName,
        allTargetColumns: List<String>,
        primaryKeyTargetColumns: List<String>,
        cursorTargetColumn: String?,
        cdcHardDeleteEnabled: Boolean
    ): String {
        val primaryKeysMatches =
            primaryKeyTargetColumns.joinToString(" AND ") { primaryKey ->
                "${getFullyQualifiedName(targetTableName)}.$primaryKey = $dedupTableAlias.$primaryKey"
            }

        val cursorComparison =
            buildCursorComparison(cursorTargetColumn, targetTableName, dedupTableAlias)

        val updateAssignments =
            allTargetColumns.joinToString(",\n") { columnName ->
                "$columnName = $dedupTableAlias.$columnName"
            }

        val skipCdcDeletedClause =
            if (cdcHardDeleteEnabled) "AND $dedupTableAlias.$DELETED_AT_COLUMN_NAME IS NULL" else ""
        return """
             UPDATE ${getFullyQualifiedName(targetTableName)}
             SET 
                $updateAssignments
             FROM $dedupTableAlias
                WHERE $primaryKeysMatches
                    $skipCdcDeletedClause
                    AND ($cursorComparison)
        """
    }

    /**
     * Generates a CDC hard delete statement wrapped in a CTE, or returns empty string if disabled.
     *
     * Deletes rows from the target table where the source has a CDC deletion marker and the
     * deletion is newer than the target record (based on cursor or extracted_at).
     */
    @VisibleForTesting
    internal fun cdcDelete(
        dedupTableAlias: String,
        cursorTargetColumn: String?,
        targetTableName: TableName,
        primaryKeyTargetColumns: List<String>,
        cdcHardDeleteEnabled: Boolean
    ): String {
        if (!cdcHardDeleteEnabled) {
            return ""
        }

        val primaryKeysMatchingCondition =
            primaryKeyTargetColumns.joinToString(" AND ") { primaryKey ->
                "${getFullyQualifiedName(targetTableName)}.$primaryKey = $dedupTableAlias.$primaryKey"
            }

        // ensure we only delete if the deletion is newer
        val cursorComparison =
            buildCursorComparison(cursorTargetColumn, targetTableName, dedupTableAlias)

        val deleteStatement =
            """
            DELETE FROM ${getFullyQualifiedName(targetTableName)}
            USING $dedupTableAlias
            WHERE $primaryKeysMatchingCondition
                AND $dedupTableAlias.$DELETED_AT_COLUMN_NAME IS NOT NULL
                AND ($cursorComparison)
        """

        return """
            deleted AS (
            $deleteStatement
            ),
        """
    }

    /**
     * Builds a SQL comparison expression to determine if source data is newer than target data.
     *
     * If a cursor exists, compares cursor values with extracted_at as tiebreaker and NULL handling.
     * If no cursor, compares only extracted_at timestamps.
     */
    private fun buildCursorComparison(
        cursorTargetColumn: String?,
        targetTableName: TableName,
        dedupTableAlias: String
    ): String {
        return if (cursorTargetColumn != null) {
            val extractedAtColumn = EXTRACTED_AT_COLUMN_NAME
            """
                  ${getFullyQualifiedName(targetTableName)}.$cursorTargetColumn < $dedupTableAlias.$cursorTargetColumn
                  OR (${getFullyQualifiedName(targetTableName)}.$cursorTargetColumn = $dedupTableAlias.$cursorTargetColumn AND ${getFullyQualifiedName(targetTableName)}.$extractedAtColumn < $dedupTableAlias.$extractedAtColumn)
                  OR (${getFullyQualifiedName(targetTableName)}.$cursorTargetColumn IS NULL AND $dedupTableAlias.$cursorTargetColumn IS NOT NULL)
                  OR (${getFullyQualifiedName(targetTableName)}.$cursorTargetColumn IS NULL AND $dedupTableAlias.$cursorTargetColumn IS NULL AND ${getFullyQualifiedName(targetTableName)}.$extractedAtColumn < $dedupTableAlias.$extractedAtColumn)
                """
        } else {
            // No cursor - use extraction timestamp only
            val extractedAtColumn = EXTRACTED_AT_COLUMN_NAME
            "${getFullyQualifiedName(targetTableName)}.$extractedAtColumn < $dedupTableAlias.$extractedAtColumn"
        }
    }

    /**
     * Generates a SELECT query that deduplicates source data using ROW_NUMBER() window function.
     *
     * Partitions by primary key and orders by cursor (if present) then extracted_at, keeping only
     * the most recent record for each unique primary key.
     */
    @VisibleForTesting
    internal fun selectDeduped(
        primaryKeyTargetColumns: List<String>,
        cursorTargetColumn: String?,
        allTargetColumns: List<String>,
        sourceTableName: TableName
    ): String {
        val cursorOrderClause = cursorTargetColumn?.let { "$it DESC NULLS LAST," } ?: ""

        return """
            SELECT ${allTargetColumns.joinToString(", ")}
            FROM (
              SELECT *,
                ROW_NUMBER() OVER (
                  PARTITION BY ${primaryKeyTargetColumns.joinToString( ", " )}
                  ORDER BY
                    $cursorOrderClause $EXTRACTED_AT_COLUMN_NAME DESC
                ) AS row_number
              FROM ${getFullyQualifiedName(sourceTableName)}
            ) AS deduplicated
            WHERE row_number = 1
        """
    }

    fun dropTable(tableName: TableName): String =
        "DROP TABLE IF EXISTS ${getFullyQualifiedName(tableName)}$dropTableSuffix;"

    fun countTable(tableName: TableName): String {
        return "SELECT COUNT(*) AS \"$COUNT_TOTAL_ALIAS\" FROM ${getFullyQualifiedName(tableName)};"
    }

    fun createNamespace(namespace: String): String {
        return "CREATE SCHEMA IF NOT EXISTS \"$namespace\";"
    }

    fun getGenerationId(tableName: TableName): String =
        "SELECT \"${COLUMN_NAME_AB_GENERATION_ID}\" FROM ${getFullyQualifiedName(tableName)} LIMIT 1;"

    fun getTableSchema(tableName: TableName): String =
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = '${tableName.namespace}'
        AND table_name = '${tableName.name}';
        """

    /**
     * Generates SQL to query for the columns in the primary key index. The query returns column
     * names in the order they appear in the index.
     *
     * @param tableName The table to query the index for
     * @return SQL query that returns column names in the primary key index
     */
    fun getPrimaryKeyIndexColumns(tableName: TableName): String =
        getIndexColumns(
            indexName = postgresColumnUtils.getPrimaryKeyIndexName(tableName),
            namespace = tableName.namespace
        )

    /**
     * Generates SQL to query for the column in the cursor index.
     *
     * @param tableName The table to query the index for
     * @return SQL query that returns column name in the cursor index
     */
    fun getCursorIndexColumn(tableName: TableName): String =
        getIndexColumns(
            indexName = postgresColumnUtils.getCursorIndexName(tableName),
            namespace = tableName.namespace
        )

    private fun getIndexColumns(indexName: String, namespace: String): String =
        """
        SELECT a.attname AS column_name
        FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        JOIN pg_class c ON c.oid = i.indexrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relname = '${indexName}'
        AND n.nspname = '${namespace}'
        ORDER BY array_position(i.indkey, a.attnum);
        """

    private fun dropIndex(indexName: String, schema: String): String =
        "DROP INDEX IF EXISTS $schema.$indexName$dropTableSuffix;"

    fun copyFromCsv(tableName: TableName): String =
        """
        COPY "${tableName.namespace}"."${tableName.name}"
        FROM STDIN
        WITH (FORMAT csv)
        """

    fun matchSchemas(
        tableName: TableName,
        columnsToAdd: Set<Column>,
        columnsToRemove: Set<Column>,
        columnsToModify: Set<Column>,
        columnsInDb: Set<Column>,
        recreatePrimaryKeyIndex: Boolean,
        primaryKeyColumnNames: List<String>,
        recreateCursorIndex: Boolean,
        cursorColumnName: String?
    ): String {
        val clauses = mutableSetOf<String>()
        val fullyQualifiedTableName = getFullyQualifiedName(tableName)
        columnsToAdd.forEach {
            clauses.add(
                "ALTER TABLE $fullyQualifiedTableName ADD COLUMN ${getName(it)} ${it.columnTypeName};"
            )
        }
        columnsToRemove.forEach {
            clauses.add(
                "ALTER TABLE $fullyQualifiedTableName DROP COLUMN ${getName(it)}$dropTableSuffix;"
            )
        }

        columnsToModify.forEach { newColumn ->
            val oldColumn = columnsInDb.find { it.columnName == newColumn.columnName }
            val oldType = oldColumn?.columnTypeName
            val newType = newColumn.columnTypeName

            val usingClause =
                when {
                    // Converting to jsonb from any type
                    newType == "jsonb" -> "USING to_jsonb(${getName(newColumn)})"
                    // Converting from jsonb to varchar/text - extract text value without JSON
                    // quotes
                    oldType == "jsonb" &&
                        (newType == "varchar" ||
                            newType == "text" ||
                            newType == "character varying") ->
                        "USING ${getName(newColumn)} #>> '{}'"
                    // Standard cast for other conversions
                    else -> "USING ${getName(newColumn)}::$newType"
                }
            clauses.add(
                "ALTER TABLE $fullyQualifiedTableName ALTER COLUMN ${getName(newColumn)} TYPE $newType $usingClause$dropTableSuffix;"
            )
        }

        if (recreatePrimaryKeyIndex) {
            val quotedPrimaryKeyColumnNames = primaryKeyColumnNames.map { quoteIdentifier(it) }
            clauses.add(recreatePrimaryKeyIndex(quotedPrimaryKeyColumnNames, tableName))
        }

        if (recreateCursorIndex) {
            val quotedCursorColumnName = cursorColumnName?.let { quoteIdentifier(it) }
            clauses.add(recreateCursorIndex(quotedCursorColumnName, tableName))
        }

        return """
            BEGIN TRANSACTION;
            ${clauses.joinToString("\n")}
            COMMIT;
        """
    }

    private fun getFullyQualifiedName(tableName: TableName): String =
        "${getNamespace(tableName)}.${getName(tableName)}"

    private fun getNamespace(tableName: TableName): String = "\"${tableName.namespace}\""

    private fun getName(tableName: TableName): String = "\"${tableName.name}\""

    private fun getName(column: Column): String = "\"${column.columnName}\""

    internal fun Column.toSQLString(): String {
        val isNullableSuffix = if (nullable) "" else "NOT NULL"
        return "\"$columnName\" $columnTypeName $isNullableSuffix".trim()
    }
}
