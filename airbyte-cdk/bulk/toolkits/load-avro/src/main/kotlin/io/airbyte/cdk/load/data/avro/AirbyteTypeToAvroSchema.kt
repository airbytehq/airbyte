/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.avro

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
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
import io.airbyte.cdk.load.data.Transformations
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.message.Meta
import org.apache.avro.LogicalTypes
import org.apache.avro.Schema
import org.apache.avro.SchemaBuilder

class AirbyteTypeToAvroSchema {
    fun convert(airbyteSchema: AirbyteType, path: List<String>): Schema {
        return try {
            when (airbyteSchema) {
                is ObjectType -> {
                    val recordName = Transformations.toAvroSafeName(path.last())
                    val recordNamespace = path.take(path.size - 1).reversed().joinToString(".")
                    val namespaceMangled = Transformations.toAvroSafeNamespace(recordNamespace)
                    val builder =
                        SchemaBuilder.record(recordName).namespace(namespaceMangled).fields()
                    airbyteSchema.properties.entries
                        .fold(builder) { acc, (name, field) ->
                            val propertySchema =
                                when (name) {
                                    Meta.COLUMN_NAME_AB_EXTRACTED_AT ->
                                        LogicalTypes.timestampMillis()
                                            .addToSchema(Schema.create(Schema.Type.LONG))
                                    Meta.COLUMN_NAME_AB_RAW_ID ->
                                        LogicalTypes.uuid()
                                            .addToSchema(Schema.create(Schema.Type.STRING))
                                    else -> {
                                        val converted = convert(field.type, path + name)
                                        maybeMakeNullable(field, converted)
                                    }
                                }
                            val nameMangled = Transformations.toAvroSafeName(name)
                            acc.name(nameMangled).type(propertySchema).let {
                                if (field.nullable) {
                                    it.withDefault(null)
                                } else {
                                    it.noDefault()
                                }
                            }
                        }
                        .endRecord()
                }
                is ArrayType -> {
                    val converted = convert(airbyteSchema.items.type, path + "items")
                    val itemsSchema = maybeMakeNullable(airbyteSchema.items, converted)
                    SchemaBuilder.array().items(itemsSchema)
                }
                is BooleanType -> SchemaBuilder.builder().booleanType()
                is IntegerType -> SchemaBuilder.builder().longType()
                is NumberType -> SchemaBuilder.builder().doubleType()
                is StringType -> SchemaBuilder.builder().stringType()

                // HACK: After upstream validation, UnknownType is sentinel for NullType
                is UnknownType -> SchemaBuilder.builder().nullType()
                is ObjectTypeWithEmptySchema,
                is ObjectTypeWithoutSchema,
                is ArrayTypeWithoutSchema -> SchemaBuilder.builder().stringType()
                is DateType -> {
                    val schema = SchemaBuilder.builder().intType()
                    LogicalTypes.date().addToSchema(schema)
                }
                is TimeTypeWithTimezone,
                is TimeTypeWithoutTimezone -> {
                    val schema = SchemaBuilder.builder().longType()
                    LogicalTypes.timeMicros().addToSchema(schema)
                }
                is TimestampTypeWithTimezone,
                is TimestampTypeWithoutTimezone -> {
                    val schema = SchemaBuilder.builder().longType()
                    LogicalTypes.timestampMicros().addToSchema(schema)
                }
                is UnionType -> Schema.createUnion(airbyteSchema.options.map { convert(it, path) })
            }
        } catch (e: Exception) {
            throw IllegalArgumentException("Failed to convert $airbyteSchema at $path", e)
        }
    }

    private fun maybeMakeNullable(
        airbyteSchema: FieldType,
        avroSchema: Schema,
    ): Schema =
        if (airbyteSchema.nullable && avroSchema.type != Schema.Type.UNION) {
            if (avroSchema.type == Schema.Type.NULL) {
                avroSchema
            } else {
                SchemaBuilder.unionOf().nullType().and().type(avroSchema).endUnion()
            }
        } else if (airbyteSchema.nullable && avroSchema.type == Schema.Type.UNION) {
            avroSchema.types
                .fold(SchemaBuilder.unionOf().nullType()) { acc, type -> acc.and().type(type) }
                .endUnion()
        } else {
            avroSchema
        }
}

fun ObjectType.toAvroSchema(stream: DestinationStream.Descriptor): Schema {
    val path = listOf(stream.namespace ?: "default", stream.name)
    return AirbyteTypeToAvroSchema().convert(this, path)
}
