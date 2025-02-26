/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
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
import io.airbyte.cdk.load.message.Meta
import java.util.UUID
import org.apache.iceberg.Schema
import org.apache.iceberg.types.Type
import org.apache.iceberg.types.Types
import org.apache.iceberg.types.Types.NestedField

class AirbyteTypeToIcebergSchema {

    fun convert(airbyteSchema: AirbyteType, stringifyObjects: Boolean): Type {
        return when (airbyteSchema) {
            is ObjectType -> {
                if (stringifyObjects) {
                    Types.StringType.get()
                } else {
                    Types.StructType.of(
                        *airbyteSchema.properties.entries
                            .map { (name, field) ->
                                if (field.nullable) {
                                    NestedField.optional(
                                        UUID.randomUUID().hashCode(),
                                        name,
                                        convert(field.type, stringifyObjects)
                                    )
                                } else {
                                    NestedField.required(
                                        UUID.randomUUID().hashCode(),
                                        name,
                                        convert(field.type, stringifyObjects)
                                    )
                                }
                            }
                            .toTypedArray()
                    )
                }
            }
            is ArrayType -> {
                val convert = convert(airbyteSchema.items.type, stringifyObjects)
                if (airbyteSchema.items.nullable) {
                    return Types.ListType.ofOptional(UUID.randomUUID().hashCode(), convert)
                }
                return Types.ListType.ofRequired(UUID.randomUUID().hashCode(), convert)
            }
            is BooleanType -> Types.BooleanType.get()
            is DateType -> Types.DateType.get()
            is IntegerType -> Types.LongType.get()
            is NumberType -> Types.DoubleType.get()
            // Schemaless types are converted to string
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
                        convert(airbyteSchema.options.first(), stringifyObjects)
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
        // There's no _airbyte_data field, because we flatten the fields.
        // But we should leave the _airbyte_meta field as an actual object.
        val stringifyObjects = name != Meta.COLUMN_NAME_AB_META
        fields.add(
            NestedField.of(
                id,
                isOptional,
                name,
                icebergTypeConverter.convert(field.type, stringifyObjects = stringifyObjects),
            ),
        )
        if (isPrimaryKey) {
            identifierFields.add(id)
        }
    }
    return Schema(fields, identifierFields)
}

private fun generatedSchemaFieldId() = UUID.randomUUID().hashCode()
