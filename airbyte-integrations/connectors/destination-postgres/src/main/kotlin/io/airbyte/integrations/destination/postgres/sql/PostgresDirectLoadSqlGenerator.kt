/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.sql

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.table.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.postgres.spec.CdcDeletionMode
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlin.collections.forEach

internal const val COUNT_TOTAL_ALIAS = "total"

private val log = KotlinLogging.logger {}

@Singleton
class PostgresDirectLoadSqlGenerator(
    private val postgresConfiguration: PostgresConfiguration
) {
    companion object {
        private const val CURSOR_INDEX_PREFIX = "idx_cursor_"
        private const val PRIMARY_KEY_INDEX_PREFIX = "idx_pk_"
        private const val DEDUPED_TABLE_ALIAS = "deduped_source"
        internal val DEFAULT_COLUMNS =
            listOf(
                Column(
                    columnName = COLUMN_NAME_AB_RAW_ID,
                    columnTypeName = PostgresDataType.VARCHAR.typeName,
                    nullable = false

                ),
                Column(
                    columnName = COLUMN_NAME_AB_EXTRACTED_AT,
                    columnTypeName = PostgresDataType.TIMESTAMP_WITH_TIMEZONE.typeName,
                    nullable = false
                ),
                Column(
                    columnName = COLUMN_NAME_AB_META,
                    columnTypeName = PostgresDataType.JSONB.typeName,
                    nullable = false
                ),
                Column(
                    columnName = COLUMN_NAME_AB_GENERATION_ID,
                    columnTypeName = PostgresDataType.BIGINT.typeName,
                    nullable = false
                ),
            )

        /**
         * This extension is here to avoid writing `.also { log.info { it }}` for every returned string
         * we want to log
         */
        fun String.andLog(): String {
            log.info { this.trim() }
            return this
        }
    }

    fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ): String {
        val columnDeclarations = columnsAndTypes(stream, columnNameMapping).joinToString(",\n") {it.toSQLString() }
        val dropTableIfExistsStatement = if (replace) "DROP TABLE IF EXISTS ${getFullyQualifiedName(tableName)};" else ""
        val createIndexesStatement = createIndexes(stream, tableName, columnNameMapping)
        return """
            BEGIN TRANSACTION;
            $dropTableIfExistsStatement
            CREATE TABLE ${getFullyQualifiedName(tableName)} (
                $columnDeclarations
            );
            $createIndexesStatement
            COMMIT;
            """
            .trimIndent()
            .andLog()
    }

    private fun createIndexes(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ): String {
        val primaryKeyIndexStatement = getPrimaryKeysColumnNames(stream, columnNameMapping)
            .takeIf {  it.isNotEmpty() }
            ?.let {
                "CREATE INDEX ${getPrimaryKeyIndexName(tableName)} ON ${getFullyQualifiedName(tableName)} (${it.joinToString(", ")});"
            } ?: ""

        val cursorIndexStatement = getCursorColumnName(stream, columnNameMapping)?.let { cursorColumnName ->
            "CREATE INDEX ${getCursorIndexName(tableName)} ON ${getFullyQualifiedName(tableName)} ($cursorColumnName);"
        } ?: ""

        val extractedAtIndexStatement = "CREATE INDEX ON ${getFullyQualifiedName(tableName)} (${getExtractedAtColumnName()});"

        return """
            $primaryKeyIndexStatement
            $cursorIndexStatement
            $extractedAtIndexStatement
        """.trimIndent()
    }

    private fun getPrimaryKeysColumnNames(stream: DestinationStream, columnNameMapping: ColumnNameMapping): List<String> {
        return when (stream.importType) {
            is Dedupe -> getPrimaryKeysColumnNames(stream.importType as Dedupe, columnNameMapping)
            else -> listOf()
        }
    }

    private fun getPrimaryKeysColumnNames(
        importType: Dedupe,
        columnNameMapping: ColumnNameMapping
    ): List<String> {
        return importType.primaryKey.map { fieldPath ->
            val primaryKeyColumnName = fieldPath.first() //only at the root level for Postgres
            val targetColumnName = getTargetColumnName(primaryKeyColumnName, columnNameMapping)
            "\"$targetColumnName\""
        }.toList()
    }

    private fun getCursorColumnName(
        cursor: List<String>,
        columnNameMapping: ColumnNameMapping
    ): String? {
        return cursor
            .firstOrNull()
            ?.let { columnName -> getQuotedTargetColumnName(columnName, columnNameMapping) }
    }

    private fun getCursorColumnName(stream: DestinationStream, columnNameMapping: ColumnNameMapping): String? {
        when (stream.importType) {
            is Dedupe -> return getCursorColumnName((stream.importType as Dedupe).cursor, columnNameMapping)
            else -> return null
        }
    }

    private fun getPrimaryKeyIndexName(tableName: TableName): String =
        "\"${PRIMARY_KEY_INDEX_PREFIX + tableName.name}\""

    private fun getCursorIndexName(tableName: TableName): String =
        "\"${CURSOR_INDEX_PREFIX + tableName.name}\""

    private fun getExtractedAtColumnName(): String =
        "\"$COLUMN_NAME_AB_EXTRACTED_AT\""

    private fun getDeletedAtColumnName(): String =
        "\"$CDC_DELETED_AT_COLUMN\""

    fun columnsAndTypes(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): List<Column> {
        val targetColumns = stream.schema
            .asColumns()
            .map { (columnName, columnType) ->
                val targetColumnName = getTargetColumnName(columnName, columnNameMapping)
                val typeName = columnType.type.toDialectType()
                Column(
                    columnName = targetColumnName,
                    columnTypeName = typeName,
                )
            }
            .toList()

        return (DEFAULT_COLUMNS + targetColumns)
    }

    fun overwriteTable(
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        return """
            BEGIN TRANSACTION;
            DROP TABLE IF EXISTS ${getFullyQualifiedName(targetTableName)};
            ALTER TABLE ${getFullyQualifiedName(sourceTableName)} RENAME TO ${getName(targetTableName)};
            COMMIT;
            """
            .trimIndent()
            .andLog()
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
            .trimIndent()
            .andLog()
    }

    private fun getTargetColumnNames(stream: DestinationStream, columnNameMapping: ColumnNameMapping): List<String> {
        return columnsAndTypes(stream, columnNameMapping).map { getQuotedTargetColumnName(it.columnName, columnNameMapping) }
    }

    private fun getTargetColumnNames(columnNameMapping: ColumnNameMapping): List<String> =
        getDefaultColumnNames() + columnNameMapping.map { (_, targetName) -> "\"${targetName}\"" }

    private fun getTargetColumnName(streamColumnName : String, columnNameMapping: ColumnNameMapping): String =
        columnNameMapping[streamColumnName] ?: streamColumnName

    private fun getQuotedTargetColumnName(streamColumnName: String, columnNameMapping: ColumnNameMapping): String {
        return "\"${getTargetColumnName(streamColumnName, columnNameMapping)}\""
    }

    fun getDefaultColumnNames(): List<String> =
        DEFAULT_COLUMNS.map { "\"${it.columnName}\"" }

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

        val selectDedupedQuery = selectDeduped(primaryKeyTargetColumns, cursorTargetColumn, allTargetColumns, sourceTableName)

        val cdcHardDeleteEnabled =  stream.schema.asColumns().containsKey(CDC_DELETED_AT_COLUMN) &&
            postgresConfiguration.cdcDeletionMode == CdcDeletionMode.HARD_DELETE

        val cdcDeleteQuery = cdcDelete(
            DEDUPED_TABLE_ALIAS,
            cursorTargetColumn,
            targetTableName,
            primaryKeyTargetColumns,
            cdcHardDeleteEnabled
        )

        val updateExistingRowsQuery = updateExistingRows(
            DEDUPED_TABLE_ALIAS,
            targetTableName,
            allTargetColumns,
            primaryKeyTargetColumns,
            cursorTargetColumn,
            cdcHardDeleteEnabled
        )

        val insertNewRowsQuery = insertNewRows(
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
            """.trimIndent().andLog()
    }

    internal fun insertNewRows(
        dedupTableAlias: String,
        targetTableName: TableName,
        allTargetColumns: List<String>,
        primaryKeyTargetColumns: List<String>,
        cdcHardDeleteEnabled: Boolean
    ): String {
        val pkConditions = primaryKeyTargetColumns.joinToString(" AND ") { pk ->
            "${getFullyQualifiedName(targetTableName)}.$pk = $dedupTableAlias.$pk"
        }

        val skipCdcDeletedClause = if(cdcHardDeleteEnabled) "AND $dedupTableAlias.${getDeletedAtColumnName()} IS NULL" else ""

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
                WHERE $pkConditions
              )
              $skipCdcDeletedClause
        """.trimIndent()
    }

    internal fun updateExistingRows(dedupTableAlias: String,
                                   targetTableName: TableName,
                                   allTargetColumns: List<String>,
                                   primaryKeyTargetColumns: List<String>,
                                   cursorTargetColumn: String?,
                                   cdcHardDeleteEnabled: Boolean): String {
        val primaryKeysMatches = primaryKeyTargetColumns.joinToString(" AND ") { pk ->
            "${getFullyQualifiedName(targetTableName)}.$pk = $dedupTableAlias.$pk"
        }

        val cursorComparison = buildCursorComparison(cursorTargetColumn, targetTableName, dedupTableAlias)

        val updateAssignments =
            allTargetColumns.joinToString(",\n") { columnName ->
                "$columnName = $dedupTableAlias.$columnName"
            }

        val skipCdcDeletedClause = if(cdcHardDeleteEnabled) "AND $dedupTableAlias.${getDeletedAtColumnName()} IS NULL" else ""
        return """
             UPDATE ${getFullyQualifiedName(targetTableName)}
             SET 
                $updateAssignments
             FROM $dedupTableAlias
                WHERE $primaryKeysMatches
                    $skipCdcDeletedClause
                    AND ($cursorComparison)
        """.trimIndent()
    }

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

        val primaryKeysMatchingCondition = primaryKeyTargetColumns.joinToString(" AND ") { pk ->
            "${getFullyQualifiedName(targetTableName)}.$pk = $dedupTableAlias.$pk"
        }

        // ensure we only delete if the deletion is newer
        val cursorComparison = buildCursorComparison(cursorTargetColumn, targetTableName, dedupTableAlias)

        val deleteStatement = """
            DELETE FROM ${getFullyQualifiedName(targetTableName)}
            USING $dedupTableAlias
            WHERE $primaryKeysMatchingCondition
                AND $dedupTableAlias.${getDeletedAtColumnName()} IS NOT NULL
                AND ($cursorComparison)
        """.trimIndent()

        return """
            deleted AS (
            $deleteStatement
            ),
        """.trimIndent()
    }

    private fun buildCursorComparison(
        cursorTargetColumn: String?,
        targetTableName: TableName,
        dedupTableAlias: String
    ): String {
        return if (cursorTargetColumn != null) {
            val extractedAtColumn = getExtractedAtColumnName()
            """
                  ${getFullyQualifiedName(targetTableName)}.$cursorTargetColumn < $dedupTableAlias.$cursorTargetColumn
                  OR (${getFullyQualifiedName(targetTableName)}.$cursorTargetColumn = $dedupTableAlias.$cursorTargetColumn AND ${getFullyQualifiedName(targetTableName)}.$extractedAtColumn < $dedupTableAlias.$extractedAtColumn)
                  OR (${getFullyQualifiedName(targetTableName)}.$cursorTargetColumn IS NULL AND $dedupTableAlias.$cursorTargetColumn IS NOT NULL)
                  OR (${getFullyQualifiedName(targetTableName)}.$cursorTargetColumn IS NULL AND $dedupTableAlias.$cursorTargetColumn IS NULL AND ${getFullyQualifiedName(targetTableName)}.$extractedAtColumn < $dedupTableAlias.$extractedAtColumn)
                """.trimIndent()
        } else {
            // No cursor - use extraction timestamp only
            val extractedAtColumn = getExtractedAtColumnName()
            "${getFullyQualifiedName(targetTableName)}.$extractedAtColumn < $dedupTableAlias.$extractedAtColumn"
        }
    }

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
                    $cursorOrderClause ${getExtractedAtColumnName()} DESC
                ) AS row_number
              FROM ${getFullyQualifiedName(sourceTableName)}
            ) AS deduplicated
            WHERE row_number = 1
        """.trimIndent()
    }

    fun dropTable(tableName: TableName): String =
        "DROP TABLE IF EXISTS ${getFullyQualifiedName(tableName)};".andLog()

    fun countTable(tableName: TableName): String {
        return "SELECT COUNT(*) AS \"$COUNT_TOTAL_ALIAS\" FROM ${getFullyQualifiedName(tableName)};".andLog()
    }

    fun createNamespace(namespace: String): String {
        return "CREATE SCHEMA IF NOT EXISTS \"$namespace\";".andLog()
    }

    fun getGenerationId(tableName: TableName): String =
        "SELECT \"${COLUMN_NAME_AB_GENERATION_ID}\" FROM ${getFullyQualifiedName(tableName)} LIMIT 1;".andLog()

    fun getTableSchema(tableName: TableName): String =
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = '${tableName.namespace}'
        AND table_name = '${tableName.name}';
        """.trimIndent().andLog()

    fun copyFromCsv(tableName: TableName): String =
        """
        COPY "${tableName.namespace}"."${tableName.name}"
        FROM STDIN
        WITH (FORMAT csv)
        """.trimIndent()

    //should all alters happen in one same tx? probably
    fun matchSchemas(
        tableName: TableName,
        columnsToAdd: Set<Column>,
        columnsToRemove: Set<Column>,
        columnsToModify: Set<Column>,
    ): Set<String> {
        val clauses = mutableSetOf<String>()
        val fullyQualifiedTableName = getFullyQualifiedName(tableName)
        columnsToAdd.forEach {
            clauses.add(
                "ALTER TABLE $fullyQualifiedTableName ADD COLUMN ${getName(it)} ${it.columnTypeName};".andLog()
            )
        }
        columnsToRemove.forEach {
            clauses.add("ALTER TABLE $fullyQualifiedTableName DROP COLUMN ${getName(it)};".andLog())
        }

        columnsToModify.forEach {
            clauses.add("ALTER TABLE $fullyQualifiedTableName ALTER COLUMN ${getName(it)} SET DATA TYPE ${it.columnTypeName};".andLog())
        }
        return clauses
    }

    private fun getFullyQualifiedName(tableName: TableName): String =
        "${getNamespace(tableName)}.${getName(tableName)}"

    private fun getNamespace(tableName: TableName): String =
        "\"${tableName.namespace}\""

    private fun getName(tableName: TableName): String =
        "\"${tableName.name}\""

    private fun getName(column: Column): String =
        "\"${column.columnName}\""

    fun AirbyteType.toDialectType(): String =
        when (this) {
            BooleanType -> PostgresDataType.BOOLEAN.typeName
            DateType -> PostgresDataType.DATE.typeName
            IntegerType -> PostgresDataType.BIGINT.typeName
            NumberType -> PostgresDataType.DECIMAL.typeName
            StringType -> PostgresDataType.VARCHAR.typeName
            TimeTypeWithTimezone -> PostgresDataType.TIME_WITH_TIMEZONE.typeName
            TimeTypeWithoutTimezone -> PostgresDataType.TIME.typeName
            TimestampTypeWithTimezone -> PostgresDataType.TIMESTAMP_WITH_TIMEZONE.typeName
            TimestampTypeWithoutTimezone -> PostgresDataType.TIMESTAMP.typeName
            is ArrayType,
            ArrayTypeWithoutSchema,
            is ObjectType,
            ObjectTypeWithEmptySchema,
            ObjectTypeWithoutSchema,
            is UnknownType,
            is UnionType -> PostgresDataType.JSONB.typeName
        }

    fun Column.toSQLString(): String {
        val isNullableSuffix = if (nullable) "" else "NOT NULL"
        return "\"$columnName\" $columnTypeName $isNullableSuffix".trim()
    }
}

data class Column(val columnName: String, val columnTypeName: String, val nullable: Boolean = true)
