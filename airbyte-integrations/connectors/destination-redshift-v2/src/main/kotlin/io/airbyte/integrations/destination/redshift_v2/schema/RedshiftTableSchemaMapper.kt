/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.schema

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
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2Configuration
import io.airbyte.integrations.destination.redshift_v2.sql.RedshiftDataType
import jakarta.inject.Singleton

@Singleton
class RedshiftTableSchemaMapper(
    private val config: RedshiftV2Configuration,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : TableSchemaMapper {

    override fun toFinalTableName(desc: DestinationStream.Descriptor): TableName {
        val namespace = (desc.namespace ?: config.schema).toRedshiftCompatibleName()
        val name = desc.name.toRedshiftCompatibleName()
        return TableName(namespace, name)
    }

    override fun toTempTableName(tableName: TableName): TableName {
        return tempTableNameGenerator.generate(tableName)
    }

    override fun toColumnName(name: String): String {
        return name.toRedshiftCompatibleName()
    }

    override fun toColumnType(fieldType: FieldType): ColumnType {
        val redshiftType =
            when (fieldType.type) {
                BooleanType -> RedshiftDataType.BOOLEAN.typeName
                IntegerType -> RedshiftDataType.BIGINT.typeName
                NumberType -> RedshiftDataType.DOUBLE.typeName
                StringType -> RedshiftDataType.VARCHAR.typeName
                DateType -> RedshiftDataType.DATE.typeName
                TimeTypeWithTimezone,
                TimeTypeWithoutTimezone -> RedshiftDataType.TIME.typeName
                TimestampTypeWithTimezone -> RedshiftDataType.TIMESTAMPTZ.typeName
                TimestampTypeWithoutTimezone -> RedshiftDataType.TIMESTAMP.typeName
                is ArrayType,
                ArrayTypeWithoutSchema -> RedshiftDataType.SUPER.typeName
                is ObjectType,
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema -> RedshiftDataType.SUPER.typeName
                is UnionType,
                is UnknownType -> RedshiftDataType.SUPER.typeName
            }
        return ColumnType(redshiftType, fieldType.nullable)
    }
}

/**
 * Transforms a string to be compatible with Redshift identifiers. Redshift identifiers are
 * case-insensitive and stored as lowercase. Max identifier length is 127 characters.
 */
fun String.toRedshiftCompatibleName(): String {
    // Redshift identifiers: lowercase, alphanumeric + underscore
    var transformed = this.lowercase().replace(Regex("[^a-z0-9_]"), "_")

    // Ensure the identifier does not start with a digit
    if (transformed.isNotEmpty() && transformed[0].isDigit()) {
        transformed = "_$transformed"
    }

    // Redshift max identifier length is 127
    return transformed.take(127)
}
