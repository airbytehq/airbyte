/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.schema

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
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.schema.TableSchemaMapper
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.firebolt.config.FireboltConfiguration
import io.airbyte.integrations.destination.firebolt.sql.FireboltDataType
import io.airbyte.integrations.destination.firebolt.sql.FireboltSqlEscapeUtils
import jakarta.inject.Singleton

/** Maps Airbyte stream schemas to Firebolt table names, column names, and column types. */
@Singleton
class FireboltTableSchemaMapper(
    private val config: FireboltConfiguration,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : TableSchemaMapper {

    override fun toFinalTableName(desc: DestinationStream.Descriptor): TableName {
        val namespace = desc.namespace ?: config.schema
        return TableName(
            namespace = namespace.toCompatibleName(),
            name = desc.name.toCompatibleName(),
        )
    }

    override fun toTempTableName(tableName: TableName): TableName =
        tempTableNameGenerator.generate(tableName)

    override fun toColumnName(name: String): String = name.toCompatibleName()

    override fun toColumnType(fieldType: FieldType): ColumnType {
        val fireboltType =
            when (fieldType.type) {
                BooleanType -> FireboltDataType.BOOLEAN.typeName
                IntegerType -> FireboltDataType.BIGINT.typeName
                NumberType -> FireboltDataType.DOUBLE_PRECISION.typeName
                StringType -> FireboltDataType.TEXT.typeName

                DateType -> FireboltDataType.DATE.typeName
                TimeTypeWithoutTimezone,
                TimeTypeWithTimezone -> FireboltDataType.TEXT.typeName
                TimestampTypeWithoutTimezone -> FireboltDataType.TIMESTAMP.typeName
                TimestampTypeWithTimezone -> FireboltDataType.TIMESTAMPTZ.typeName

                is ArrayType,
                ArrayTypeWithoutSchema,
                is UnknownType -> FireboltDataType.TEXT.typeName

                is ObjectType,
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema -> FireboltDataType.JSON.typeName

                is UnionType -> {
                    val union = fieldType.type as UnionType
                    val nonNull = union.options.filter { it !is UnknownType }
                    if (nonNull.size == 1) {
                        toColumnType(FieldType(nonNull.first(), fieldType.nullable)).type
                    } else {
                        FireboltDataType.TEXT.typeName
                    }
                }
            }

        return ColumnType(fireboltType, fieldType.nullable)
    }

    private fun String.toCompatibleName(): String =
        this
}
