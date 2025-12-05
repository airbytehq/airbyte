/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.client

import com.clickhouse.data.ClickHouseDataType
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
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
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.clickhouse.client.ClickhouseSqlGenerator.Companion.DATETIME_WITH_PRECISION
import io.airbyte.integrations.destination.clickhouse.client.ClickhouseSqlGenerator.Companion.DECIMAL_WITH_PRECISION_AND_SCALE
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

@Singleton
class ClickhouseSqlGenerator(
    val clickhouseConfiguration: ClickhouseConfiguration,
) {
    private val log = KotlinLogging.logger {}

    /**
     * This extension is here to avoid writing `.also { log.info { it }}` for every returned string
     * we want to log
     */
    private fun String.andLog(): String {
        log.info { this }
        return this
    }

    private fun isValidVersionColumnType(airbyteType: AirbyteType): Boolean {
        // Must be of an integer type or of type Date/DateTime/DateTime64
        return VALID_VERSION_COLUMN_TYPES.any { it.isInstance(airbyteType) }
    }

    fun createNamespace(namespace: String): String {
        return "CREATE DATABASE IF NOT EXISTS `$namespace`;".andLog()
    }

    fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    ): String {
        val pks: List<String> =
            when (stream.importType) {
                is Dedupe -> extractPks((stream.importType as Dedupe).primaryKey, columnNameMapping)
                else -> listOf()
            }

        // For ReplacingMergeTree, we need to make the cursor column non-nullable if it's used as
        // version column. We'll also determine here if we need to fall back to extracted_at.
        var useCursorAsVersionColumn = false
        val nonNullableColumns =
            mutableSetOf<String>().apply {
                addAll(pks) // Primary keys are always non-nullable
                if (stream.importType is Dedupe) {
                    val dedupeType = stream.importType as Dedupe
                    if (dedupeType.cursor.isNotEmpty()) {
                        val cursorFieldName = dedupeType.cursor.first()
                        val cursorColumnName = columnNameMapping[cursorFieldName] ?: cursorFieldName

                        // Check if the cursor column type is valid for ClickHouse
                        // ReplacingMergeTree
                        val cursorColumnType = stream.schema.asColumns()[cursorFieldName]?.type
                        if (
                            cursorColumnType != null && isValidVersionColumnType(cursorColumnType)
                        ) {
                            // Cursor column is valid, use it as version column
                            add(cursorColumnName) // Make cursor column non-nullable too
                            useCursorAsVersionColumn = true
                        } else {
                            // Cursor column is invalid, we'll fall back to _airbyte_extracted_at
                            log.warn {
                                "Cursor column '$cursorFieldName' for stream '${stream.mappedDescriptor}' has type '${cursorColumnType?.let { it::class.simpleName }}' which is not valid for use as a version column in ClickHouse ReplacingMergeTree. " +
                                    "Falling back to using _airbyte_extracted_at as version column. Valid types are: Integer, Date, Timestamp."
                            }
                            useCursorAsVersionColumn = false
                        }
                    }
                    // If no cursor is specified or cursor is invalid, we'll use
                    // _airbyte_extracted_at
                    // as version column, which is already non-nullable by default (defined in
                    // CREATE TABLE statement)
                }
            }

        val columnDeclarations =
            columnsAndTypes(stream, columnNameMapping, nonNullableColumns.toList())

        val forceCreateTable = if (replace) "OR REPLACE" else ""

        val pksAsString =
            pks.joinToString(",") {
                // Escape the columns
                "`$it`"
            }

        val engine =
            when (stream.importType) {
                is Dedupe -> {
                    val dedupeType = stream.importType as Dedupe
                    // Use cursor column as version column for ReplacingMergeTree if available and
                    // valid
                    val versionColumn =
                        if (dedupeType.cursor.isNotEmpty() && useCursorAsVersionColumn) {
                            val cursorFieldName = dedupeType.cursor.first()
                            val cursorColumnName =
                                columnNameMapping[cursorFieldName] ?: cursorFieldName
                            "`$cursorColumnName`"
                        } else {
                            // Fallback to _airbyte_extracted_at if no cursor is specified or cursor
                            // is invalid
                            COLUMN_NAME_AB_EXTRACTED_AT
                        }
                    "ReplacingMergeTree($versionColumn)"
                }
                else -> "MergeTree()"
            }

        return """
            CREATE $forceCreateTable TABLE `${tableName.namespace}`.`${tableName.name}` (
              $COLUMN_NAME_AB_RAW_ID String NOT NULL,
              $COLUMN_NAME_AB_EXTRACTED_AT DateTime64(3) NOT NULL,
              $COLUMN_NAME_AB_META String NOT NULL,
              $COLUMN_NAME_AB_GENERATION_ID UInt32 NOT NULL,
              $columnDeclarations
            )
            ENGINE = ${engine}
            ORDER BY (${if (pks.isEmpty()) {
            "$COLUMN_NAME_AB_RAW_ID"
        } else {
            pksAsString
        }})
            """
            .trimIndent()
            .andLog()
    }

    internal fun extractPks(
        primaryKey: List<List<String>>,
        columnNameMapping: ColumnNameMapping
    ): List<String> {
        return primaryKey.map { fieldPath ->
            if (fieldPath.size != 1) {
                throw UnsupportedOperationException(
                    "Only top-level primary keys are supported, got $fieldPath",
                )
            }
            val fieldName = fieldPath.first()
            val columnName = columnNameMapping[fieldName] ?: fieldName
            columnName
        }
    }

    fun dropTable(tableName: TableName): String =
        "DROP TABLE IF EXISTS `${tableName.namespace}`.`${tableName.name}`;".andLog()

    fun exchangeTable(sourceTableName: TableName, targetTableName: TableName): String =
        """
        EXCHANGE TABLES `${sourceTableName.namespace}`.`${sourceTableName.name}`
            AND `${targetTableName.namespace}`.`${targetTableName.name}`;
        """
            .trimIndent()
            .andLog()

    fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ): String {
        val columnNames = columnNameMapping.map { (_, actualName) -> actualName }.joinToString(",")
        // TODO can we use CDK builtin stuff instead of hardcoding the airbyte meta columns?
        return """
            INSERT INTO `${targetTableName.namespace}`.`${targetTableName.name}`
            (
                $COLUMN_NAME_AB_RAW_ID,
                $COLUMN_NAME_AB_EXTRACTED_AT,
                $COLUMN_NAME_AB_META,
                $COLUMN_NAME_AB_GENERATION_ID,
                $columnNames
            )
            SELECT
                $COLUMN_NAME_AB_RAW_ID,
                $COLUMN_NAME_AB_EXTRACTED_AT,
                $COLUMN_NAME_AB_META,
                $COLUMN_NAME_AB_GENERATION_ID,
                $columnNames
            FROM `${sourceTableName.namespace}`.`${sourceTableName.name}`
            """
            .trimIndent()
            .andLog()
    }

    /**
     * A SQL SELECT statement that extracts records from the table and dedupes the records (since we
     * only need the most-recent record to upsert).
     */
    private fun selectDedupedRecords(
        stream: DestinationStream,
        sourceTableName: TableName,
        columnNameMapping: ColumnNameMapping,
    ): String {
        val columnList: String =
            stream.schema.asColumns().keys.joinToString("\n") { fieldName ->
                val columnName = columnNameMapping[fieldName]!!
                "`$columnName`,"
            }

        val importType = stream.importType as Dedupe

        // We need to dedupe the records. Note the row_number() invocation in
        // the SQL statement. We only take the most-recent raw record for each PK.
        val pkList =
            importType.primaryKey.joinToString(",") { fieldName ->
                val columnName = columnNameMapping[fieldName.first()]!!
                "`$columnName`"
            }
        val cursorOrderClause =
            if (importType.cursor.isEmpty()) {
                ""
            } else if (importType.cursor.size == 1) {
                val columnName = columnNameMapping[importType.cursor.first()]!!
                "`$columnName` DESC NULLS LAST,"
            } else {
                throw UnsupportedOperationException(
                    "Only top-level cursors are supported, got ${importType.cursor}",
                )
            }

        return """
               WITH records AS (
                 SELECT
                   $columnList
                   $COLUMN_NAME_AB_META,
                   $COLUMN_NAME_AB_RAW_ID,
                   $COLUMN_NAME_AB_EXTRACTED_AT,
                   $COLUMN_NAME_AB_GENERATION_ID
                 FROM `${sourceTableName.namespace}`.`${sourceTableName.name}`
               ), numbered_rows AS (
                 SELECT *, row_number() OVER (
                   PARTITION BY $pkList ORDER BY $cursorOrderClause `$COLUMN_NAME_AB_EXTRACTED_AT` DESC
                 ) AS row_number
                 FROM records
               )
               SELECT $columnList $COLUMN_NAME_AB_META, $COLUMN_NAME_AB_RAW_ID, $COLUMN_NAME_AB_EXTRACTED_AT, $COLUMN_NAME_AB_GENERATION_ID
               FROM numbered_rows
               WHERE row_number = 1
               """
            .trimIndent()
            .andLog()
    }

    fun countTable(
        tableName: TableName,
        alias: String = "",
    ): String =
        """
        SELECT count(1) $alias FROM `${tableName.namespace}`.`${tableName.name}`;
    """
            .trimMargin()
            .andLog()

    fun getGenerationId(
        tableName: TableName,
        alias: String = "",
    ): String =
        """
        SELECT $COLUMN_NAME_AB_GENERATION_ID $alias FROM `${tableName.namespace}`.`${tableName.name}` LIMIT 1;
    """
            .trimIndent()
            .andLog()

    private fun columnsAndTypes(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        nonNullableColumns: List<String>,
    ): String {
        return stream.schema
            .asColumns()
            .map { (fieldName, type) ->
                val columnName = columnNameMapping[fieldName]!!
                val typeName = type.type.toDialectType(clickhouseConfiguration.enableJson)
                "`$columnName` ${typeDecl(typeName, !nonNullableColumns.contains(columnName))}"
            }
            .joinToString(",\n")
    }

    fun alterTable(alterationSummary: ColumnChangeset, tableName: TableName): String {
        val builder =
            StringBuilder()
                .append("ALTER TABLE `${tableName.namespace}`.`${tableName.name}`")
                .appendLine()
        alterationSummary.columnsToAdd.forEach { (columnName, columnType) ->
            builder.append(" ADD COLUMN `$columnName` ${columnType.typeDecl()},")
        }
        alterationSummary.columnsToChange.forEach { (columnName, columnType) ->
            builder.append(" MODIFY COLUMN `$columnName` ${columnType.newType.typeDecl()},")
        }
        alterationSummary.columnsToDrop.forEach { (columnName, _) ->
            builder.append(" DROP COLUMN `$columnName`,")
        }

        return builder.dropLast(1).toString().andLog()
    }

    companion object {
        const val DATETIME_WITH_PRECISION = "DateTime64(3)"
        const val DECIMAL_WITH_PRECISION_AND_SCALE = "Decimal(38, 9)"

        private val VALID_VERSION_COLUMN_TYPES =
            setOf(
                IntegerType::class,
                DateType::class,
                TimestampTypeWithTimezone::class,
                TimestampTypeWithoutTimezone::class,
            )
    }
}

