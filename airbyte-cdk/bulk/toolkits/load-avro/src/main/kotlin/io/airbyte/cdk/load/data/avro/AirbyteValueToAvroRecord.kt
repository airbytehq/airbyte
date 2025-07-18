/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.avro

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.Transformations
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import org.apache.avro.Schema
import org.apache.avro.generic.GenericData
import org.apache.avro.generic.GenericRecord

class AirbyteValueToAvroRecord {
    fun convert(airbyteValue: AirbyteValue, airbyteSchema: AirbyteType, schema: Schema): Any? {
        try {
            if (airbyteValue == NullValue) {
                return null
            }

            if (
                schema.isUnion &&
                    schema.types.size == 2 &&
                    schema.types.any { it.type == Schema.Type.NULL }
            ) {
                val nonNullSchema = schema.types.find { it.type != Schema.Type.NULL }!!
                return convert(airbyteValue, airbyteSchema, nonNullSchema)
            }

            when (airbyteSchema) {
                is ObjectType -> {
                    val record = GenericData.Record(schema)
                    airbyteSchema.properties.forEach { (name, airbyteField) ->
                        val nameMangled = Transformations.toAvroSafeName(name)
                        schema.getField(nameMangled)?.let { avroField ->
                            val value = (airbyteValue as ObjectValue).values[name]
                            record.put(
                                nameMangled,
                                convert(value ?: NullValue, airbyteField.type, avroField.schema())
                            )
                        }
                    }
                    return record
                }
                is ArrayType -> {
                    val array =
                        GenericData.Array<Any>((airbyteValue as ArrayValue).values.size, schema)
                    airbyteValue.values.forEach { value ->
                        array.add(convert(value, airbyteSchema.items.type, schema.elementType))
                    }
                    return array
                }
                BooleanType -> return (airbyteValue as BooleanValue).value
                DateType -> return (airbyteValue as IntegerValue).value.toInt()
                IntegerType -> return (airbyteValue as IntegerValue).value.toLong()
                NumberType -> return (airbyteValue as NumberValue).value.toDouble()
                StringType -> return (airbyteValue as StringValue).value

                // Upstream all unknown types other than {"type": "null"} are converted to
                // Schemaless
                is UnknownType -> return null

                // Converted to strings upstream
                ObjectTypeWithEmptySchema,
                ObjectTypeWithoutSchema,
                ArrayTypeWithoutSchema -> return (airbyteValue as StringValue).value

                // Converted to integrals upstream
                TimeTypeWithTimezone,
                TimeTypeWithoutTimezone,
                TimestampTypeWithTimezone,
                TimestampTypeWithoutTimezone -> return (airbyteValue as IntegerValue).value.toLong()
                is UnionType -> {
                    for (optionType in airbyteSchema.options) {
                        try {
                            val optionSchema = matchingAvroType(optionType, schema)
                            return convert(airbyteValue, optionType, optionSchema)
                        } catch (e: Exception) {
                            continue
                        }
                    }
                    throw IllegalArgumentException(
                        "No matching Avro type found for $airbyteSchema in $schema (airbyte value: ${airbyteValue.javaClass.simpleName})"
                    )
                }
            }
        } catch (e: Exception) {
            throw RuntimeException(
                "Failed to convert $airbyteSchema(${airbyteValue.javaClass.simpleName}) to $schema",
                e
            )
        }
    }

    private fun matchingAvroType(airbyteSchema: AirbyteType, avroUnionSchema: Schema): Schema {
        return when (airbyteSchema) {
            is ObjectType -> avroUnionSchema.types.find { it.type == Schema.Type.RECORD }
            is ArrayType -> avroUnionSchema.types.find { it.type == Schema.Type.ARRAY }
            BooleanType -> avroUnionSchema.types.find { it.type == Schema.Type.BOOLEAN }
            DateType -> avroUnionSchema.types.find { it.type == Schema.Type.INT }
            IntegerType -> avroUnionSchema.types.find { it.type == Schema.Type.LONG }
            NumberType -> avroUnionSchema.types.find { it.type == Schema.Type.DOUBLE }
            is UnknownType,
            ArrayTypeWithoutSchema,
            ObjectTypeWithEmptySchema,
            ObjectTypeWithoutSchema,
            StringType -> avroUnionSchema.types.find { it.type == Schema.Type.STRING }
            TimeTypeWithTimezone,
            TimeTypeWithoutTimezone,
            TimestampTypeWithTimezone,
            TimestampTypeWithoutTimezone ->
                avroUnionSchema.types.find { it.type == Schema.Type.LONG }
            is UnionType -> throw IllegalArgumentException("Nested unions are not supported")
        }
            ?: throw IllegalArgumentException(
                "No matching Avro type found for $airbyteSchema in $avroUnionSchema"
            )
    }
}

fun ObjectValue.toAvroRecord(airbyteSchema: ObjectType, avroSchema: Schema): GenericRecord {
    return AirbyteValueToAvroRecord().convert(this, airbyteSchema, avroSchema) as GenericRecord
}
