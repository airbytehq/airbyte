/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.sql

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.ColumnTypeChange
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.redshift_v2.schema.toRedshiftCompatibleName
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2Configuration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.UUID

private val log = KotlinLogging.logger {}

internal const val COUNT_TOTAL_ALIAS = "total"

/** Extension to log SQL statements before returning them. */
fun String.andLog(): String {
    log.info { this.trim() }
    return this
}

@Singleton
class RedshiftSqlGenerator(
    private val columnUtils: RedshiftColumnUtils,
    private val sqlNameUtils: RedshiftSqlNameUtils,
    private val config: RedshiftV2Configuration,
) {
    // Hard delete is always enabled for CDC - Redshift supports it
    private val hardDeleteEnabled: Boolean = true
    // ========================================
    // NAMESPACE OPERATIONS
    // ========================================

    fun createNamespace(namespace: String): String {
        return "CREATE SCHEMA IF NOT EXISTS ${sqlNameUtils.fullyQualifiedNamespace(namespace)}".andLog()
    }

    fun namespaceExists(namespace: String): String {
        return """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name = '$namespace'
        """
            .trimIndent()
            .andLog()
    }

    // ========================================
    // TABLE OPERATIONS
    // ========================================

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

        // Redshift doesn't support CREATE OR REPLACE TABLE, so we need to drop first if
        // replace=true
        val createStatement =
            if (replace) {
                """
                DROP TABLE IF EXISTS ${sqlNameUtils.fullyQualifiedName(tableName)};
                CREATE TABLE ${sqlNameUtils.fullyQualifiedName(tableName)} (
                    $columnDeclarations
                )
            """.trimIndent()
            } else {
                """
                CREATE TABLE IF NOT EXISTS ${sqlNameUtils.fullyQualifiedName(tableName)} (
                    $columnDeclarations
                )
            """.trimIndent()
            }

        return createStatement.andLog()
    }

    fun dropTable(tableName: TableName): String {
        val cascadeModifier = if (config.dropCascade) "CASCADE" else ""
        return "DROP TABLE IF EXISTS ${sqlNameUtils.fullyQualifiedName(tableName)}$cascadeModifier".andLog()
    }

    fun countTable(tableName: TableName): String {
        return "SELECT COUNT(*) AS $COUNT_TOTAL_ALIAS FROM ${sqlNameUtils.fullyQualifiedName(tableName)}".andLog()
    }

    fun getGenerationId(tableName: TableName): String {
        return """
            SELECT "${columnUtils.getGenerationIdColumnName()}"
            FROM ${sqlNameUtils.fullyQualifiedName(tableName)}
            LIMIT 1
        """
            .trimIndent()
            .andLog()
    }

    // ========================================
    // SCHEMA INTROSPECTION
    // ========================================

    fun describeTable(schemaName: String, tableName: String): String {
        return """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = '$schemaName'
              AND table_name = '$tableName'
            ORDER BY ordinal_position
        """
            .trimIndent()
            .andLog()
    }

    // ========================================
    // TABLE MANIPULATION (for later phases)
    // ========================================

    fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        val columnNames = columnUtils.getColumnNames(columnNameMapping)

        return """
            INSERT INTO ${sqlNameUtils.fullyQualifiedName(targetTableName)}
            ($columnNames)
            SELECT $columnNames
            FROM ${sqlNameUtils.fullyQualifiedName(sourceTableName)}
        """
            .trimIndent()
            .andLog()
    }

    fun renameTable(sourceTableName: TableName, targetTableName: TableName): String {
        return """
            ALTER TABLE ${sqlNameUtils.fullyQualifiedName(sourceTableName)}
            RENAME TO ${targetTableName.name.quote()}
        """
            .trimIndent()
            .andLog()
    }

    /**
     * Move data from source table to target table using ALTER TABLE APPEND. This is used for
     * cross-schema table moves since Redshift doesn't support ALTER TABLE SET SCHEMA.
     *
     * ALTER TABLE APPEND moves rows from source to target table (source becomes empty). It's much
     * faster than INSERT...SELECT for large tables.
     */
    fun appendTable(sourceTableName: TableName, targetTableName: TableName): String {
        return """
            ALTER TABLE ${sqlNameUtils.fullyQualifiedName(targetTableName)}
            APPEND FROM ${sqlNameUtils.fullyQualifiedName(sourceTableName)}
        """
            .trimIndent()
            .andLog()
    }

    /** Create a table with the same schema as an existing table. */
    fun createTableLike(sourceTableName: TableName, targetTableName: TableName): String {
        return """
            CREATE TABLE ${sqlNameUtils.fullyQualifiedName(targetTableName)}
            (LIKE ${sqlNameUtils.fullyQualifiedName(sourceTableName)})
        """
            .trimIndent()
            .andLog()
    }

    // ========================================
    // UPSERT / DEDUPE OPERATIONS
    // ========================================

    /**
     * Generate SQL statements for upsert (merge) operation. Redshift doesn't have native MERGE, so
     * we use DELETE + INSERT pattern:
     * 1. Delete from target where primary key matches source (and source record is newer)
     * 2. Insert deduped records from source
     *
     * For CDC with hard delete: also delete records where _ab_cdc_deleted_at is not null.
     */
    fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): List<String> {
        val importType = stream.importType as Dedupe
        val statements = mutableListOf<String>()

        val targetTable = sqlNameUtils.fullyQualifiedName(targetTableName)
        // For DELETE...USING, Redshift doesn't support table aliases in the DELETE clause
        // We need to use the actual table name for column references
        val targetTableRef = targetTable

        // Build column list for SELECT and INSERT
        val columnList =
            columnUtils
                .getFormattedColumnNames(
                    columns = stream.schema.asColumns(),
                    columnNameMapping = columnNameMapping,
                    quote = true,
                )
                .joinToString(",\n")

        // Build primary key matching condition (use actual table name, not alias)
        val pkCondition =
            if (importType.primaryKey.isNotEmpty()) {
                importType.primaryKey.joinToString(" AND ") { fieldPath ->
                    val fieldName = fieldPath.first()
                    val columnName = (columnNameMapping[fieldName] ?: fieldName).quote()
                    """($targetTableRef.$columnName = deduped.$columnName OR ($targetTableRef.$columnName IS NULL AND deduped.$columnName IS NULL))"""
                }
            } else {
                throw IllegalArgumentException("Cannot perform upsert without primary key")
            }

        // Build cursor comparison for determining which record is newer
        val extractedAtColumn = COLUMN_NAME_AB_EXTRACTED_AT.toRedshiftCompatibleName().quote()
        val cursorComparison: String =
            if (importType.cursor.isNotEmpty()) {
                val cursorFieldName = importType.cursor.first()
                val cursor = (columnNameMapping[cursorFieldName] ?: cursorFieldName).quote()
                """
                (
                  $targetTableRef.$cursor < deduped.$cursor
                  OR ($targetTableRef.$cursor = deduped.$cursor AND $targetTableRef.$extractedAtColumn < deduped.$extractedAtColumn)
                  OR ($targetTableRef.$cursor IS NULL AND deduped.$cursor IS NULL AND $targetTableRef.$extractedAtColumn < deduped.$extractedAtColumn)
                  OR ($targetTableRef.$cursor IS NULL AND deduped.$cursor IS $NOT_NULL)
                )
            """.trimIndent()
            } else {
                // No cursor - use extraction timestamp only
                """$targetTableRef.$extractedAtColumn < deduped.$extractedAtColumn"""
            }

        // Get deduped records from source as a CTE
        val dedupedRecordsCte = selectDedupedRecords(stream, sourceTableName, columnNameMapping)

        // Check if CDC deletion is needed
        val hasCdcColumn = stream.schema.asColumns().containsKey(CDC_DELETED_AT_COLUMN)
        val cdcDeletedAtColumn = CDC_DELETED_AT_COLUMN.toRedshiftCompatibleName().quote()

        // Step 1: Handle CDC hard deletes (if applicable)
        if (hasCdcColumn && hardDeleteEnabled) {
            statements.add(
                """
                WITH $dedupedRecordsCte
                DELETE FROM $targetTable
                USING deduped
                WHERE $pkCondition
                  AND deduped.$cdcDeletedAtColumn IS NOT NULL
                  AND $cursorComparison
            """
                    .trimIndent()
                    .andLog()
            )
        }

        // Step 2: Delete existing records that will be updated by newer records
        // (This handles the "matched and newer" case)
        statements.add(
            """
            WITH $dedupedRecordsCte
            DELETE FROM $targetTable
            USING deduped
            WHERE $pkCondition
              AND $cursorComparison
              ${if (hasCdcColumn && hardDeleteEnabled) "AND deduped.$cdcDeletedAtColumn IS NULL" else ""}
        """
                .trimIndent()
                .andLog()
        )

        // Step 3: Insert deduped records (excluding CDC deleted records if hard delete is enabled)
        // Redshift doesn't support WITH...INSERT directly, use subquery instead
        val insertFilter =
            if (hasCdcColumn && hardDeleteEnabled) {
                "WHERE $cdcDeletedAtColumn IS NULL"
            } else {
                ""
            }

        // Use a subquery for deduplication since Redshift doesn't support WITH...INSERT
        val dedupedSubquery =
            selectDedupedRecordsSubquery(stream, sourceTableName, columnNameMapping)

        statements.add(
            """
            INSERT INTO $targetTable ($columnList)
            SELECT $columnList
            FROM ($dedupedSubquery) deduped
            $insertFilter
        """
                .trimIndent()
                .andLog()
        )

        return statements
    }

    /**
     * Generates a CTE (Common Table Expression) that extracts and deduplicates records from the
     * source table. Uses ROW_NUMBER() window function to select the most recent record per primary
     * key.
     *
     * Returns the CTE definition without the WITH keyword (caller adds WITH).
     */
    private fun selectDedupedRecords(
        stream: DestinationStream,
        sourceTableName: TableName,
        columnNameMapping: ColumnNameMapping
    ): String {
        val columnList =
            columnUtils
                .getFormattedColumnNames(
                    columns = stream.schema.asColumns(),
                    columnNameMapping = columnNameMapping,
                    quote = true,
                )
                .joinToString(",\n")

        val importType = stream.importType as Dedupe

        // Build the primary key list for partitioning
        val pkList =
            if (importType.primaryKey.isNotEmpty()) {
                importType.primaryKey.joinToString(",") { fieldPath ->
                    (columnNameMapping[fieldPath.first()] ?: fieldPath.first()).quote()
                }
            } else {
                throw IllegalArgumentException("Cannot deduplicate without primary key")
            }

        // Build cursor order clause for sorting within each partition
        val extractedAtColumn = COLUMN_NAME_AB_EXTRACTED_AT.toRedshiftCompatibleName().quote()
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
            deduped AS (
              SELECT $columnList
              FROM (
                SELECT
                  $columnList,
                  ROW_NUMBER() OVER (
                    PARTITION BY $pkList ORDER BY $cursorOrderClause $extractedAtColumn DESC
                  ) AS row_number
                FROM ${sqlNameUtils.fullyQualifiedName(sourceTableName)}
              ) numbered_rows
              WHERE row_number = 1
            )
        """.trimIndent()
    }

    /**
     * Generates a subquery (not CTE) that extracts and deduplicates records from the source table.
     * Used for INSERT statements since Redshift doesn't support WITH...INSERT directly.
     */
    private fun selectDedupedRecordsSubquery(
        stream: DestinationStream,
        sourceTableName: TableName,
        columnNameMapping: ColumnNameMapping
    ): String {
        val columnList =
            columnUtils
                .getFormattedColumnNames(
                    columns = stream.schema.asColumns(),
                    columnNameMapping = columnNameMapping,
                    quote = true,
                )
                .joinToString(",\n")

        val importType = stream.importType as Dedupe

        // Build the primary key list for partitioning
        val pkList =
            if (importType.primaryKey.isNotEmpty()) {
                importType.primaryKey.joinToString(",") { fieldPath ->
                    (columnNameMapping[fieldPath.first()] ?: fieldPath.first()).quote()
                }
            } else {
                throw IllegalArgumentException("Cannot deduplicate without primary key")
            }

        // Build cursor order clause for sorting within each partition
        val extractedAtColumn = COLUMN_NAME_AB_EXTRACTED_AT.toRedshiftCompatibleName().quote()
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
            SELECT $columnList
            FROM (
              SELECT
                $columnList,
                ROW_NUMBER() OVER (
                  PARTITION BY $pkList ORDER BY $cursorOrderClause $extractedAtColumn DESC
                ) AS row_number
              FROM ${sqlNameUtils.fullyQualifiedName(sourceTableName)}
            ) numbered_rows
            WHERE row_number = 1
        """.trimIndent()
    }

    // ========================================
    // SCHEMA EVOLUTION
    // ========================================

    /**
     * Generate SQL statements to alter a table's schema. Returns a set of SQL statements to be
     * executed in order.
     *
     * For type changes, we use the add-copy-rename-drop pattern since Redshift doesn't support
     * direct ALTER COLUMN TYPE for all type combinations.
     */
    fun alterTable(
        tableName: TableName,
        addedColumns: Map<String, ColumnType>,
        deletedColumns: Map<String, ColumnType>,
        modifiedColumns: Map<String, ColumnTypeChange>,
    ): List<String> {
        val statements = mutableListOf<String>()
        val prettyTableName = sqlNameUtils.fullyQualifiedName(tableName)

        // Add new columns
        addedColumns.forEach { (name, columnType) ->
            // Add as nullable since we don't know what default value to use for existing records
            statements.add(
                "ALTER TABLE $prettyTableName ADD COLUMN ${name.quote()} ${columnType.type}".andLog()
            )
        }

        // Drop columns
        deletedColumns.forEach { (name, _) ->
            statements.add("ALTER TABLE $prettyTableName DROP COLUMN ${name.quote()}".andLog())
        }

        // Modify column types using add-copy-rename-drop pattern
        modifiedColumns.forEach { (name, typeChange) ->
            if (typeChange.originalType.type != typeChange.newType.type) {
                // Generate a unique temp column name
                val tempColumn = "${name}_${UUID.randomUUID().toString().replace("-", "").take(8)}"
                val backupColumn = "${tempColumn}_backup"

                // 1. Add temp column with new type
                statements.add(
                    "ALTER TABLE $prettyTableName ADD COLUMN ${tempColumn.quote()} ${typeChange.newType.type}".andLog()
                )

                // 2. Copy/cast data from old column to temp column
                // Use CAST for type conversion
                statements.add(
                    "UPDATE $prettyTableName SET ${tempColumn.quote()} = CAST(${name.quote()} AS ${typeChange.newType.type})".andLog()
                )

                // 3. Rename old column to backup
                statements.add(
                    "ALTER TABLE $prettyTableName RENAME COLUMN ${name.quote()} TO ${backupColumn.quote()}".andLog()
                )

                // 4. Rename temp column to original name
                statements.add(
                    "ALTER TABLE $prettyTableName RENAME COLUMN ${tempColumn.quote()} TO ${name.quote()}".andLog()
                )

                // 5. Drop backup column
                statements.add(
                    "ALTER TABLE $prettyTableName DROP COLUMN ${backupColumn.quote()}".andLog()
                )
            } else if (!typeChange.originalType.nullable && typeChange.newType.nullable) {
                // Only changing nullability from NOT NULL to nullable
                // Redshift supports ALTER COLUMN ... DROP NOT NULL
                statements.add(
                    "ALTER TABLE $prettyTableName ALTER COLUMN ${name.quote()} DROP NOT NULL".andLog()
                )
            }
            // Note: We don't change from nullable to NOT NULL because existing records may have
            // nulls
        }

        return statements
    }
}
