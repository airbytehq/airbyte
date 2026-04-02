/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.schema

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.schema.TableSchemaMapper
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.TempTableNameGenerator
import jakarta.inject.Singleton

/**
 * Maps stream schemas to Glue-compatible table schemas.
 *
 * AWS Glue and downstream engines (e.g. Snowflake, Athena) require lowercase identifiers:
 * - Only alphanumeric characters (a-z, 0-9) and underscores (_)
 * - All lowercase
 *
 * This mapper uses [Transformations.toAlphanumericAndUnderscore] and lowercases the result
 * to ensure all names meet these requirements.
 */
@Singleton
class S3DataLakeTableSchemaMapper(
    private val tempTableNameGenerator: TempTableNameGenerator
) : TableSchemaMapper {

    override fun toFinalTableName(desc: DestinationStream.Descriptor): TableName {
        val namespace =
            Transformations.toAlphanumericAndUnderscore(desc.namespace ?: "").lowercase()
        val name = Transformations.toAlphanumericAndUnderscore(desc.name).lowercase()
        return TableName(namespace, name)
    }

    override fun toTempTableName(tableName: TableName): TableName {
        return tempTableNameGenerator.generate(tableName)
    }

    override fun toColumnName(name: String): String {
        return Transformations.toAlphanumericAndUnderscore(name).lowercase()
    }

    override fun toColumnType(fieldType: FieldType): ColumnType {
        val parquetType =
            when (fieldType.type) {
                BooleanType -> "BOOL"
                DateType -> "DATE"
                IntegerType -> "INT64"
                NumberType -> "FLOAT64"
                StringType -> "STRING"
                TimeTypeWithTimezone,
                TimeTypeWithoutTimezone -> "STRING"
                TimestampTypeWithTimezone,
                TimestampTypeWithoutTimezone -> "TIMESTAMP"
                is ArrayType,
                ArrayTypeWithoutSchema -> "STRING"
                is UnionType,
                is UnknownType -> "STRING"
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema,
                is ObjectType -> "STRING"
            }

        return ColumnType(parquetType, fieldType.nullable)
    }
}
