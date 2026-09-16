/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.schema

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
import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import io.airbyte.integrations.destination.redshift.sql.RedshiftDataType
import jakarta.inject.Singleton

/** Maps Airbyte stream schemas to Redshift-specific table names, column names, and column types. */
@Singleton
class RedshiftTableSchemaMapper(
    private val config: RedshiftConfiguration,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : TableSchemaMapper {

    override fun toFinalTableName(desc: DestinationStream.Descriptor): TableName {
        val namespace = desc.namespace ?: config.schema
        return TableName(
            namespace = namespace.toRedshiftCompatibleName(),
            name = desc.name.toRedshiftCompatibleName(),
        )
    }

    override fun toTempTableName(tableName: TableName): TableName =
        tempTableNameGenerator.generate(tableName)

    override fun toColumnName(name: String): String = name.toRedshiftCompatibleName()

    override fun toColumnType(fieldType: FieldType): ColumnType {
        val redshiftType =
            when (fieldType.type) {
                // Simple types
                BooleanType -> RedshiftDataType.BOOLEAN.typeName
                IntegerType -> RedshiftDataType.BIGINT.typeName
                NumberType -> RedshiftDataType.NUMERIC.typeName
                StringType -> RedshiftDataType.VARCHAR.typeName

                // Temporal types
                DateType -> RedshiftDataType.DATE.typeName
                TimeTypeWithTimezone -> RedshiftDataType.TIMETZ.typeName
                TimeTypeWithoutTimezone -> RedshiftDataType.TIME.typeName
                TimestampTypeWithTimezone -> RedshiftDataType.TIMESTAMPTZ.typeName
                TimestampTypeWithoutTimezone -> RedshiftDataType.TIMESTAMP.typeName
                is UnionType,
                is UnknownType -> RedshiftDataType.VARCHAR.typeName

                // Semi-structured types (all map to Redshift SUPER)
                is ArrayType,
                ArrayTypeWithoutSchema,
                is ObjectType,
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema -> RedshiftDataType.SUPER.typeName
            }

        return ColumnType(redshiftType, fieldType.nullable)
    }
}
