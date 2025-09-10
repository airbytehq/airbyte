/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.client

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
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

private val log = KotlinLogging.logger {}

@Singleton
class SnowflakeDirectLoadSqlGenerator() {

    /**
     * This extension is here to avoid writing `.also { log.info { it }}` for every returned string
     * we want to log
     */
    private fun String.andLog(): String {
        log.info { this }
        return this
    }

    fun countTable(tableName: TableName): String {
        return "SELECT COUNT(*) AS total FROM ${tableName.toPrettyString()}".andLog()
    }

    fun createNamespace(namespace: String): String {
        return "CREATE SCHEMA IF NOT EXISTS \"$namespace\"".andLog()
    }

    fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ): String {
        fun columnsAndTypes(
            stream: DestinationStream,
            columnNameMapping: ColumnNameMapping
        ): String =
            stream.schema
                .asColumns()
                .map { (fieldName, type) ->
                    val columnName = columnNameMapping[fieldName]!!
                    val typeName = toDialectType(type.type)
                    "\"$columnName\" $typeName"
                }
                .joinToString(",\n")

        val columnDeclarations = columnsAndTypes(stream, columnNameMapping)

        // Snowflake supports CREATE OR REPLACE TABLE, which is simpler than drop+recreate
        val createOrReplace = if (replace) "CREATE OR REPLACE" else "CREATE"

        val createTableStatement =
            """
            $createOrReplace TABLE ${tableName.toPrettyString(QUOTE)} (
              "$COLUMN_NAME_AB_RAW_ID" VARCHAR NOT NULL,
              "$COLUMN_NAME_AB_EXTRACTED_AT" TIMESTAMP_TZ NOT NULL,
              "$COLUMN_NAME_AB_META" VARIANT NOT NULL,
              "$COLUMN_NAME_AB_GENERATION_ID" NUMBER,
              $columnDeclarations
            )
        """.trimIndent()

        return createTableStatement.andLog()
    }

    //    fun overwriteTable(sourceTableName: TableName, targetTableName: TableName): String {
    //        TODO("Not yet implemented")
    //    }

    fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        val columnNames =
            columnNameMapping.map { (_, actualName) -> actualName }.joinToString(",") { "\"$it\"" }

        return """
            INSERT INTO ${targetTableName.toPrettyString(QUOTE)}
            (
                "$COLUMN_NAME_AB_RAW_ID",
                "$COLUMN_NAME_AB_EXTRACTED_AT",
                "$COLUMN_NAME_AB_META",
                "$COLUMN_NAME_AB_GENERATION_ID",
                $columnNames
            )
            SELECT
                "$COLUMN_NAME_AB_RAW_ID",
                "$COLUMN_NAME_AB_EXTRACTED_AT",
                "$COLUMN_NAME_AB_META",
                "$COLUMN_NAME_AB_GENERATION_ID",
                $columnNames
            FROM ${sourceTableName.toPrettyString(QUOTE)}
            """
            .trimIndent()
            .andLog()
    }

    fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ): String {
        val importType = stream.importType as Dedupe

        // Build primary key matching condition
        val pkEquivalent =
            if (importType.primaryKey.isNotEmpty()) {
                importType.primaryKey.joinToString(" AND ") { fieldPath ->
                    val fieldName = fieldPath.first()
                    val columnName = columnNameMapping[fieldName]!!
                    """(target_table."$columnName" = new_record."$columnName" OR (target_table."$columnName" IS NULL AND new_record."$columnName" IS NULL))"""
                }
            } else {
                // If no primary key, we can't perform a meaningful upsert
                throw IllegalArgumentException("Cannot perform upsert without primary key")
            }

        // Build column lists for INSERT and UPDATE
        val columnList: String =
            stream.schema.asColumns().keys.joinToString(",\n") { fieldName ->
                val columnName = columnNameMapping[fieldName]!!
                "\"$columnName\""
            }

        val newRecordColumnList: String =
            stream.schema.asColumns().keys.joinToString(",\n") { fieldName ->
                val columnName = columnNameMapping[fieldName]!!
                "new_record.\"$columnName\""
            }

        // Get deduped records from source
        val selectSourceRecords = selectDedupedRecords(stream, sourceTableName, columnNameMapping)

        // Build cursor comparison for determining which record is newer
        val cursorComparison: String
        if (importType.cursor.isNotEmpty()) {
            val cursorFieldName = importType.cursor.first()
            val cursorColumnName = columnNameMapping[cursorFieldName]!!
            val cursor = "\"$cursorColumnName\""
            cursorComparison =
                """
                (
                  target_table.$cursor < new_record.$cursor
                  OR (target_table.$cursor = new_record.$cursor AND target_table."$COLUMN_NAME_AB_EXTRACTED_AT" < new_record."$COLUMN_NAME_AB_EXTRACTED_AT")
                  OR (target_table.$cursor IS NULL AND new_record.$cursor IS NULL AND target_table."$COLUMN_NAME_AB_EXTRACTED_AT" < new_record."$COLUMN_NAME_AB_EXTRACTED_AT")
                  OR (target_table.$cursor IS NULL AND new_record.$cursor IS NOT NULL)
                )
            """.trimIndent()
        } else {
            // No cursor - use extraction timestamp only
            cursorComparison =
                """target_table."$COLUMN_NAME_AB_EXTRACTED_AT" < new_record."$COLUMN_NAME_AB_EXTRACTED_AT""""
        }

        // Build column assignments for UPDATE
        val columnAssignments: String =
            stream.schema.asColumns().keys.joinToString(",\n") { fieldName ->
                val column = columnNameMapping[fieldName]!!
                "\"$column\" = new_record.\"$column\""
            }

        // Build the MERGE statement
        val mergeStatement =
            """
            MERGE INTO ${targetTableName.toPrettyString(QUOTE)} AS target_table
            USING (
              $selectSourceRecords
            ) AS new_record
            ON $pkEquivalent
            WHEN MATCHED AND $cursorComparison THEN UPDATE SET
              $columnAssignments,
              "$COLUMN_NAME_AB_META" = new_record."$COLUMN_NAME_AB_META",
              "$COLUMN_NAME_AB_RAW_ID" = new_record."$COLUMN_NAME_AB_RAW_ID",
              "$COLUMN_NAME_AB_EXTRACTED_AT" = new_record."$COLUMN_NAME_AB_EXTRACTED_AT",
              "$COLUMN_NAME_AB_GENERATION_ID" = new_record."$COLUMN_NAME_AB_GENERATION_ID"
            WHEN NOT MATCHED THEN INSERT (
              $columnList,
              "$COLUMN_NAME_AB_META",
              "$COLUMN_NAME_AB_RAW_ID",
              "$COLUMN_NAME_AB_EXTRACTED_AT",
              "$COLUMN_NAME_AB_GENERATION_ID"
            ) VALUES (
              $newRecordColumnList,
              new_record."$COLUMN_NAME_AB_META",
              new_record."$COLUMN_NAME_AB_RAW_ID",
              new_record."$COLUMN_NAME_AB_EXTRACTED_AT",
              new_record."$COLUMN_NAME_AB_GENERATION_ID"
            )
        """.trimIndent()

        return mergeStatement.andLog()
    }

    /**
     * Generates a SQL SELECT statement that extracts and deduplicates records from the source
     * table. Uses ROW_NUMBER() window function to select the most recent record per primary key.
     */
    private fun selectDedupedRecords(
        stream: DestinationStream,
        sourceTableName: TableName,
        columnNameMapping: ColumnNameMapping
    ): String {
        val columnList: String =
            stream.schema.asColumns().keys.joinToString(",\n") { fieldName ->
                val columnName = columnNameMapping[fieldName]!!
                "\"$columnName\""
            }

        val importType = stream.importType as Dedupe

        // Build the primary key list for partitioning
        val pkList =
            if (importType.primaryKey.isNotEmpty()) {
                importType.primaryKey.joinToString(",") { fieldPath ->
                    val columnName = columnNameMapping[fieldPath.first()]!!
                    "\"$columnName\""
                }
            } else {
                // Should not happen as we check this earlier, but handle it defensively
                throw IllegalArgumentException("Cannot deduplicate without primary key")
            }

        // Build cursor order clause for sorting within each partition
        val cursorOrderClause =
            if (importType.cursor.isNotEmpty()) {
                val columnName = columnNameMapping[importType.cursor.first()]!!
                "\"$columnName\" DESC NULLS LAST,"
            } else {
                ""
            }

        return """
            WITH records AS (
              SELECT
                $columnList,
                "$COLUMN_NAME_AB_META",
                "$COLUMN_NAME_AB_RAW_ID",
                "$COLUMN_NAME_AB_EXTRACTED_AT",
                "$COLUMN_NAME_AB_GENERATION_ID"
              FROM ${sourceTableName.toPrettyString(QUOTE)}
            ), numbered_rows AS (
              SELECT *, ROW_NUMBER() OVER (
                PARTITION BY $pkList ORDER BY $cursorOrderClause "$COLUMN_NAME_AB_EXTRACTED_AT" DESC
              ) AS row_number
              FROM records
            )
            SELECT $columnList, "$COLUMN_NAME_AB_META", "$COLUMN_NAME_AB_RAW_ID", "$COLUMN_NAME_AB_EXTRACTED_AT", "$COLUMN_NAME_AB_GENERATION_ID"
            FROM numbered_rows
            WHERE row_number = 1
        """
            .trimIndent()
            .andLog()
    }

    fun dropTable(tableName: TableName): String {
        return "DROP TABLE IF EXISTS ${tableName.toPrettyString(QUOTE)}".andLog()
    }

    fun getGenerationId(
        tableName: TableName,
        alias: String = "",
    ): String {
        val aliasClause = if (alias.isNotEmpty()) " AS $alias" else ""
        return """
            SELECT "$COLUMN_NAME_AB_GENERATION_ID"$aliasClause 
            FROM ${tableName.toPrettyString(QUOTE)} 
            LIMIT 1
        """
            .trimIndent()
            .andLog()
    }

    fun createFileFormat(): String {
        return """
            CREATE OR REPLACE FILE FORMAT $STAGE_FORMAT_NAME
            TYPE = 'CSV'
            FIELD_DELIMITER = ','
            RECORD_DELIMITER = '\n'
            SKIP_HEADER = 1
            FIELD_OPTIONALLY_ENCLOSED_BY = '"'
            TRIM_SPACE = TRUE
            ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
            REPLACE_INVALID_CHARACTERS = TRUE
        """
            .trimIndent()
            .andLog()
    }

    private fun buildSnowflakeStageName(tableName: TableName): String {
        return "airbyte_stage_${tableName.name}"
    }

    fun createSnowflakeStage(tableName: TableName): String {
        val stageName = buildSnowflakeStageName(tableName)
        return """
            CREATE OR REPLACE STAGE $stageName
                FILE_FORMAT = my_csv_format;
        """
            .trimIndent()
            .andLog()
    }

    fun putInStage(tableName: TableName, tempFilePath: String): String {
        val stageName = buildSnowflakeStageName(tableName)
        return """
            PUT 'file://$tempFilePath' @$stageName
            AUTO_COMPRESS = TRUE
            OVERWRITE = TRUE
        """
            .trimIndent()
            .andLog()
    }

    fun copyFromStage(tableName: TableName): String {
        val stageName = buildSnowflakeStageName(tableName)

        return """
            COPY INTO ${tableName.toPrettyString(QUOTE)}
            FROM @$stageName
            FILE_FORMAT = $STAGE_FORMAT_NAME
            MATCH_BY_COLUMN_NAME = 'CASE_INSENSITIVE'
            ON_ERROR = 'ABORT_STATEMENT'
            PURGE = TRUE
        """
            .trimIndent()
            .andLog()
    }

    companion object {
        const val QUOTE: String = "\""
        const val STAGE_FORMAT_NAME: String = "airbyte_csv_format"

        fun toDialectType(type: AirbyteType): String =
            when (type) {
                BooleanType -> SnowflakeDataType.BOOLEAN.typeName
                DateType -> SnowflakeDataType.DATE.typeName
                IntegerType -> SnowflakeDataType.INTEGER.typeName
                NumberType -> SnowflakeDataType.NUMBER.typeName
                StringType -> SnowflakeDataType.VARCHAR.typeName
                TimeTypeWithTimezone -> SnowflakeDataType.TIME.typeName
                TimeTypeWithoutTimezone -> SnowflakeDataType.TIME.typeName
                TimestampTypeWithTimezone -> SnowflakeDataType.TIMESTAMP_TZ.typeName
                TimestampTypeWithoutTimezone -> SnowflakeDataType.TIMESTAMP_NTZ.typeName
                is ArrayType,
                ArrayTypeWithoutSchema,
                is ObjectType,
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema -> SnowflakeDataType.VARIANT.typeName
                is UnionType ->
                    if (type.isLegacyUnion) {
                        toDialectType(type.chooseType())
                    } else {
                        SnowflakeDataType.VARIANT.typeName
                    }
                is UnknownType -> SnowflakeDataType.VARIANT.typeName
            }
    }
}
