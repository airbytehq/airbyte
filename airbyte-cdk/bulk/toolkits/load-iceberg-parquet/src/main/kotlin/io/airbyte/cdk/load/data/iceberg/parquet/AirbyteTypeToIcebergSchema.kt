/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.iceberg.parquet

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.DateType
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
import java.util.UUID
import org.apache.iceberg.Schema
import org.apache.iceberg.types.Type
import org.apache.iceberg.types.Types
import org.apache.iceberg.types.Types.NestedField

class AirbyteTypeToIcebergSchema {

    companion object {
        /** Default maximum nesting depth for ObjectType → StructType conversion. */
        const val DEFAULT_MAX_STRUCT_DEPTH = 3
    }

    /**
     * Converts an [AirbyteType] to an Iceberg [Type].
     *
     * [ObjectType] instances with defined properties are converted to [Types.StructType] up to
     * [maxDepth] levels of nesting. Beyond that depth, or when properties are empty, they fall back
     * to [Types.StringType] (JSON serialization).
     */
    fun convert(airbyteSchema: AirbyteType, maxDepth: Int = DEFAULT_MAX_STRUCT_DEPTH): Type {
        return when (airbyteSchema) {
            is ObjectType -> {
                if (airbyteSchema.properties.isNotEmpty() && maxDepth > 0) {
                    Types.StructType.of(
                        *airbyteSchema.properties.entries
                            .map { (name, field) ->
                                if (field.nullable) {
                                    NestedField.optional(
                                        UUID.randomUUID().hashCode(),
                                        name,
                                        convert(field.type, maxDepth - 1)
                                    )
                                } else {
                                    NestedField.required(
                                        UUID.randomUUID().hashCode(),
                                        name,
                                        convert(field.type, maxDepth - 1)
                                    )
                                }
                            }
                            .toTypedArray()
                    )
                } else {
                    Types.StringType.get()
                }
            }
            is ArrayType -> {
                val convert = convert(airbyteSchema.items.type, maxDepth)
                if (airbyteSchema.items.nullable) {
                    return Types.ListType.ofOptional(UUID.randomUUID().hashCode(), convert)
                }
                return Types.ListType.ofRequired(UUID.randomUUID().hashCode(), convert)
            }
            is BooleanType -> Types.BooleanType.get()
            is DateType -> Types.DateType.get()
            is IntegerType -> Types.LongType.get()
            is NumberType -> Types.DoubleType.get()
            // Schemaless types are always converted to string
            is ArrayTypeWithoutSchema,
            is ObjectTypeWithEmptySchema,
            is ObjectTypeWithoutSchema -> Types.StringType.get()
            is StringType -> Types.StringType.get()
            is TimeTypeWithTimezone,
            is TimeTypeWithoutTimezone -> Types.TimeType.get()
            is TimestampTypeWithTimezone -> Types.TimestampType.withZone()
            is TimestampTypeWithoutTimezone -> Types.TimestampType.withoutZone()
            is UnionType -> {
                // We should never get a trivial union, b/c the AirbyteType parser already handles
                // this case.
                // but it costs nothing to have this check here
                if (airbyteSchema.options.size == 1) {
                    return Types.ListType.ofOptional(
                        UUID.randomUUID().hashCode(),
                        convert(airbyteSchema.options.first(), maxDepth)
                    )
                }
                // We stringify nontrivial unions
                return Types.StringType.get()
            }
            is UnknownType -> Types.StringType.get()
        }
    }
}

fun ObjectType.toIcebergSchema(primaryKeys: List<List<String>>): Schema {
    val fields = mutableListOf<NestedField>()
    val identifierFields = mutableSetOf<Int>()
    val identifierFieldNames = primaryKeys.flatten().toSet()
    val icebergTypeConverter = AirbyteTypeToIcebergSchema()
    this.properties.entries.forEach { (name, field) ->
        val id = generatedSchemaFieldId()
        val isPrimaryKey = identifierFieldNames.contains(name)
        val isOptional = !isPrimaryKey && field.nullable
        val icebergType =
            if (isPrimaryKey && field.type is NumberType) {
                // Override PK NumberType fields to StringType so they can be used as
                // Iceberg identifier fields (float/double are disallowed as identifiers).
                Types.StringType.get()
            } else {
                icebergTypeConverter.convert(field.type)
            }
        fields.add(
            NestedField.builder()
                .withId(id)
                .isOptional(isOptional)
                .withName(name)
                .ofType(icebergType)
                .build(),
        )
        // Identifier fields must be primitive types, and cannot be float/double.
        if (
            isPrimaryKey &&
                icebergType.isPrimitiveType &&
                icebergType != Types.DoubleType.get() &&
                icebergType != Types.FloatType.get()
        ) {
            identifierFields.add(id)
        }
    }
    return Schema(fields, identifierFields)
}

private fun generatedSchemaFieldId() = UUID.randomUUID().hashCode()
