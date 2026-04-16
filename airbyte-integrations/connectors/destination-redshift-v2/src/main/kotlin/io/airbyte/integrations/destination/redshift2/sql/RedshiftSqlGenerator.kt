/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift2.sql

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

@Singleton
class RedshiftSqlGenerator {
    private val log = KotlinLogging.logger {}

    companion object {
        private const val DEDUPED_TABLE_ALIAS = "deduped_source"
        private val EXTRACTED_AT_COLUMN_NAME = quoteIdentifier(COLUMN_NAME_AB_EXTRACTED_AT)
        private val DELETED_AT_COLUMN_NAME = quoteIdentifier(CDC_DELETED_AT_COLUMN)

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

    fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        replace: Boolean,
    ): String {
        val metaColumns = META_COLUMNS
        val userColumns = getUserColumns(stream)

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

        val dropStatement =
            if (replace) "DROP TABLE IF EXISTS ${getFullyQualifiedName(tableName)};\n" else ""

        return """
            |BEGIN TRANSACTION;
            |${dropStatement}
            |CREATE TABLE IF NOT EXISTS ${getFullyQualifiedName(tableName)} ($columnDeclarations);
            |COMMIT;
        """
            .trimMargin()
            .andLog()
    }

    fun dropTable(tableName: TableName): String =
        "DROP TABLE IF EXISTS ${getFullyQualifiedName(tableName)};".andLog()

    fun addColumn(tableName: TableName, columnName: String, columnType: String): String =
        "ALTER TABLE ${getFullyQualifiedName(tableName)} ADD COLUMN ${quoteIdentifier(columnName)} $columnType;".andLog()

    fun countTable(tableName: TableName): String =
        "SELECT COUNT(*) AS \"total\" FROM ${getFullyQualifiedName(tableName)};".andLog()

