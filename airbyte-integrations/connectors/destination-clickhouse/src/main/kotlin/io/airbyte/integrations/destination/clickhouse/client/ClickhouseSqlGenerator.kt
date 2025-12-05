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

    fun createNamespace(namespace: String): String {
        return "CREATE DATABASE IF NOT EXISTS `$namespace`;".andLog()
    }

    fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        replace: Boolean,
    ): String {
        val pks: List<String> = stream.tableSchema.getPrimaryKey().flatten()

        // For ReplacingMergeTree, we need to make the cursor column non-nullable if it's used as
        // version column. We'll also determine here if we need to fall back to extracted_at.
        var useCursorAsVersionColumn = false
        val cursorColumns = stream.tableSchema.getCursor()
        val nonNullableColumns =
            mutableSetOf<String>().apply {
                addAll(pks) // Primary keys are always non-nullable
                if (stream.importType is Dedupe && cursorColumns.isNotEmpty()) {
                    val cursorFieldName = (stream.importType as Dedupe).cursor.firstOrNull()
                    val cursorColumnName = cursorColumns.firstOrNull()
                    
                    if (cursorFieldName != null && cursorColumnName != null) {
                        // Check if the cursor column type is valid for ClickHouse
                        // ReplacingMergeTree
                        val cursorColumnType = stream.tableSchema.columnSchema.inputSchema[cursorFieldName]?.type
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
            columnsAndTypes(stream, nonNullableColumns.toList())

        val forceCreateTable = if (replace) "OR REPLACE" else ""

        val pksAsString =
            pks.joinToString(",") {
                // Escape the columns
                "`$it`"
            }

        val engine =
            when (stream.importType) {
                is Dedupe -> {
                    // Use cursor column as version column for ReplacingMergeTree if available and
                    // valid
                    val versionColumn =
                        if (cursorColumns.isNotEmpty() && useCursorAsVersionColumn) {
                            "`${cursorColumns.first()}`"
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
            ENGINE = $engine
            ORDER BY (${if (pks.isEmpty()) {
            COLUMN_NAME_AB_RAW_ID
        } else {
            pksAsString
        }})
            """
            .trimIndent()
            .andLog()
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
        nonNullableColumns: List<String>,
    ): String {
        return stream.tableSchema.columnSchema.inputSchema
            .map { (fieldName, type) ->
                val columnName = stream.tableSchema.columnSchema.inputToFinalColumnNames[fieldName]!!
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
}

fun String.sqlNullable(): String = "Nullable($this)"

fun typeDecl(type: String, nullable: Boolean) =
    if (nullable) {
        type.sqlNullable()
    } else {
        type
    }

fun ColumnType.typeDecl() = typeDecl(this.type, this.nullable)
