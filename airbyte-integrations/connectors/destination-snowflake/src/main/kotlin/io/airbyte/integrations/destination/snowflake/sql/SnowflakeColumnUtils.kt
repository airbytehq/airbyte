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
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import jakarta.inject.Singleton
import kotlin.collections.component1
import kotlin.collections.component2

internal val DEFAULT_COLUMNS =
    listOf(
        ColumnAndType(columnName = COLUMN_NAME_AB_RAW_ID, columnType = "VARCHAR NOT NULL"),
        ColumnAndType(
            columnName = COLUMN_NAME_AB_EXTRACTED_AT,
            columnType = "TIMESTAMP_TZ NOT NULL"
        ),
        ColumnAndType(columnName = COLUMN_NAME_AB_META, columnType = "VARIANT NOT NULL"),
        ColumnAndType(columnName = COLUMN_NAME_AB_GENERATION_ID, columnType = "NUMBER"),
    )

@Singleton
class SnowflakeColumnUtils {

    fun columnsAndTypes(
        columns: Map<String, FieldType>,
        columnNameMapping: ColumnNameMapping
    ): List<ColumnAndType> =
        DEFAULT_COLUMNS +
            columns.map { (fieldName, type) ->
                val columnName = columnNameMapping[fieldName] ?: fieldName
                val typeName = toDialectType(type.type)
                ColumnAndType(columnName = columnName, columnType = typeName)
            }

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

data class ColumnAndType(val columnName: String, val columnType: String) {
    override fun toString(): String {
        return "\"$columnName\" $columnType"
    }
}
