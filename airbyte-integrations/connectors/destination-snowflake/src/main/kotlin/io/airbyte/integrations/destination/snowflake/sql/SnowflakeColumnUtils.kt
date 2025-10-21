/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.sql

import com.google.common.annotations.VisibleForTesting
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
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_LOADED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_DATA
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.snowflake.db.SnowflakeColumnNameGenerator
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import jakarta.inject.Singleton
import kotlin.collections.component1
import kotlin.collections.component2
import kotlin.collections.joinToString
import kotlin.collections.map
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
        columnName = COLUMN_NAME_DATA,
        columnType = "${SnowflakeDataType.VARIANT.typeName} $NOT_NULL"
    )

internal val RAW_COLUMNS =
    listOf(
        ColumnAndType(
            columnName = COLUMN_NAME_AB_LOADED_AT,
            columnType = SnowflakeDataType.TIMESTAMP_TZ.typeName
        ),
        RAW_DATA_COLUMN
    )

@Singleton
class SnowflakeColumnUtils(
    private val snowflakeConfiguration: SnowflakeConfiguration,
    private val snowflakeColumnNameGenerator: SnowflakeColumnNameGenerator,
) {

    @VisibleForTesting
    internal fun defaultColumns(): List<ColumnAndType> =
        if (snowflakeConfiguration.legacyRawTablesOnly) {
            DEFAULT_COLUMNS + RAW_COLUMNS
        } else {
            DEFAULT_COLUMNS
        }

    internal fun formattedDefaultColumns(): List<ColumnAndType> =
        defaultColumns().map {
            ColumnAndType(
                columnName = formatColumnName(it.columnName, false),
                columnType = it.columnType,
            )
        }

    fun getGenerationIdColumnName(): String {
        return if (snowflakeConfiguration.legacyRawTablesOnly) {
            COLUMN_NAME_AB_GENERATION_ID
        } else {
            COLUMN_NAME_AB_GENERATION_ID.toSnowflakeCompatibleName()
        }
    }

    fun getColumnNames(columnNameMapping: ColumnNameMapping): String =
        if (snowflakeConfiguration.legacyRawTablesOnly) {
            getFormattedDefaultColumnNames(true).joinToString(",")
        } else {
            (getFormattedDefaultColumnNames(true) +
                    columnNameMapping.map { (_, actualName) -> actualName.quote() })
                .joinToString(",")
        }

    fun getFormattedDefaultColumnNames(quote: Boolean = false): List<String> =
        defaultColumns().map { formatColumnName(it.columnName, quote) }

    fun getFormattedColumnNames(
        columns: Map<String, FieldType>,
        columnNameMapping: ColumnNameMapping,
        quote: Boolean = true,
    ): List<String> =
        if (snowflakeConfiguration.legacyRawTablesOnly == true) {
            getFormattedDefaultColumnNames(quote)
        } else {
            getFormattedDefaultColumnNames(quote) +
                columns.map { (fieldName, _) ->
                    val columnName = columnNameMapping[fieldName] ?: fieldName
                    if (quote) columnName.quote() else columnName
                }
        }

    fun columnsAndTypes(
        columns: Map<String, FieldType>,
        columnNameMapping: ColumnNameMapping
    ): List<ColumnAndType> =
        if (snowflakeConfiguration.legacyRawTablesOnly == true) {
            formattedDefaultColumns()
        } else {
            formattedDefaultColumns() +
                columns.map { (fieldName, type) ->
                    val columnName = columnNameMapping[fieldName] ?: fieldName
                    val typeName = toDialectType(type.type)
                    ColumnAndType(
                        columnName = columnName,
                        columnType = typeName,
                    )
                }
        }

    fun formatColumnName(
        columnName: String,
        quote: Boolean = true,
    ): String {
        val formattedColumnName =
            if (columnName == COLUMN_NAME_DATA) columnName
            else snowflakeColumnNameGenerator.getColumnName(columnName).displayName
        return if (quote) formattedColumnName.quote() else formattedColumnName
    }

    fun toDialectType(type: AirbyteType): String =
        when (type) {
            // Simple types
            BooleanType -> SnowflakeDataType.BOOLEAN.typeName
            IntegerType -> SnowflakeDataType.NUMBER.typeName
            NumberType -> SnowflakeDataType.FLOAT.typeName
            StringType -> SnowflakeDataType.VARCHAR.typeName

            // Temporal types
            DateType -> SnowflakeDataType.DATE.typeName
            TimeTypeWithTimezone -> SnowflakeDataType.VARCHAR.typeName
            TimeTypeWithoutTimezone -> SnowflakeDataType.TIME.typeName
            TimestampTypeWithTimezone -> SnowflakeDataType.TIMESTAMP_TZ.typeName
            TimestampTypeWithoutTimezone -> SnowflakeDataType.TIMESTAMP_NTZ.typeName

            // Semistructured types
            is ArrayType,
            ArrayTypeWithoutSchema -> SnowflakeDataType.ARRAY.typeName
            is ObjectType,
            ObjectTypeWithEmptySchema,
            ObjectTypeWithoutSchema -> SnowflakeDataType.OBJECT.typeName
            is UnionType -> SnowflakeDataType.VARIANT.typeName
            is UnknownType -> SnowflakeDataType.VARIANT.typeName
        }
}

data class ColumnAndType(val columnName: String, val columnType: String) {
    override fun toString(): String {
        return "${columnName.quote()} $columnType"
    }
}

/**
 * Surrounds the string instance with double quotation marks (e.g. "some string" -> "\"some
 * string\"").
 */
fun String.quote() = "$QUOTE$this$QUOTE"
