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
import org.apache.avro.Schema
import org.apache.avro.SchemaBuilder

class AirbyteTypeToAvroSchema {
    fun convert(airbyteSchema: AirbyteType, path: List<String>): Schema {
        when (airbyteSchema) {
            is ObjectType -> {
                val name = path.last()
                val namespace = path.take(path.size - 1).reversed().joinToString(".")
                val builder = SchemaBuilder.record(name).namespace(namespace).fields()
                return airbyteSchema.properties.entries
                    .fold(builder) { acc, (name, field) ->
                        // NOTE: We will not support nullable at this stage.
                        // All nullables should have been converted to union[this, null] upstream
                        // TODO: Enforce this
                        acc.name(name).type(convert(field.type, path + name)).noDefault()
                    }
                    .endRecord()
            }
            is ArrayType -> {
                return SchemaBuilder.array()
                    .items(convert(airbyteSchema.items.type, path + "items"))
            }
            is ArrayTypeWithoutSchema ->
                throw IllegalArgumentException("Array type without schema is not supported")
            is BooleanType -> return SchemaBuilder.builder().booleanType()
            is DateType ->
                throw IllegalArgumentException("String-based date types are not supported")
            is IntegerType -> return SchemaBuilder.builder().longType()
            is NullType -> return SchemaBuilder.builder().nullType()
            is NumberType -> return SchemaBuilder.builder().doubleType()
            is ObjectTypeWithEmptySchema ->
                throw IllegalArgumentException("Object type with empty schema is not supported")
            is ObjectTypeWithoutSchema ->
                throw IllegalArgumentException("Object type without schema is not supported")
            is StringType -> return SchemaBuilder.builder().stringType()
            is TimeTypeWithTimezone,
            is TimeTypeWithoutTimezone ->
                throw IllegalArgumentException("String-based time types are not supported")
            is TimestampTypeWithTimezone,
            is TimestampTypeWithoutTimezone ->
                throw IllegalArgumentException("String-based timestamp types are not supported")
            is UnionType ->
                return Schema.createUnion(airbyteSchema.options.map { convert(it, path) })
            is UnknownType -> throw IllegalArgumentException("Unknown type: ${airbyteSchema.what}")
        }
    }
}

fun ObjectType.toAvroSchema(stream: DestinationStream.Descriptor): Schema {
    val path = listOf(stream.namespace ?: "default", stream.name)
    return AirbyteTypeToAvroSchema().convert(this, path)
}
