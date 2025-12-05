/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.client

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

@Singleton
class ClickhouseSqlGenerator {
    private val log = KotlinLogging.logger {}

    fun createNamespace(namespace: String): String {
        return "CREATE DATABASE IF NOT EXISTS `$namespace`;".andLog()
    }

    fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        replace: Boolean,
    ): String {
        val forceCreateTable = if (replace) "OR REPLACE" else ""

        val columnDeclarations =
            stream.tableSchema.columnSchema.finalSchema
                .map { (columnName, columnType) -> "`$columnName` ${columnType.typeDecl()}" }
                .joinToString(",\n")

        val orderBy =
            if (stream.tableSchema.importType !is Dedupe) {
                COLUMN_NAME_AB_RAW_ID
            } else {
                val pks = flattenPks(stream.tableSchema.getPrimaryKey())
                pks.joinToString(",") {
                    // Escape the columns
                    "`$it`"
                }
            }

        val engine =
            when (stream.importType) {
                is Dedupe -> {
                    val cursor = stream.tableSchema.getCursor().firstOrNull()

                    val versionColumn =
                        if (cursor != null && cursor.isValidVersionColumnType()) {
                            "`${cursor}`"
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
            ORDER BY ($orderBy)
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

    fun ColumnType.typeDecl() =
        if (nullable) {
            "Nullable($type)"
        } else {
            type
        }

    /**
     * TODO: this is really a schema validation function and should probably run on startup long
     * before we go to create a table.
     */
    internal fun flattenPks(
        primaryKey: List<List<String>>,
    ): List<String> {
        return primaryKey.map { fieldPath ->
            if (fieldPath.size != 1) {
                throw UnsupportedOperationException(
                    "Only top-level primary keys are supported, got $fieldPath",
                )
            }
            fieldPath.first()
        }
    }

    /**
     * This extension is here to avoid writing `.also { log.info { it }}` for every returned string
     * we want to log
     */
    private fun String.andLog(): String {
        log.info { this }
        return this
    }
}
