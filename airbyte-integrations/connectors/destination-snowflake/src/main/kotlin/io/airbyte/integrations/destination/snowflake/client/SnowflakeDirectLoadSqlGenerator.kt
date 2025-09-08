/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.client

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
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.cdk.load.orchestration.db.TableName
import jakarta.inject.Singleton

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

    fun overwriteTable(sourceTableName: TableName, targetTableName: TableName): String {
        TODO("Not yet implemented")
    }

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
    ): Sql {
        TODO("Not yet implemented")
    }

    fun dropTable(tableName: TableName): String {
        return "DROP TABLE IF EXISTS \"${tableName.namespace}\".\"${tableName.name}\"".andLog()
    }

    companion object {
        const val QUOTE: String = "\""

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
