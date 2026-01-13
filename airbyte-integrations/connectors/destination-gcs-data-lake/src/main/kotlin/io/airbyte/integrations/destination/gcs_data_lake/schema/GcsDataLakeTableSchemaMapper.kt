/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.schema

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.*
import io.airbyte.cdk.load.schema.TableSchemaMapper
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import jakarta.inject.Singleton

/**
 * Maps stream schemas to BigLake-compatible table schemas.
 *
 * BigLake external tables have strict naming requirements:
 * - Only alphanumeric characters (a-z, A-Z, 0-9) and underscores (_)
 *
 * This mapper uses [Transformations.toAlphanumericAndUnderscore] to ensure all names meet these
 * requirements.
 */
@Singleton
class GcsDataLakeTableSchemaMapper(
    private val config: GcsDataLakeConfiguration,
    private val tempTableNameGenerator: TempTableNameGenerator
) : TableSchemaMapper {

    override fun toFinalTableName(desc: DestinationStream.Descriptor): TableName {
        val namespace =
            Transformations.toAlphanumericAndUnderscore(desc.namespace ?: config.namespace)
        val name = Transformations.toAlphanumericAndUnderscore(desc.name)
        return TableName(namespace, name)
    }

    override fun toTempTableName(tableName: TableName): TableName {
        return tempTableNameGenerator.generate(tableName)
    }

    override fun toColumnName(name: String): String {
        return Transformations.toAlphanumericAndUnderscore(name)
    }

    override fun toColumnType(fieldType: FieldType): ColumnType {
        // Map Airbyte field types to BigLake/Parquet column types
        // BigLake uses Parquet as the underlying format
        val parquetType =
            when (fieldType.type) {
                BooleanType -> "BOOL"
                DateType -> "DATE"
                IntegerType -> "INT64"
                NumberType -> "FLOAT64"
                StringType -> "STRING"
                TimeTypeWithTimezone,
                TimeTypeWithoutTimezone -> "STRING" // Store times as strings
                TimestampTypeWithTimezone,
                TimestampTypeWithoutTimezone -> "TIMESTAMP"
                is ArrayType,
                ArrayTypeWithoutSchema -> "STRING" // Arrays as JSON strings
                is UnionType,
                is UnknownType -> "STRING"
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema,
                is ObjectType -> "STRING" // Objects as JSON strings
            }

        return ColumnType(parquetType, fieldType.nullable)
    }
}
