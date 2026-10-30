/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.schema

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
import io.airbyte.integrations.destination.databricks.spec.DatabricksConfiguration
import jakarta.inject.Singleton

/**
 * Key Databricks behaviors:
 * - Object names (tables, schemas, catalogs) are **lowercased** by Databricks
 * - Column names **preserve casing**, so we do NOT lowercase them.
 */
@Singleton
class DatabricksTableSchemaMapper(
    private val config: DatabricksConfiguration,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : TableSchemaMapper {

    override fun toFinalTableName(desc: DestinationStream.Descriptor): TableName {
        // Databricks downcases all object names (tables, schemas, catalogs).
        val namespace = (desc.namespace ?: config.schema).toDatabricksCompatibleNameLowercase()
        val name = desc.name.toDatabricksCompatibleNameLowercase()
        return TableName(namespace, name)
    }

    override fun toTempTableName(tableName: TableName): TableName {
        return tempTableNameGenerator.generate(tableName)
    }

    override fun toColumnName(name: String): String {
        return name.toDatabricksCompatibleName()
    }

    override fun toColumnType(fieldType: FieldType): ColumnType {
        val databricksType =
            when (fieldType.type) {
                // Primitive types
                BooleanType -> BOOLEAN
                IntegerType -> LONG
                NumberType -> DECIMAL
                StringType -> STRING

                // Temporal types
                DateType -> DATE
                TimestampTypeWithTimezone -> TIMESTAMP
                TimestampTypeWithoutTimezone -> TIMESTAMP_NTZ

                // Not implemented: Time type is supported in DBR 18.3+ (05/2026) with limitations
                TimeTypeWithTimezone,
                TimeTypeWithoutTimezone -> STRING

                // Not implemented: VARIANT(Semi-structured) type is still in Public Preview
                is ArrayType,
                ArrayTypeWithoutSchema,
                is ObjectType,
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema,

                // Other types
                is UnionType,
                is UnknownType -> STRING
            }

        return ColumnType(databricksType, fieldType.nullable)
    }

    /** Databricks preserves column name casing */
    override fun colsConflict(a: String, b: String): Boolean = a == b

    companion object {
        const val BOOLEAN = "BOOLEAN"
        const val LONG = "LONG"
        const val DECIMAL = "DECIMAL(38, 10)"
        const val STRING = "STRING"
        const val DATE = "DATE"
        const val TIMESTAMP = "TIMESTAMP"
        const val TIMESTAMP_NTZ = "TIMESTAMP_NTZ"
    }
}
