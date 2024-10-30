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
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NullType
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
import org.apache.avro.LogicalTypes
import org.apache.avro.Schema
import org.apache.avro.SchemaBuilder

class AirbyteTypeToAvroSchema {
    fun convert(airbyteSchema: AirbyteType, path: List<String>): Schema {
        return when (airbyteSchema) {
            is ObjectType -> {
                val name = path.last()
                val namespace = path.take(path.size - 1).reversed().joinToString(".")
                val builder = SchemaBuilder.record(name).namespace(namespace).fields()
                airbyteSchema.properties.entries
                    .fold(builder) { acc, (name, field) ->
                        // NOTE: We will not support nullable at this stage.
                        // All nullables should have been converted to union[this, null] upstream
                        // TODO: Enforce this
                        acc.name(name).type(convert(field.type, path + name)).noDefault()
                    }
                    .endRecord()
            }
            is ArrayType -> {
                SchemaBuilder.array().items(convert(airbyteSchema.items.type, path + "items"))
            }
            is ArrayTypeWithoutSchema ->
                throw IllegalArgumentException("Array type without schema is not supported")
            is BooleanType -> SchemaBuilder.builder().booleanType()
            is DateType -> {
                val schema = SchemaBuilder.builder().intType()
                LogicalTypes.date().addToSchema(schema)
            }
            is IntegerType -> SchemaBuilder.builder().longType()
            is NullType -> SchemaBuilder.builder().nullType()
            is NumberType -> SchemaBuilder.builder().doubleType()
            is ObjectTypeWithEmptySchema ->
                throw IllegalArgumentException("Object type with empty schema is not supported")
            is ObjectTypeWithoutSchema ->
                throw IllegalArgumentException("Object type without schema is not supported")
            is StringType -> SchemaBuilder.builder().stringType()
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
            is UnknownType -> throw IllegalArgumentException("Unknown type: ${airbyteSchema.what}")
        }
    }
}

fun ObjectType.toAvroSchema(stream: DestinationStream.Descriptor): Schema {
    val path = listOf(stream.namespace ?: "default", stream.name)
    return AirbyteTypeToAvroSchema().convert(this, path)
}
