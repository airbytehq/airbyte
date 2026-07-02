/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.client

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

@Singleton
class DorisSqlGenerator {
    private val log = KotlinLogging.logger {}

    fun createNamespace(namespace: String): String {
        return "CREATE DATABASE IF NOT EXISTS `$namespace`".andLog()
    }

    fun createTable(
        tableName: TableName,
        tableSchema: StreamTableSchema,
        replace: Boolean,
    ): String {
        val finalSchema = tableSchema.columnSchema.finalSchema
        val columnDeclarations =
            finalSchema
                .map { (columnName, columnType) -> "  `$columnName` ${columnType.typeDecl()}" }
                .joinToString(",\n")

        val isDedupe = tableSchema.importType is Dedupe

        val keyModel: String
        val distributeBy: String

        if (isDedupe) {
            val pks = flattenPks(tableSchema.getPrimaryKey())
            val pkCols = pks.joinToString(", ") { "`$it`" }
            keyModel = "UNIQUE KEY($pkCols)"
            distributeBy = "DISTRIBUTED BY HASH(${pks.first().let { "`$it`" }}) BUCKETS AUTO"
        } else {
            keyModel = "DUPLICATE KEY(`$COLUMN_NAME_AB_RAW_ID`)"
            distributeBy = "DISTRIBUTED BY HASH(`$COLUMN_NAME_AB_RAW_ID`) BUCKETS AUTO"
        }

        val statements = StringBuilder()
        if (replace) {
            statements.appendLine(
                "DROP TABLE IF EXISTS `${tableName.namespace}`.`${tableName.name}`;"
            )
        }

        statements.append(
            """
            CREATE TABLE IF NOT EXISTS `${tableName.namespace}`.`${tableName.name}` (
              `$COLUMN_NAME_AB_RAW_ID` ${DorisSqlTypes.VARCHAR_40} NOT NULL,
              `$COLUMN_NAME_AB_EXTRACTED_AT` ${DorisSqlTypes.DATETIME} NOT NULL,
              `$COLUMN_NAME_AB_META` ${DorisSqlTypes.STRING} NOT NULL,
              `$COLUMN_NAME_AB_GENERATION_ID` ${DorisSqlTypes.BIGINT} NOT NULL,
            $columnDeclarations
            )
            $keyModel
            $distributeBy
            PROPERTIES ("replication_num" = "1")
            """.trimIndent()
        )

        return statements.toString().andLog()
    }

    fun dropTable(tableName: TableName): String =
        "DROP TABLE IF EXISTS `${tableName.namespace}`.`${tableName.name}`".andLog()

    fun renameTable(sourceTableName: TableName, targetTableName: TableName): String =
        "ALTER TABLE `${sourceTableName.namespace}`.`${sourceTableName.name}` RENAME `${targetTableName.name}`".andLog()

    fun copyTable(
        columnNames: Set<String>,
        sourceTableName: TableName,
        targetTableName: TableName,
    ): String {
        val joinedNames = columnNames.joinToString(", ") { "`$it`" }
        return """
            INSERT INTO `${targetTableName.namespace}`.`${targetTableName.name}`
            (
                `$COLUMN_NAME_AB_RAW_ID`,
                `$COLUMN_NAME_AB_EXTRACTED_AT`,
                `$COLUMN_NAME_AB_META`,
                `$COLUMN_NAME_AB_GENERATION_ID`,
                $joinedNames
            )
            SELECT
                `$COLUMN_NAME_AB_RAW_ID`,
                `$COLUMN_NAME_AB_EXTRACTED_AT`,
                `$COLUMN_NAME_AB_META`,
                `$COLUMN_NAME_AB_GENERATION_ID`,
                $joinedNames
            FROM `${sourceTableName.namespace}`.`${sourceTableName.name}`
            """
            .trimIndent()
            .andLog()
    }

    fun countTable(tableName: TableName, alias: String = ""): String =
        "SELECT count(1) $alias FROM `${tableName.namespace}`.`${tableName.name}`".andLog()

    fun getGenerationId(tableName: TableName, alias: String = ""): String =
        "SELECT `$COLUMN_NAME_AB_GENERATION_ID` $alias FROM `${tableName.namespace}`.`${tableName.name}` LIMIT 1".andLog()

    fun alterTable(alterationSummary: ColumnChangeset, tableName: TableName): String {
        val statements = mutableListOf<String>()

        alterationSummary.columnsToAdd.forEach { (columnName, columnType) ->
            statements.add(
                "ALTER TABLE `${tableName.namespace}`.`${tableName.name}` ADD COLUMN `$columnName` ${columnType.typeDecl()}"
            )
        }
        alterationSummary.columnsToChange.forEach { (columnName, columnType) ->
            statements.add(
                "ALTER TABLE `${tableName.namespace}`.`${tableName.name}` MODIFY COLUMN `$columnName` ${columnType.newType.typeDecl()}"
            )
        }
        alterationSummary.columnsToDrop.forEach { (columnName, _) ->
            statements.add(
                "ALTER TABLE `${tableName.namespace}`.`${tableName.name}` DROP COLUMN `$columnName`"
            )
        }

        return statements.joinToString(";\n").andLog()
    }

    fun ColumnType.typeDecl(): String =
        if (nullable) {
            "$type NULL"
        } else {
            "$type NOT NULL"
        }

    internal fun flattenPks(primaryKey: List<List<String>>): List<String> {
        return primaryKey.map { fieldPath ->
            if (fieldPath.size != 1) {
                throw UnsupportedOperationException(
                    "Only top-level primary keys are supported, got $fieldPath"
                )
            }
            fieldPath.first()
        }
    }

    private fun String.andLog(): String {
        log.info { this }
        return this
    }
}
