/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.schema

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
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
import io.airbyte.cdk.load.data.Transformations.Companion.toAlphanumericAndUnderscore
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.schema.TableSchemaMapper
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.clickhouse.client.ClickhouseSqlGenerator.Companion.DATETIME_WITH_PRECISION
import io.airbyte.integrations.destination.clickhouse.client.ClickhouseSqlGenerator.Companion.DECIMAL_WITH_PRECISION_AND_SCALE
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
import jakarta.inject.Singleton
import java.util.UUID

@Singleton
class ClickhouseTableSchemaMapper(
    private val config: ClickhouseConfiguration,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : TableSchemaMapper {
    override fun toFinalTableName(desc: DestinationStream.Descriptor): TableName {
        val namespace = (desc.namespace ?: config.resolvedDatabase).toClickHouseCompatibleName()
        val name = desc.name.toClickHouseCompatibleName()
        return TableName(namespace, name)
    }

    override fun toTempTableName(tableName: TableName): TableName {
        return tempTableNameGenerator.generate(tableName)
    }

    override fun toColumnName(name: String): String {
        return name.toClickHouseCompatibleName()
    }

    override fun toColumnType(fieldType: FieldType): ColumnType {
        // Map Airbyte field types to ClickHouse column types
        val clickhouseType = when (fieldType.type) {
            BooleanType -> "Bool"
            DateType -> "Date32"
            IntegerType -> "Int64"
            NumberType -> DECIMAL_WITH_PRECISION_AND_SCALE
            StringType -> "String"
            TimeTypeWithTimezone -> "String"
            TimeTypeWithoutTimezone -> "String"
            TimestampTypeWithTimezone,
            TimestampTypeWithoutTimezone -> DATETIME_WITH_PRECISION
            is ArrayType,
            ArrayTypeWithoutSchema,
            is UnionType,
            is UnknownType -> "String"
            ObjectTypeWithEmptySchema,
            ObjectTypeWithoutSchema,
            is ObjectType -> {
                if (config.enableJson) {
                    "JSON"
                } else {
                    "String"
                }
            }
        }
        
        // Apply nullability
        val finalType = if (fieldType.nullable) {
            "Nullable($clickhouseType)"
        } else {
            clickhouseType
        }
        
        return ColumnType(finalType, fieldType.nullable)
    }
}

/**
 * Transforms a string to be compatible with ClickHouse table and column names.
 *
 * @return The transformed string suitable for ClickHouse identifiers.
 */
fun String.toClickHouseCompatibleName(): String {
    // 1. Replace any character that is not a letter,
    //    a digit (0-9), or an underscore (_) with a single underscore.
    var transformed = toAlphanumericAndUnderscore(this)

    // 2. Ensure the identifier does not start with a digit.
    //    If it starts with a digit, prepend an underscore.
    if (transformed.isNotEmpty() && transformed[0].isDigit()) {
        transformed = "_$transformed"
    }

    // 3.Do not allow empty strings.
    if (transformed.isEmpty()) {
        return "default_name_${UUID.randomUUID()}" // A fallback name if the input results in an
        // empty string
    }

    return transformed
}
