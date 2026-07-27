/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.sql

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift.schema.toRedshiftCompatibleName
import jakarta.inject.Singleton

@Singleton
class RedshiftSqlGenerator(private val config: RedshiftConfiguration) {

    /** Suffix appended to DROP TABLE / DROP COLUMN when cascade mode is enabled. */
    private val cascadeSuffix: String
        get() = if (config.dropCascade) " CASCADE" else ""

    companion object {
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
        "CREATE SCHEMA IF NOT EXISTS ${quoteIdentifier(namespace)};"

    /** Generates a query to check if a schema exists via `information_schema.schemata`. */
    fun namespaceExists(namespace: String): String =
        """
            |SELECT EXISTS(
            |    SELECT 1 FROM information_schema.schemata
            |    WHERE schema_name = '${RedshiftSqlEscapeUtils.escapeSqlString(namespace)}'
            |)
        """.trimMargin()

    /** Generates a query to check if a table exists via `information_schema.tables`. */
    fun tableExists(tableName: TableName): String =
        """
            |SELECT EXISTS(
            |    SELECT 1 FROM information_schema.tables
            |    WHERE table_schema = '${RedshiftSqlEscapeUtils.escapeSqlString(tableName.namespace)}'
            |    AND table_name = '${RedshiftSqlEscapeUtils.escapeSqlString(tableName.name)}'
            |)
        """.trimMargin()

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

        val createStatement =
            "CREATE TABLE IF NOT EXISTS ${getFullyQualifiedName(tableName)} ($columnDeclarations);"

        // Only wrap in a transaction when replacing (DROP + CREATE must be atomic).
        return if (replace) {
            """
                |BEGIN TRANSACTION;
                |DROP TABLE IF EXISTS ${getFullyQualifiedName(tableName)}$cascadeSuffix;
                |$createStatement
                |COMMIT;
            """.trimMargin()
        } else {
            createStatement
        }
    }

    fun dropTable(tableName: TableName): String =
        "DROP TABLE IF EXISTS ${getFullyQualifiedName(tableName)}$cascadeSuffix;"

    fun addColumn(tableName: TableName, columnName: String, columnType: String): String =
        "ALTER TABLE ${getFullyQualifiedName(tableName)} ADD COLUMN ${quoteIdentifier(columnName)} $columnType;"

    fun countTable(tableName: TableName): String =
        "SELECT COUNT(*) AS \"total\" FROM ${getFullyQualifiedName(tableName)};"

    /** Generates an efficient emptiness check using `SELECT EXISTS(... LIMIT 1)` */
    fun isTableNotEmpty(tableName: TableName): String =
        "SELECT EXISTS(SELECT 1 FROM ${getFullyQualifiedName(tableName)} LIMIT 1) AS \"not_empty\";"

    fun getGenerationId(tableName: TableName): String =
        """
            |SELECT ${quoteIdentifier(COLUMN_NAME_AB_GENERATION_ID)}
            |FROM ${getFullyQualifiedName(tableName)}
            |LIMIT 1;
        """.trimMargin()

    fun deleteByRawId(tableName: TableName): String =
        "DELETE FROM ${getFullyQualifiedName(tableName)} WHERE ${quoteIdentifier("_airbyte_raw_id")} = ?;"

    /**
     * Generates an `ALTER TABLE APPEND` to efficiently move data from the source table to the
     * target table. This moves the underlying data blocks instead of copying row-by-row, which is
     * significantly faster for large datasets. The source table is emptied after the operation.
     *
     * Requires both tables to have the same column structure (names, types, order). Cannot be
     * executed inside a transaction block (autoCommit must be true). So If the target table has
     * more columns than the source table, we specify the FILLTARGET parameter.
     *
     * @see <a
     * href="https://docs.aws.amazon.com/redshift/latest/dg/r_ALTER_TABLE_APPEND.html">Redshift
     * ALTER TABLE APPEND</a>
     */
    fun copyTable(
        sourceTableName: TableName,
        targetTableName: TableName,
    ): String =
        """
            |ALTER TABLE ${getFullyQualifiedName(targetTableName)}
            |APPEND FROM ${getFullyQualifiedName(sourceTableName)}
            |FILLTARGET;
        """.trimMargin()

