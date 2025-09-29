/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.sql

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
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
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import jakarta.inject.Singleton
import kotlin.collections.component1
import kotlin.collections.component2
import kotlin.collections.joinToString
import kotlin.collections.plus

internal const val NOT_NULL = "NOT NULL"

internal val DEFAULT_COLUMNS =
    listOf(
        ColumnAndType(
            columnName = COLUMN_NAME_AB_RAW_ID,
            columnType = "${SnowflakeDataType.VARCHAR.typeName} $NOT_NULL"
        ),
        ColumnAndType(
            columnName = COLUMN_NAME_AB_EXTRACTED_AT,
            columnType = "${SnowflakeDataType.TIMESTAMP_TZ.typeName} $NOT_NULL"
        ),
        ColumnAndType(
            columnName = COLUMN_NAME_AB_META,
            columnType = "${SnowflakeDataType.VARIANT.typeName} $NOT_NULL"
        ),
        ColumnAndType(
            columnName = COLUMN_NAME_AB_GENERATION_ID,
            columnType = SnowflakeDataType.NUMBER.typeName
        ),
    )

internal val RAW_DATA_COLUMN =
    ColumnAndType(
        columnName = Meta.COLUMN_NAME_DATA,
        columnType = "${SnowflakeDataType.VARCHAR.typeName} $NOT_NULL"
    )

@Singleton
class SnowflakeColumnUtils(
    private val snowflakeConfiguration: SnowflakeConfiguration,
) {

    fun defaultColumns(): List<ColumnAndType> =
        if (snowflakeConfiguration.legacyRawTablesOnly == true) {
            DEFAULT_COLUMNS + listOf(RAW_DATA_COLUMN)
        } else {
            DEFAULT_COLUMNS
        }

    fun getColumnNames(columnNameMapping: ColumnNameMapping): String =
        if (snowflakeConfiguration.legacyRawTablesOnly == true) {
            defaultColumns().map { it.columnName }.joinToString(",") { "\"$it\"" }
        } else {
            (defaultColumns().map { it.columnName } +
                    columnNameMapping.map { (_, actualName) -> actualName })
                .joinToString(",") { "\"$it\"" }
        }

    fun columnsAndTypes(
        columns: Map<String, FieldType>,
        columnNameMapping: ColumnNameMapping
    ): List<ColumnAndType> =
        if (snowflakeConfiguration.legacyRawTablesOnly == true) {
            defaultColumns()
        } else {
            defaultColumns() +
                columns.map { (fieldName, type) ->
                    val columnName = columnNameMapping[fieldName] ?: fieldName
                    val typeName = toDialectType(type.type)
                    ColumnAndType(columnName = columnName, columnType = typeName)
                }
        }

    fun toDialectType(type: AirbyteType): String =
        when (type) {
            BooleanType -> SnowflakeDataType.BOOLEAN.typeName
            DateType -> SnowflakeDataType.DATE.typeName
            IntegerType -> SnowflakeDataType.NUMBER.typeName
            NumberType -> SnowflakeDataType.FLOAT.typeName
            StringType -> SnowflakeDataType.VARCHAR.typeName
            TimeTypeWithTimezone -> SnowflakeDataType.VARCHAR.typeName
            TimeTypeWithoutTimezone -> SnowflakeDataType.TIME.typeName
            TimestampTypeWithTimezone -> SnowflakeDataType.TIMESTAMP_TZ.typeName
            TimestampTypeWithoutTimezone -> SnowflakeDataType.TIMESTAMP_NTZ.typeName
            is ArrayType,
            ArrayTypeWithoutSchema,
            is ObjectType,
            ObjectTypeWithEmptySchema,
            ObjectTypeWithoutSchema,
            is UnionType -> SnowflakeDataType.VARIANT.typeName
            is UnknownType -> SnowflakeDataType.VARCHAR.typeName
        }
}

data class ColumnAndType(val columnName: String, val columnType: String) {
    override fun toString(): String {
        return "\"${columnName.toSnowflakeCompatibleName()}\" $columnType"
    }
}
