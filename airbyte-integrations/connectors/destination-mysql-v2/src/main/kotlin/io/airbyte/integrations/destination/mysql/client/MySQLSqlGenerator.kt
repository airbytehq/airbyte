/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.client

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
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

@Singleton
class MySQLSqlGenerator {

    private fun String.andLog(): String {
        log.info { this }
        return this
    }

    // ========================================
    // NAMESPACE OPERATIONS
    // ========================================

    fun createNamespace(namespace: String): String {
        return "CREATE DATABASE IF NOT EXISTS `$namespace`".andLog()
    }

    fun namespaceExists(namespace: String): String {
        return """
            SELECT SCHEMA_NAME
            FROM information_schema.SCHEMATA
            WHERE SCHEMA_NAME = '$namespace'
        """.trimIndent().andLog()
    }

    // ========================================
    // TABLE OPERATIONS
    // ========================================

    fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    ): String {
        val columnDeclarations = columnsAndTypes(stream, columnNameMapping)

        // MySQL doesn't have CREATE OR REPLACE TABLE, so we drop first if replace is true
        val dropIfReplace = if (replace) {
            dropTable(tableName) + ";\n"
        } else {
            ""
        }

        // Only add the user columns section if there are any columns
        val userColumnsSection = if (columnDeclarations.isNotEmpty()) {
            ",\n$columnDeclarations"
        } else {
            ""
        }

        val createTableSql = """
            ${dropIfReplace}CREATE TABLE IF NOT EXISTS `${tableName.namespace}`.`${tableName.name}` (
              `$COLUMN_NAME_AB_RAW_ID` VARCHAR(256) NOT NULL,
              `$COLUMN_NAME_AB_EXTRACTED_AT` DATETIME(6) NOT NULL,
              `$COLUMN_NAME_AB_META` JSON NOT NULL,
              `$COLUMN_NAME_AB_GENERATION_ID` BIGINT$userColumnsSection
            )
        """.trimIndent()

        return createTableSql.andLog()
    }

    fun dropTable(tableName: TableName): String {
        return "DROP TABLE IF EXISTS `${tableName.namespace}`.`${tableName.name}`".andLog()
    }

    fun countTable(tableName: TableName, alias: String = ""): String {
        val aliasClause = if (alias.isNotEmpty()) " AS $alias" else ""
        return "SELECT COUNT(*) $aliasClause FROM `${tableName.namespace}`.`${tableName.name}`".andLog()
    }

    fun getGenerationId(tableName: TableName, alias: String = ""): String {
        val aliasClause = if (alias.isNotEmpty()) " AS $alias" else ""
        return """
            SELECT `$COLUMN_NAME_AB_GENERATION_ID` $aliasClause
            FROM `${tableName.namespace}`.`${tableName.name}`
            LIMIT 1
        """.trimIndent().andLog()
    }

    fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ): String {
        val columnNames = columnNameMapping.map { (_, actualName) -> "`$actualName`" }.joinToString(",")
        return """
            INSERT INTO `${targetTableName.namespace}`.`${targetTableName.name}`
            (
                `$COLUMN_NAME_AB_RAW_ID`,
                `$COLUMN_NAME_AB_EXTRACTED_AT`,
                `$COLUMN_NAME_AB_META`,
                `$COLUMN_NAME_AB_GENERATION_ID`,
                $columnNames
            )
            SELECT
                `$COLUMN_NAME_AB_RAW_ID`,
                `$COLUMN_NAME_AB_EXTRACTED_AT`,
                `$COLUMN_NAME_AB_META`,
                `$COLUMN_NAME_AB_GENERATION_ID`,
                $columnNames
            FROM `${sourceTableName.namespace}`.`${sourceTableName.name}`
        """.trimIndent().andLog()
    }

    fun renameTable(source: TableName, target: TableName): String {
        return "RENAME TABLE `${source.namespace}`.`${source.name}` TO `${target.namespace}`.`${target.name}`".andLog()
    }

    fun alterTable(alterationSummary: ColumnChangeset, tableName: TableName): String {
        val alterations = mutableListOf<String>()

        alterationSummary.columnsToAdd.forEach { (columnName, columnType) ->
            alterations.add("ADD COLUMN `$columnName` ${columnType.toMySQLTypeDecl()}")
        }
        alterationSummary.columnsToChange.forEach { (columnName, columnChange) ->
            alterations.add("MODIFY COLUMN `$columnName` ${columnChange.newType.toMySQLTypeDecl()}")
        }
        alterationSummary.columnsToDrop.forEach { (columnName, _) ->
            alterations.add("DROP COLUMN `$columnName`")
        }

        return "ALTER TABLE `${tableName.namespace}`.`${tableName.name}` ${alterations.joinToString(", ")}".andLog()
    }

    // ========================================
    // UPSERT OPERATIONS (MySQL uses INSERT ON DUPLICATE KEY UPDATE)
    // ========================================

    /**
     * Generates SQL to upsert deduplicated records from source table to target table.
     *
     * Uses a DELETE + INSERT approach:
     * 1. Select deduplicated records from source (using ROW_NUMBER to keep latest per PK)
     * 2. Delete existing records from target where PK exists in source
     * 3. Insert deduplicated records into target
     */
    fun upsertFromTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ): String {
        val importType = stream.importType as Dedupe
        val primaryKey = importType.primaryKey.map { fieldPath ->
            if (fieldPath.size != 1) {
                throw UnsupportedOperationException("Only top-level primary keys are supported, got $fieldPath")
            }
            val fieldName = fieldPath.first()
            columnNameMapping[fieldName] ?: fieldName
        }

        val pkColumns = primaryKey.joinToString(", ") { "`$it`" }

        // First deduplicate the source table
        val dedupedSelect = selectDedupedRecords(stream, sourceTableName, columnNameMapping)

        val columnNames = columnNameMapping.map { (_, actualName) -> "`$actualName`" }.joinToString(",")
        val allColumns = """
            `$COLUMN_NAME_AB_RAW_ID`,
            `$COLUMN_NAME_AB_EXTRACTED_AT`,
            `$COLUMN_NAME_AB_META`,
            `$COLUMN_NAME_AB_GENERATION_ID`,
            $columnNames
        """.trimIndent()

        // Use DELETE + INSERT approach since MySQL doesn't support MERGE
        // This is wrapped in a transaction by the caller
        return """
            DELETE FROM `${targetTableName.namespace}`.`${targetTableName.name}`
            WHERE ($pkColumns) IN (
                SELECT $pkColumns FROM `${sourceTableName.namespace}`.`${sourceTableName.name}`
            );
            INSERT INTO `${targetTableName.namespace}`.`${targetTableName.name}`
            ($allColumns)
            $dedupedSelect
        """.trimIndent().andLog()
    }

    private fun selectDedupedRecords(
        stream: DestinationStream,
        sourceTableName: TableName,
        columnNameMapping: ColumnNameMapping,
    ): String {
        val columnList = stream.schema.asColumns().keys.joinToString(",\n") { fieldName ->
            val columnName = columnNameMapping[fieldName]!!
            "`$columnName`"
        }

        val importType = stream.importType as Dedupe

        val pkList = importType.primaryKey.joinToString(",") { fieldName ->
            val columnName = columnNameMapping[fieldName.first()]!!
            "`$columnName`"
        }

        val cursorOrderClause = if (importType.cursor.isEmpty()) {
            ""
        } else if (importType.cursor.size == 1) {
            val columnName = columnNameMapping[importType.cursor.first()]!!
            "`$columnName` DESC,"
        } else {
            throw UnsupportedOperationException("Only top-level cursors are supported, got ${importType.cursor}")
        }

        return """
            SELECT
                `$COLUMN_NAME_AB_RAW_ID`,
                `$COLUMN_NAME_AB_EXTRACTED_AT`,
                `$COLUMN_NAME_AB_META`,
                `$COLUMN_NAME_AB_GENERATION_ID`,
                $columnList
            FROM (
                SELECT *, ROW_NUMBER() OVER (
                    PARTITION BY $pkList ORDER BY $cursorOrderClause `$COLUMN_NAME_AB_EXTRACTED_AT` DESC
                ) AS row_num
                FROM `${sourceTableName.namespace}`.`${sourceTableName.name}`
            ) AS deduped
            WHERE row_num = 1
        """.trimIndent()
    }

    // ========================================
    // HELPER METHODS
    // ========================================

    private fun columnsAndTypes(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
    ): String {
        return stream.schema
            .asColumns()
            .map { (fieldName, type) ->
                val columnName = columnNameMapping[fieldName]!!
                val typeName = type.type.toDialectType()
                val nullableClause = if (type.nullable) "" else " NOT NULL"
                "`$columnName` $typeName$nullableClause"
            }
            .joinToString(",\n")
    }

    internal fun extractPks(
        primaryKey: List<List<String>>,
        columnNameMapping: ColumnNameMapping
    ): List<String> {
        return primaryKey.map { fieldPath ->
            if (fieldPath.size != 1) {
                throw UnsupportedOperationException("Only top-level primary keys are supported, got $fieldPath")
            }
            val fieldName = fieldPath.first()
            columnNameMapping[fieldName] ?: fieldName
        }
    }

    companion object {
        const val DATETIME_PRECISION = "DATETIME(6)"
        const val DECIMAL_PRECISION = "DECIMAL(38, 9)"
    }
}