    /**
     * Generates a rename-based table swap within a transaction:
     * 1. DROP the target table
     * 2. RENAME the source table to the target name
     */
    fun overwriteTable(sourceTableName: TableName, targetTableName: TableName): String {
        return """
            |BEGIN TRANSACTION;
            |DROP TABLE IF EXISTS ${getFullyQualifiedName(targetTableName)}$cascadeSuffix;
            |ALTER TABLE ${getFullyQualifiedName(sourceTableName)} RENAME TO ${getName(targetTableName)};
            |COMMIT;
        """.trimMargin()
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

        val cdcHardDeleteEnabled =
            stream.tableSchema.columnSchema.inputSchema.containsKey(CDC_DELETED_AT_COLUMN)

        // Redshift doesn't support writable CTEs (DELETE/UPDATE inside WITH clauses).
        // Use a session-scoped TEMP TABLE for deduped rows, then run DELETE, UPDATE, INSERT
        // as separate statements. Temp tables are session-scoped so concurrent syncs on
        // different connections cannot collide.
        val dedupTempTable =
            "_airbyte_dedup_${sourceTableName.namespace}_${sourceTableName.name}".toRedshiftCompatibleName()
        val dedupRef = quoteIdentifier(dedupTempTable)

        val selectDedupedQuery =
            selectDeduped(
                primaryKeyTargetColumns,
                cursorTargetColumn,
                allTargetColumns,
                sourceTableName,
            )

        val updateExistingRowsQuery =
            updateExistingRows(
                dedupRef,
                targetTableName,
                allTargetColumns,
                primaryKeyTargetColumns,
                cursorTargetColumn,
                cdcHardDeleteEnabled,
            )

        val insertNewRowsQuery =
            insertNewRows(
                dedupRef,
                targetTableName,
                allTargetColumns,
                primaryKeyTargetColumns,
                cdcHardDeleteEnabled,
            )

        val statements = mutableListOf<String>()

        // Step 1: Materialize deduped rows into a session-scoped temp table
        statements.add("CREATE TEMP TABLE $dedupRef AS\n$selectDedupedQuery;")

        // Step 2: CDC hard-delete (if enabled)
        if (cdcHardDeleteEnabled) {
            val primaryKeysMatchingCondition =
                primaryKeyTargetColumns.joinToString(" AND ") { pk ->
                    "${getFullyQualifiedName(targetTableName)}.$pk = $dedupRef.$pk"
                }
            val cursorComparison =
                buildCursorComparison(cursorTargetColumn, targetTableName, dedupRef)
            statements.add(
                """
                |DELETE FROM ${getFullyQualifiedName(targetTableName)}
                |USING $dedupRef
                |WHERE $primaryKeysMatchingCondition
                |  AND $dedupRef.$DELETED_AT_COLUMN_NAME IS NOT NULL
                |  AND ($cursorComparison);
                """.trimMargin()
            )
        }

        // Step 3: Update existing rows
        statements.add("$updateExistingRowsQuery;")

        // Step 4: Insert new rows
        statements.add("$insertNewRowsQuery;")

        // Step 5: Drop temp table
        statements.add("DROP TABLE IF EXISTS $dedupRef;")

        return """
            |BEGIN TRANSACTION;
            |${statements.joinToString("\n")}
            |COMMIT;
        """.trimMargin()
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
            allTargetColumns
                .filter { it !in primaryKeyTargetColumns }
                .joinToString(",\n    ") { col -> "$col = $dedupTableAlias.$col" }

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
            clauses.add(addColumn(tableName, name, columnType.type))
        }

        // Remove columns
        columnsToRemove.forEach { (name, _) ->
            clauses.add("ALTER TABLE $fqn DROP COLUMN ${quoteIdentifier(name)}$cascadeSuffix;")
        }

        // Modify column types via 4-step rename pattern
        columnsToModify.forEach { (name, typeChange) ->
            clauses.addAll(buildTypeChangeStatements(fqn, name, typeChange))
        }