    fun getGenerationId(tableName: TableName): String =
        "SELECT ${quoteIdentifier(COLUMN_NAME_AB_GENERATION_ID)} FROM ${
            getFullyQualifiedName(
                tableName,
            )
        } LIMIT 1;".andLog()

    fun deleteByRawId(tableName: TableName): String =
        "DELETE FROM ${getFullyQualifiedName(tableName)} WHERE ${quoteIdentifier("_airbyte_raw_id")} = ?;".andLog()

    /** Generates an `INSERT INTO target SELECT FROM source` to copy data between tables. */
    fun copyTable(
        columnNames: List<String>,
        sourceTableName: TableName,
        targetTableName: TableName,
    ): String {
        val quotedColumnNames = columnNames.joinToString(", ") { quoteIdentifier(it) }
        return """
            |INSERT INTO ${getFullyQualifiedName(targetTableName)} ($quotedColumnNames)
            |SELECT $quotedColumnNames
            |FROM ${getFullyQualifiedName(sourceTableName)};
        """
            .trimMargin()
            .andLog()
    }

    /**
     * Generates a rename-based table swap within a transaction:
     * 1. DROP the target table
     * 2. RENAME the source table to the target name
     * 3. If cross-schema, SET SCHEMA to move the renamed table
     */
    fun overwriteTable(sourceTableName: TableName, targetTableName: TableName): String {
        val moveSchemaSql =
            if (sourceTableName.namespace != targetTableName.namespace) {
                "\nALTER TABLE ${getNamespace(sourceTableName)}.${getName(targetTableName)} SET SCHEMA ${
                    getNamespace(
                        targetTableName,
                    )
                };"
            } else {
                ""
            }

        return """
            |BEGIN TRANSACTION;
            |DROP TABLE IF EXISTS ${getFullyQualifiedName(targetTableName)};
            |ALTER TABLE ${getFullyQualifiedName(sourceTableName)} RENAME TO ${
            getName(
                targetTableName,
            )
        };
            |$moveSchemaSql
            |COMMIT;
        """
            .trimMargin()
            .andLog()
    }

    /**
     * Generates a CTE-based upsert statement to performs:
     * 1. **Deduplication CTE**: Deduplicates source rows by primary key using ROW_NUMBER()
     * 2. **CDC Delete CTE**: (if enabled) Deletes target rows matching CDC deletion markers
     * 3. **Update CTE**: Updates existing target rows with newer source data
     * 4. **Insert**: Inserts new rows that don't exist in the target
     */
    fun upsertTable(
        stream: DestinationStream,
        sourceTableName: TableName,
        targetTableName: TableName,
    ): String {
        val importType = stream.tableSchema.importType as Dedupe

        if (importType.primaryKey.isEmpty()) {
            throw IllegalArgumentException("Cannot perform upsert without primary key")
        }

        val primaryKeyTargetColumns = getPrimaryKeysColumnNamesQuoted(stream)
        val cursorTargetColumn = getCursorColumnNameQuoted(stream)
        val allTargetColumns = getTargetColumnNamesForStream(stream)

        val selectDedupedQuery =
            selectDeduped(
                primaryKeyTargetColumns,
                cursorTargetColumn,
                allTargetColumns,
                sourceTableName,
            )

        val cdcHardDeleteEnabled =
            stream.tableSchema.columnSchema.inputSchema.containsKey(CDC_DELETED_AT_COLUMN)

        val cdcDeleteQuery =
            cdcDelete(
                DEDUPED_TABLE_ALIAS,
                cursorTargetColumn,
                targetTableName,
                primaryKeyTargetColumns,
                cdcHardDeleteEnabled,
            )

        val updateExistingRowsQuery =
            updateExistingRows(
                DEDUPED_TABLE_ALIAS,
                targetTableName,
                allTargetColumns,
                primaryKeyTargetColumns,
                cursorTargetColumn,
                cdcHardDeleteEnabled,
            )

        val insertNewRowsQuery =
            insertNewRows(
                DEDUPED_TABLE_ALIAS,
                targetTableName,
                allTargetColumns,
                primaryKeyTargetColumns,
                cdcHardDeleteEnabled,
            )

        return """
            |WITH $DEDUPED_TABLE_ALIAS AS (
            |$selectDedupedQuery
            |),
            |
            |$cdcDeleteQuery
            |updates AS (
            |$updateExistingRowsQuery
            |)
            |
            |$insertNewRowsQuery
        """
            .trimMargin()
            .andLog()
    }

    /**
     * Generates a SELECT with ROW_NUMBER() window function for deduplication.
     *
     * Partitions by primary key, orders by cursor (DESC NULLS LAST) then extracted_at (DESC), and
     * keeps only the first row (most recent) per primary key.
     */
    internal fun selectDeduped(
        primaryKeyTargetColumns: List<String>,
        cursorTargetColumn: String?,
        allTargetColumns: List<String>,
        sourceTableName: TableName,
    ): String {
        val cursorOrderClause = cursorTargetColumn?.let { "$it DESC NULLS LAST," } ?: ""

        return """
            |  SELECT ${allTargetColumns.joinToString(", ")}
            |  FROM (
            |    SELECT *,
            |      ROW_NUMBER() OVER (
            |        PARTITION BY ${primaryKeyTargetColumns.joinToString(", ")}
            |        ORDER BY
            |          $cursorOrderClause $EXTRACTED_AT_COLUMN_NAME DESC
            |      ) AS row_number
            |    FROM ${getFullyQualifiedName(sourceTableName)}
            |  ) AS deduplicated
            |  WHERE row_number = 1
        """.trimMargin()
    }

    /**
     * Generates the CDC hard-delete CTE, or an empty string if CDC hard delete is disabled.
     *
     * Deletes target rows where the source has a CDC deletion marker and the deletion is newer than
     * the target record.
     */
    internal fun cdcDelete(
        dedupTableAlias: String,
        cursorTargetColumn: String?,
        targetTableName: TableName,
        primaryKeyTargetColumns: List<String>,
        cdcHardDeleteEnabled: Boolean,
    ): String {
        if (!cdcHardDeleteEnabled) {
            return ""
        }

        val primaryKeysMatchingCondition =
            primaryKeyTargetColumns.joinToString(" AND ") { pk ->
                "${getFullyQualifiedName(targetTableName)}.$pk = $dedupTableAlias.$pk"
            }

        val cursorComparison =
            buildCursorComparison(cursorTargetColumn, targetTableName, dedupTableAlias)

        return """
            |deleted AS (
            |  DELETE FROM ${getFullyQualifiedName(targetTableName)}
            |  USING $dedupTableAlias
            |  WHERE $primaryKeysMatchingCondition
            |    AND $dedupTableAlias.$DELETED_AT_COLUMN_NAME IS NOT NULL
            |    AND ($cursorComparison)
            |),
            |
        """.trimMargin()
    }

    /**
     * Generates an UPDATE statement that updates existing target rows with newer source data.
     *
     * Rows are matched by primary key and only updated when the source cursor/extracted_at is
     * newer. CDC-deleted rows are skipped if CDC hard delete is enabled.
     */
    internal fun updateExistingRows(
        dedupTableAlias: String,
        targetTableName: TableName,
        allTargetColumns: List<String>,
        primaryKeyTargetColumns: List<String>,
        cursorTargetColumn: String?,
        cdcHardDeleteEnabled: Boolean,
    ): String {
        val primaryKeysMatches =
            primaryKeyTargetColumns.joinToString(" AND ") { pk ->
                "${getFullyQualifiedName(targetTableName)}.$pk = $dedupTableAlias.$pk"
            }

        val cursorComparison =
            buildCursorComparison(cursorTargetColumn, targetTableName, dedupTableAlias)

        val updateAssignments =
            allTargetColumns.joinToString(",\n    ") { col -> "$col = $dedupTableAlias.$col" }

        val skipCdcDeletedClause =
            if (cdcHardDeleteEnabled) {
                "\n    AND $dedupTableAlias.$DELETED_AT_COLUMN_NAME IS NULL"
            } else {
                ""
            }

        return """
            |  UPDATE ${getFullyQualifiedName(targetTableName)}
            |  SET
            |    $updateAssignments
            |  FROM $dedupTableAlias
            |  WHERE $primaryKeysMatches$skipCdcDeletedClause
            |    AND ($cursorComparison)
        """.trimMargin()
    }

    /**
     * Generates an INSERT statement for new rows from the deduped source that don't exist in the
     * target.
     *
     * Uses `NOT EXISTS` to check for existing records by primary key. CDC-deleted rows are skipped
     * if CDC hard delete is enabled.
     */
    internal fun insertNewRows(
        dedupTableAlias: String,
        targetTableName: TableName,
        allTargetColumns: List<String>,
        primaryKeyTargetColumns: List<String>,
        cdcHardDeleteEnabled: Boolean,
    ): String {
        val primaryKeysConditions =
            primaryKeyTargetColumns.joinToString(" AND ") { pk ->
                "${getFullyQualifiedName(targetTableName)}.$pk = $dedupTableAlias.$pk"
            }

        val skipCdcDeletedClause =
            if (cdcHardDeleteEnabled) {
                "\n  AND $dedupTableAlias.$DELETED_AT_COLUMN_NAME IS NULL"
            } else {
                ""
            }

        return """
            |INSERT INTO ${getFullyQualifiedName(targetTableName)} (
            |  ${allTargetColumns.joinToString(",\n  ")}
            |)
            |SELECT
            |  ${allTargetColumns.joinToString(",\n  ")}
            |FROM $dedupTableAlias
            |WHERE
            |  NOT EXISTS (
            |    SELECT 1
            |    FROM ${getFullyQualifiedName(targetTableName)}
            |    WHERE $primaryKeysConditions
            |  )$skipCdcDeletedClause
        """.trimMargin()
    }

    /**
     * Builds a 4-way NULL-safe cursor comparison expression to determine if source data is newer
     * than target data.
     */
    private fun buildCursorComparison(
        cursorTargetColumn: String?,
        targetTableName: TableName,
        dedupTableAlias: String,
    ): String {
        val target = getFullyQualifiedName(targetTableName)
        val source = dedupTableAlias
        return if (cursorTargetColumn != null) {
            """
            |$target.$cursorTargetColumn < $source.$cursorTargetColumn
            |    OR ($target.$cursorTargetColumn = $source.$cursorTargetColumn AND $target.$EXTRACTED_AT_COLUMN_NAME < $source.$EXTRACTED_AT_COLUMN_NAME)
            |    OR ($target.$cursorTargetColumn IS NULL AND $source.$cursorTargetColumn IS NOT NULL)
            |    OR ($target.$cursorTargetColumn IS NULL AND $source.$cursorTargetColumn IS NULL AND $target.$EXTRACTED_AT_COLUMN_NAME < $source.$EXTRACTED_AT_COLUMN_NAME)
            """.trimMargin()
        } else {
            "$target.$EXTRACTED_AT_COLUMN_NAME < $source.$EXTRACTED_AT_COLUMN_NAME"
        }
    }

    /**
     * Generates SQL to evolve a table's schema:
     * 1. ADD COLUMN with the new type (temp name)
     * 2. UPDATE to cast data from the old column to the temp column
     * 3. DROP the old column
     * 4. RENAME the temp column to the original name
     *
     * For SUPER <-> VARCHAR conversions, uses `JSON_SERIALIZE()` / `JSON_PARSE()` instead of CAST.
     */
    fun matchSchemas(
        tableName: TableName,
        columnsToAdd: Map<String, ColumnType>,
        columnsToRemove: Map<String, ColumnType>,
        columnsToModify: Map<String, ColumnTypeChange>,
    ): String {
        val clauses = mutableListOf<String>()
        val fqn = getFullyQualifiedName(tableName)

        // Add new columns (no NOT NULL -- preexisting rows would have no default)
        columnsToAdd.forEach { (name, columnType) ->
            clauses.add("ALTER TABLE $fqn ADD COLUMN ${quoteIdentifier(name)} ${columnType.type};")
        }

        // Remove columns
        columnsToRemove.forEach { (name, _) ->
            clauses.add("ALTER TABLE $fqn DROP COLUMN ${quoteIdentifier(name)};")
        }

        // Modify column types via 4-step rename pattern
        columnsToModify.forEach { (name, typeChange) ->
            clauses.addAll(buildTypeChangeStatements(fqn, name, typeChange))
        }

        return """
            |BEGIN TRANSACTION;
            |${clauses.joinToString("\n")}
            |COMMIT;
        """
            .trimMargin()
            .andLog()
    }

    /**
     * Builds the 4-step ALTER TABLE statements to change a column's type in Redshift.
     *
     * For SUPER -> VARCHAR: uses `JSON_SERIALIZE(col)` to preserve JSON structure as a string. For
     * VARCHAR -> SUPER: uses `JSON_PARSE(col)` to parse the JSON string into a SUPER value. For all
     * other conversions: uses `CAST(col AS new_type)`.
     */
    private fun buildTypeChangeStatements(
        fullyQualifiedTableName: String,
        columnName: String,
        typeChange: ColumnTypeChange,
    ): List<String> {
        val quotedName = quoteIdentifier(columnName)
        val tempColumn = quoteIdentifier("_airbyte_tmp_$columnName")
        val oldType = typeChange.originalType.type
        val newType = typeChange.newType.type

        val castExpression =
            when {
                // SUPER -> VARCHAR: serialize JSON to string
                oldType == RedshiftDataType.SUPER.typeName && newType.startsWith("varchar") ->
                    "JSON_SERIALIZE($quotedName)"
                // VARCHAR -> SUPER: parse string as JSON
                oldType.startsWith("varchar") && newType == RedshiftDataType.SUPER.typeName ->
                    "JSON_PARSE($quotedName)"
                // All other conversions: standard CAST
                else -> "CAST($quotedName AS $newType)"
            }

        return listOf(
            // Step 1: Add temp column with the new type
            "ALTER TABLE $fullyQualifiedTableName ADD COLUMN $tempColumn $newType;",
            // Step 2: Cast data from old column to temp column
            "UPDATE $fullyQualifiedTableName SET $tempColumn = $castExpression;",
            // Step 3: Drop the original column
            "ALTER TABLE $fullyQualifiedTableName DROP COLUMN $quotedName;",
            // Step 4: Rename temp column to the original name
            "ALTER TABLE $fullyQualifiedTableName RENAME COLUMN $tempColumn TO $quotedName;",
        )
    }

    /** Generates a query to retrieve column metadata from `information_schema.columns` */
    fun getTableSchema(tableName: TableName): String =
        """
            |SELECT column_name, data_type, is_nullable
            |FROM information_schema.columns
            |WHERE table_schema = '${RedshiftSqlEscapeUtils.escapeSqlString(tableName.namespace)}'
            |AND table_name = '${RedshiftSqlEscapeUtils.escapeSqlString(tableName.name)}'
            |ORDER BY ordinal_position;
        """
            .trimMargin()
            .andLog()

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

    // ================================================================
    // Internal helpers
    // ================================================================

    /** Returns the user columns (non-meta) from the stream's pre-computed table schema. */
    private fun getUserColumns(stream: DestinationStream): Map<String, ColumnType> =
        stream.tableSchema.columnSchema.finalSchema

    /** Builds the fully qualified table name as `"namespace"."name"`. */
    private fun getFullyQualifiedName(tableName: TableName): String =
        "${getNamespace(tableName)}.${getName(tableName)}"

    private fun getNamespace(tableName: TableName): String =
        quoteIdentifier(tableName.namespace.ifBlank { "public" })

    private fun getName(tableName: TableName): String = quoteIdentifier(tableName.name)

    /** Returns all target column names (meta + user) for a stream, quoted. */
    private fun getTargetColumnNamesForStream(stream: DestinationStream): List<String> {
        val metaColumnNames = META_COLUMNS.keys.map { quoteIdentifier(it) }
        val userColumnNames = getUserColumns(stream).keys.map { quoteIdentifier(it) }
        return metaColumnNames + userColumnNames
    }

    private fun getPrimaryKeysColumnNamesQuoted(stream: DestinationStream): List<String> =
        stream.tableSchema.getPrimaryKey().flatten().map { quoteIdentifier(it) }

    private fun getCursorColumnNameQuoted(stream: DestinationStream): String? =
        stream.tableSchema.getCursor().firstOrNull()?.let { quoteIdentifier(it) }

    /** Logs the SQL string at INFO level and returns it. */
    private fun String.andLog(): String {
        log.info { this }
        return this
    }
}
