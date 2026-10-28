/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.iceberg.parquet

import io.airbyte.cdk.load.command.iceberg.parquet.TimeColumnType
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

class AirbyteTypeToIcebergSchema(private val timeColumnType: TimeColumnType = TimeColumnType.TIME) {

    /**
     * @param forceOptionalFields relax all nested fields for metadata structs and array elements.
     */
    fun convert(
        airbyteSchema: AirbyteType,
        stringifyObjects: Boolean,
        forceOptionalFields: Boolean = false,
    ): Type {
        return when (airbyteSchema) {
            is ObjectType -> {
                if (stringifyObjects) {
                    Types.StringType.get()
                } else {
                    Types.StructType.of(
                        *airbyteSchema.properties.entries
                            .map { (name, field) ->
                                if (forceOptionalFields || field.nullable) {
                                    NestedField.optional(
                                        UUID.randomUUID().hashCode(),
                                        name,
                                        convert(field.type, stringifyObjects, forceOptionalFields),
                                    )
                                } else {
                                    NestedField.required(
                                        UUID.randomUUID().hashCode(),
                                        name,
                                        convert(field.type, stringifyObjects, forceOptionalFields),
                                    )
                                }
                            }
                            .toTypedArray(),
                    )
                }
            }
            is ArrayType -> {
                Types.ListType.ofOptional(
                    UUID.randomUUID().hashCode(),
                    convert(airbyteSchema.items.type, stringifyObjects, forceOptionalFields = true),
                )
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
            is TimeTypeWithoutTimezone ->
                if (timeColumnType == TimeColumnType.STRING) Types.StringType.get()
                else Types.TimeType.get()
            is TimestampTypeWithTimezone -> Types.TimestampType.withZone()
            is TimestampTypeWithoutTimezone -> Types.TimestampType.withoutZone()
            is UnionType -> {
                // We should never get a trivial union, b/c the AirbyteType parser already handles
                // this case.
                // but it costs nothing to have this check here
                if (airbyteSchema.options.size == 1) {
                    return Types.ListType.ofOptional(
                        UUID.randomUUID().hashCode(),
                        convert(
                            airbyteSchema.options.first(),
                            stringifyObjects,
                            forceOptionalFields = true,
                        ),
                    )
                }
                // We stringify nontrivial unions
                return Types.StringType.get()
            }
            is UnknownType -> Types.StringType.get()
        }
    }
}

fun ObjectType.toIcebergSchema(
    primaryKeys: List<List<String>>,
    timeColumnType: TimeColumnType = TimeColumnType.TIME,
): Schema {
    val fields = mutableListOf<NestedField>()
    val identifierFields = mutableSetOf<Int>()
    val identifierFieldNames = primaryKeys.flatten().toSet()
    val icebergTypeConverter = AirbyteTypeToIcebergSchema(timeColumnType)
    this.properties.entries.forEach { (name, field) ->
        val id = generatedSchemaFieldId()
        val isPrimaryKey = identifierFieldNames.contains(name)
        val isOptional = !isPrimaryKey && field.nullable
        // There's no _airbyte_data field, because we flatten the fields.
        // But we should leave the _airbyte_meta field as an actual object.
        val stringifyObjects = name != Meta.COLUMN_NAME_AB_META
        val icebergType =
            if (isPrimaryKey && field.type is NumberType) {
                // Override PK NumberType fields to StringType so they can be used as
                // Iceberg identifier fields (float/double are disallowed as identifiers).
                Types.StringType.get()
            } else {
                icebergTypeConverter.convert(
                    field.type,
                    stringifyObjects = stringifyObjects,
                    forceOptionalFields = name == Meta.COLUMN_NAME_AB_META,
                )
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