        return """
            |BEGIN TRANSACTION;
            |${clauses.joinToString("\n")}
            |COMMIT;
        """.trimMargin()
    }

    /**
     * Builds the ALTER TABLE statements to change a column's type in Redshift.
     *
     * The sequence is:
     * 1. ADD a temp column with the new type
     * 2. UPDATE to cast data from the old column into the temp column
     * 3. UPDATE `_airbyte_meta` to record a `DESTINATION_TYPECAST_ERROR` for any row where the
     * ```
     *    original value was non-null but the cast produced null (following the v1 pattern)
     * ```
     * 4. DROP the original column
     * 5. RENAME the temp column to the original name
     */
    private fun buildTypeChangeStatements(
        fullyQualifiedTableName: String,
        columnName: String,
        typeChange: ColumnTypeChange,
    ): List<String> {
        val quotedName = quoteIdentifier(columnName)
        val tempColumn = quoteIdentifier("_airbyte_tmp_$columnName")
        val quotedMeta = quoteIdentifier(COLUMN_NAME_AB_META)
        val oldType = typeChange.originalType.type
        val newType = typeChange.newType.type

        val castExpression =
            when {
                // SUPER -> VARCHAR: serialize JSON to string
                oldType == RedshiftDataType.SUPER.typeName && newType.startsWith("varchar") ->
                    "JSON_SERIALIZE($quotedName)"
                // VARCHAR -> SUPER: parse if valid JSON, otherwise NULL
                oldType.startsWith("varchar") && newType == RedshiftDataType.SUPER.typeName ->
                    "CASE WHEN IS_VALID_JSON($quotedName) OR IS_VALID_JSON_ARRAY($quotedName) THEN JSON_PARSE($quotedName) END"
                // All other conversions: standard CAST
                else -> "CAST($quotedName AS $newType)"
            }

        return buildList {
            // Step 1: Add temp column with the new type
            add("ALTER TABLE $fullyQualifiedTableName ADD COLUMN $tempColumn $newType;")
            // Step 2: Cast data from old column to temp column
            add("UPDATE $fullyQualifiedTableName SET $tempColumn = $castExpression;")
            // Step 3: Record DESTINATION_TYPECAST_ERROR in _airbyte_meta for rows where
            // the original value was non-null but the cast produced null.
            add(
                buildMetaUpdateForTypecastError(
                    fullyQualifiedTableName,
                    quotedName,
                    tempColumn,
                    quotedMeta,
                    columnName
                )
            )
            // Step 4: Drop the original column
            add("ALTER TABLE $fullyQualifiedTableName DROP COLUMN $quotedName$cascadeSuffix;")
            // Step 5: Rename temp column to the original name
            add("ALTER TABLE $fullyQualifiedTableName RENAME COLUMN $tempColumn TO $quotedName;")
        }
    }

    /**
     * Builds an UPDATE statement that appends a DESTINATION_TYPECAST_ERROR change entry to
     * `_airbyte_meta.changes` for rows where the original column was non-null but the cast into the
     * temp column produced null.
     */
    private fun buildMetaUpdateForTypecastError(
        fullyQualifiedTableName: String,
        quotedOriginalColumn: String,
        quotedTempColumn: String,
        quotedMeta: String,
        columnName: String,
    ): String {
        val changeEntry =
            """{"field":"$columnName","change":"NULLED","reason":"DESTINATION_TYPECAST_ERROR"}"""
        return """
            |UPDATE $fullyQualifiedTableName
            |SET $quotedMeta = OBJECT(
            |    'sync_id', $quotedMeta."sync_id",
            |    'changes', ARRAY_CONCAT(
            |        COALESCE($quotedMeta."changes", ARRAY()),
            |        ARRAY(JSON_PARSE('$changeEntry'))
            |    )
            |)
            |WHERE $quotedOriginalColumn IS NOT NULL
            |AND $quotedTempColumn IS NULL;
        """.trimMargin()
    }

    /** Generates a query to retrieve column metadata from `information_schema.columns` */
    fun getTableSchema(tableName: TableName): String =
        """
            |SELECT column_name, data_type, is_nullable
            |FROM information_schema.columns
            |WHERE table_schema = '${RedshiftSqlEscapeUtils.escapeSqlString(tableName.namespace)}'
            |AND table_name = '${RedshiftSqlEscapeUtils.escapeSqlString(tableName.name)}'
            |ORDER BY ordinal_position;
        """.trimMargin()

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
            |ROUNDEC
            |IGNOREHEADER 1
            |EMPTYASNULL;
        """.trimMargin()

    // ================================================================
    // Internal helpers
    // ================================================================

    /** Returns the user columns (non-meta) from the stream's pre-computed table schema. */
    private fun getUserColumns(stream: DestinationStream): Map<String, ColumnType> =
        stream.tableSchema.columnSchema.finalSchema

    /** Builds the fully qualified table name as `"namespace"."name"`. */
    fun getFullyQualifiedName(tableName: TableName): String =
        "${getNamespace(tableName)}.${getName(tableName)}"

    private fun getNamespace(tableName: TableName): String = quoteIdentifier(tableName.namespace)

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
}