fun AirbyteType.toDialectType(): String = when (this) {
    BooleanType -> "BOOLEAN"
    DateType -> "DATE"
    IntegerType -> "BIGINT"
    NumberType -> MySQLSqlGenerator.DECIMAL_PRECISION
    StringType -> "TEXT"
    TimeTypeWithTimezone -> "TIME(6)"
    TimeTypeWithoutTimezone -> "TIME(6)"
    TimestampTypeWithTimezone,
    TimestampTypeWithoutTimezone -> MySQLSqlGenerator.DATETIME_PRECISION
    // Use TEXT for all complex/nested types because:
    // 1. With STRINGIFY behavior, these values are already JSON-serialized strings
    // 2. UnknownType values may not be valid JSON (e.g., plain strings)
    // 3. TEXT avoids MySQL's JSON formatting (which adds spaces after colons)
    // 4. This matches Clickhouse's approach with STRINGIFY behavior
    is ArrayType,
    ArrayTypeWithoutSchema,
    is UnionType,
    is UnknownType,
    ObjectTypeWithEmptySchema,
    ObjectTypeWithoutSchema,
    is ObjectType -> "TEXT"
}

fun ColumnType.toMySQLTypeDecl(): String {
    val nullableClause = if (nullable) "" else " NOT NULL"
    return "$type$nullableClause"
}
