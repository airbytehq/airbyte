/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.client

import com.clickhouse.data.ClickHouseDataType
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
import io.airbyte.cdk.load.orchestration.db.CDC_DELETED_AT_COLUMN
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.clickhouse_v2.client.ClickhouseSqlGenerator.Companion.DATETIME_WITH_PRECISION
import io.airbyte.integrations.destination.clickhouse_v2.model.AlterationSummary
import jakarta.inject.Singleton

@Singleton
class ClickhouseSqlGenerator {

    fun createNamespace(namespace: String): String {
        return "CREATE DATABASE IF NOT EXISTS `$namespace`;"
    }

    fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    ): String {
        val columnDeclarations = columnsAndTypes(stream, columnNameMapping)

        val forceCreateTable = if (replace) "OR REPLACE" else ""

        val engine =
            when (stream.importType) {
                is Dedupe -> "ReplacingMergeTree()"
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
            ORDER BY ($COLUMN_NAME_AB_RAW_ID)
            """.trimIndent()
    }

    fun dropTable(tableName: TableName): String =
        "DROP TABLE IF EXISTS `${tableName.namespace}`.`${tableName.name}`;"

    fun swapTable(sourceTableName: TableName, targetTableName: TableName): String =
        """
        ALTER TABLE `${sourceTableName.namespace}`.`${sourceTableName.name}` 
            RENAME TO `${targetTableName.namespace}.${targetTableName.name}`;
        """.trimMargin()

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
            """.trimIndent()
    }

    fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        val importType = stream.importType as Dedupe
        val pkEquivalent =
            importType.primaryKey.joinToString(" AND ") { fieldPath ->
                val fieldName = fieldPath.first()
                val columnName = columnNameMapping[fieldName]!!
                """(target_table.`$columnName` = new_record.`$columnName` OR (target_table.`$columnName` IS NULL AND new_record.`$columnName` IS NULL))"""
            }

        val columnList: String =
            stream.schema.asColumns().keys.joinToString("\n") { fieldName ->
                val columnName = columnNameMapping[fieldName]!!
                "`$columnName`,"
            }
        val newRecordColumnList: String =
            stream.schema.asColumns().keys.joinToString("\n") { fieldName ->
                val columnName = columnNameMapping[fieldName]!!
                "new_record.`$columnName`,"
            }
        val selectSourceRecords = selectDedupedRecords(stream, sourceTableName, columnNameMapping)

        val cursorComparison: String
        if (importType.cursor.isNotEmpty()) {
            val cursorFieldName = importType.cursor.first()
            val cursorColumnName = columnNameMapping[cursorFieldName]!!
            val cursor = "`$cursorColumnName`"
            // Build a condition for "new_record is more recent than target_table":
            cursorComparison = // First, compare the cursors.
            ("""
             (
               target_table.$cursor < new_record.$cursor
               OR (target_table.$cursor = new_record.$cursor AND target_table.$COLUMN_NAME_AB_EXTRACTED_AT < new_record.$COLUMN_NAME_AB_EXTRACTED_AT)
               OR (target_table.$cursor IS NULL AND new_record.$cursor IS NULL AND target_table.$COLUMN_NAME_AB_EXTRACTED_AT < new_record.$COLUMN_NAME_AB_EXTRACTED_AT)
               OR (target_table.$cursor IS NULL AND new_record.$cursor IS NOT NULL)
             )
             """.trimIndent())
        } else {
            // If there's no cursor, then we just take the most-recently-emitted record
            cursorComparison =
                "target_table.$COLUMN_NAME_AB_EXTRACTED_AT < new_record.$COLUMN_NAME_AB_EXTRACTED_AT"
        }

        val cdcDeleteClause: String
        val cdcSkipInsertClause: String
        if (stream.schema.asColumns().containsKey(CDC_DELETED_AT_COLUMN)) {
            // Execute CDC deletions if there's already a record
            cdcDeleteClause =
                "WHEN MATCHED AND new_record._ab_cdc_deleted_at IS NOT NULL AND $cursorComparison THEN DELETE"
            // And skip insertion entirely if there's no matching record.
            // (This is possible if a single T+D batch contains both an insertion and deletion for
            // the same PK)
            cdcSkipInsertClause = "AND new_record._ab_cdc_deleted_at IS NULL"
        } else {
            cdcDeleteClause = ""
            cdcSkipInsertClause = ""
        }

        val columnAssignments: String =
            stream.schema.asColumns().keys.joinToString("\n") { fieldName ->
                val column = columnNameMapping[fieldName]!!
                "`$column` = new_record.`$column`,"
            }

        return """
               MERGE `${targetTableName.namespace}`.`${targetTableName.name}` target_table
               USING (
                 $selectSourceRecords
               ) new_record
               ON $pkEquivalent
               $cdcDeleteClause
               WHEN MATCHED AND $cursorComparison THEN UPDATE SET
                 $columnAssignments
                 $COLUMN_NAME_AB_META = new_record.$COLUMN_NAME_AB_META,
                 $COLUMN_NAME_AB_RAW_ID = new_record.$COLUMN_NAME_AB_RAW_ID,
                 $COLUMN_NAME_AB_EXTRACTED_AT = new_record.$COLUMN_NAME_AB_EXTRACTED_AT,
                 $COLUMN_NAME_AB_GENERATION_ID = new_record.$COLUMN_NAME_AB_GENERATION_ID
               WHEN NOT MATCHED $cdcSkipInsertClause THEN INSERT (
                 $columnList
                 $COLUMN_NAME_AB_META,
                 $COLUMN_NAME_AB_RAW_ID,
                 $COLUMN_NAME_AB_EXTRACTED_AT,
                 $COLUMN_NAME_AB_GENERATION_ID
               ) VALUES (
                 $newRecordColumnList
                 new_record.$COLUMN_NAME_AB_META,
                 new_record.$COLUMN_NAME_AB_RAW_ID,
                 new_record.$COLUMN_NAME_AB_EXTRACTED_AT,
                 new_record.$COLUMN_NAME_AB_GENERATION_ID
               );
               """.trimIndent()
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
               """.trimIndent()
    }

    fun countTable(
        tableName: TableName,
        alias: String = "",
    ): String =
        """
        SELECT count(1) $alias FROM `${tableName.namespace}`.`${tableName.name}`;
    """.trimMargin()

    fun getGenerationId(
        tableName: TableName,
        alias: String = "",
    ): String =
        """
        SELECT $COLUMN_NAME_AB_GENERATION_ID $alias FROM `${tableName.namespace}`.`${tableName.name}` LIMIT 1;
    """.trimIndent()

    private fun columnsAndTypes(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): String =
        stream.schema
            .asColumns()
            .map { (fieldName, type) ->
                val columnName = columnNameMapping[fieldName]!!
                val typeName = type.type.toDialectType()
                "`$columnName` Nullable($typeName)"
            }
            .joinToString(",\n")

    fun wrapInTransaction(vararg sqlStatements: String): String {
        val builder = StringBuilder()
        builder.append("BEGIN TRANSACTION;\n")
        sqlStatements.forEach {
            builder.append(it)
            // No semicolon - statements already end with a semicolon
            builder.append("\n")
        }
        builder.append("COMMIT TRANSACTION;\n")

        return builder.toString()
    }

    fun alterTable(alterationSummary: AlterationSummary, tableName: TableName): String {
        val builder =
            StringBuilder()
                .append("ALTER TABLE `${tableName.namespace}`.`${tableName.name}`")
                .appendLine()
        alterationSummary.added.forEach { (columnName, columnType) ->
            builder.append(" ADD COLUMN `$columnName` ${columnType.sqlNullable()},")
        }
        alterationSummary.modified.forEach { (columnName, columnType) ->
            builder.append(" MODIFY COLUMN `$columnName` ${columnType.sqlNullable()},")
        }
        alterationSummary.deleted.forEach { columnName ->
            builder.append(" DROP COLUMN `$columnName`,")
        }
        return builder.dropLast(1).toString()
    }

    private fun String.sqlNullable(): String = "Nullable($this)"

    companion object {
        const val DATETIME_WITH_PRECISION = "DateTime64(3)"
    }
}

fun AirbyteType.toDialectType(): String =
    when (this) {
        BooleanType -> ClickHouseDataType.Bool.name
        DateType -> ClickHouseDataType.Date.name
        IntegerType -> ClickHouseDataType.Int64.name
        NumberType -> ClickHouseDataType.Decimal.name
        StringType -> ClickHouseDataType.String.name
        TimeTypeWithTimezone -> ClickHouseDataType.String.name
        TimeTypeWithoutTimezone -> ClickHouseDataType.String.name
        TimestampTypeWithTimezone,
        TimestampTypeWithoutTimezone -> DATETIME_WITH_PRECISION
        is ArrayType,
        ArrayTypeWithoutSchema,
        is ObjectType,
        ObjectTypeWithEmptySchema,
        ObjectTypeWithoutSchema,
        is UnionType,
        is UnknownType -> ClickHouseDataType.String.name
    }