fun String.sqlNullable(): String = "Nullable($this)"

fun AirbyteType.toDialectType(enableJson: Boolean): String =
    when (this) {
        BooleanType -> ClickHouseDataType.Bool.name
        DateType -> ClickHouseDataType.Date32.name
        IntegerType -> ClickHouseDataType.Int64.name
        NumberType -> DECIMAL_WITH_PRECISION_AND_SCALE
        StringType -> ClickHouseDataType.String.name
        TimeTypeWithTimezone -> ClickHouseDataType.String.name
        TimeTypeWithoutTimezone -> ClickHouseDataType.String.name
        TimestampTypeWithTimezone,
        TimestampTypeWithoutTimezone -> DATETIME_WITH_PRECISION
        is ArrayType,
        ArrayTypeWithoutSchema,
        is UnionType,
        is UnknownType -> ClickHouseDataType.String.name
        ObjectTypeWithEmptySchema,
        ObjectTypeWithoutSchema,
        is ObjectType -> {
            if (enableJson) {
                ClickHouseDataType.JSON.name
            } else {
                ClickHouseDataType.String.name
            }
        }
    }

fun typeDecl(type: String, nullable: Boolean) =
    if (nullable) {
        type.sqlNullable()
    } else {
        type
    }

fun ColumnType.typeDecl() = typeDecl(this.type, this.nullable)
