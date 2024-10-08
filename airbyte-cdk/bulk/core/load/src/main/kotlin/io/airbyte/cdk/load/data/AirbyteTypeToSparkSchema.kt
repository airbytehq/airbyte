/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import org.apache.spark.sql.types.DataType
import org.apache.spark.sql.types.DecimalType
import org.apache.spark.sql.types.Metadata
import org.apache.spark.sql.types.StructField
import org.apache.spark.sql.types.StructType

class AirbyteTypeToSparkSchema {
    fun convert(schema: AirbyteType): StructType = convertInner(schema) as StructType

    private fun convertInner(schema: AirbyteType): DataType =
        when (schema) {
            is ArrayType -> {
                org.apache.spark.sql.types.ArrayType(
                    convertInner(schema.items.type),
                    schema.items.nullable
                )
            }
            is BooleanType -> {
                org.apache.spark.sql.types.DataTypes.BooleanType
            }
            is IntegerType -> {
                org.apache.spark.sql.types.DataTypes.LongType
            }
            is NumberType -> {
                DecimalType(38, 18)
            }
            is ObjectType -> {
                StructType(
                    schema.properties
                        .map { (name, field) ->
                            StructField(
                                name,
                                convertInner(field.type),
                                field.nullable,
                                Metadata.empty()
                            )
                        }
                        .toTypedArray()
                )
            }
            is StringType -> {
                org.apache.spark.sql.types.DataTypes.StringType
            }
            is DateType -> {
                org.apache.spark.sql.types.DataTypes.DateType
            }
            is TimestampType -> {
                org.apache.spark.sql.types.DataTypes.TimestampType
            }
            is TimeType -> {
                org.apache.spark.sql.types.DataTypes.StringType
            }
            is UnknownType -> {
                throw IllegalArgumentException("Unknown type: ${schema.what}")
            }
            is ArrayTypeWithoutSchema ->
                org.apache.spark.sql.types.ArrayType(
                    org.apache.spark.sql.types.ObjectType(Any::class.java),
                    true
                )
            is NullType -> org.apache.spark.sql.types.DataTypes.NullType
            is ObjectTypeWithEmptySchema -> org.apache.spark.sql.types.ObjectType(Any::class.java)
            is ObjectTypeWithoutSchema -> org.apache.spark.sql.types.ObjectType(Any::class.java)
            is UnionType -> TODO()
        }
}
