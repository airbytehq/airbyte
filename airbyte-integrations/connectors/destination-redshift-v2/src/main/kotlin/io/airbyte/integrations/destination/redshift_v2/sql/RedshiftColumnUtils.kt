/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.sql

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
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.table.ColumnNameMapping
import jakarta.inject.Singleton

internal const val NOT_NULL = "NOT NULL"

internal val DEFAULT_COLUMNS =
    listOf(
        ColumnAndType(
            columnName = COLUMN_NAME_AB_RAW_ID,
            columnType = "${RedshiftDataType.VARCHAR.typeName} $NOT_NULL"
        ),
        ColumnAndType(
            columnName = COLUMN_NAME_AB_EXTRACTED_AT,
            columnType = "${RedshiftDataType.TIMESTAMPTZ.typeName} $NOT_NULL"
        ),
        ColumnAndType(
            columnName = COLUMN_NAME_AB_META,
            columnType = "${RedshiftDataType.SUPER.typeName} $NOT_NULL"
        ),
        ColumnAndType(
            columnName = COLUMN_NAME_AB_GENERATION_ID,
            columnType = RedshiftDataType.BIGINT.typeName
        ),
    )

@Singleton
class RedshiftColumnUtils {

    fun getGenerationIdColumnName(): String = COLUMN_NAME_AB_GENERATION_ID

    fun getColumnNames(columnNameMapping: ColumnNameMapping): String =
        (getFormattedDefaultColumnNames(true) +
                columnNameMapping.map { (_, actualName) -> actualName.quote() })
            .joinToString(",")

    fun getFormattedDefaultColumnNames(quote: Boolean = false): List<String> =
        DEFAULT_COLUMNS.map { if (quote) it.columnName.quote() else it.columnName }

    fun getFormattedColumnNames(
        columns: Map<String, FieldType>,
        columnNameMapping: ColumnNameMapping,
        quote: Boolean = true,
    ): List<String> =
        getFormattedDefaultColumnNames(quote) +
            columns.map { (fieldName, _) ->
                val columnName = columnNameMapping[fieldName] ?: fieldName
                if (quote) columnName.quote() else columnName
            }

    fun columnsAndTypes(
        columns: Map<String, FieldType>,
        columnNameMapping: ColumnNameMapping
    ): List<ColumnAndType> =
        formattedDefaultColumns() +
            columns.map { (fieldName, type) ->
                val columnName = columnNameMapping[fieldName] ?: fieldName
                val typeName = toDialectType(type.type)
                ColumnAndType(
                    columnName = columnName,
                    columnType = if (type.nullable) typeName else "$typeName $NOT_NULL",
                )
            }

    private fun formattedDefaultColumns(): List<ColumnAndType> =
        DEFAULT_COLUMNS.map {
            ColumnAndType(
                columnName = it.columnName,
                columnType = it.columnType,
            )
        }

    fun toDialectType(type: AirbyteType): String =
        when (type) {
            // Simple types
            BooleanType -> RedshiftDataType.BOOLEAN.typeName
            IntegerType -> RedshiftDataType.BIGINT.typeName
            NumberType -> RedshiftDataType.DOUBLE.typeName
            StringType -> RedshiftDataType.VARCHAR.typeName

            // Temporal types
            DateType -> RedshiftDataType.DATE.typeName
            TimeTypeWithTimezone ->
                RedshiftDataType.VARCHAR.typeName // Redshift doesn't have TIME WITH TZ
            TimeTypeWithoutTimezone -> RedshiftDataType.TIME.typeName
            TimestampTypeWithTimezone -> RedshiftDataType.TIMESTAMPTZ.typeName
            TimestampTypeWithoutTimezone -> RedshiftDataType.TIMESTAMP.typeName

            // Semistructured types - Redshift uses SUPER for JSON
            is ArrayType,
            ArrayTypeWithoutSchema -> RedshiftDataType.SUPER.typeName
            is ObjectType,
            ObjectTypeWithEmptySchema,
            ObjectTypeWithoutSchema -> RedshiftDataType.SUPER.typeName
            is UnionType -> RedshiftDataType.SUPER.typeName
            is UnknownType -> RedshiftDataType.SUPER.typeName
        }
}

data class ColumnAndType(val columnName: String, val columnType: String) {
    override fun toString(): String {
        return "${columnName.quote()} $columnType"
    }
}
