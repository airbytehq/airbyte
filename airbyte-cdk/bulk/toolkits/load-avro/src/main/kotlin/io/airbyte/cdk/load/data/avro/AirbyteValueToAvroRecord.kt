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
import io.airbyte.cdk.load.data.IntValue
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
    //    fun convert(airbyteValue: AirbyteValue, schema: Schema): Any? {
    //        when (airbyteValue) {
    //            is ObjectValue -> {
    //                val recordSchema =
    //                    if (schema.type == Schema.Type.UNION) {
    //                        schema.types.find { it.type == Schema.Type.RECORD }
    //                            ?: throw IllegalArgumentException("Union must contain a record
    // type")
    //                    } else {
    //                        schema
    //                    }
    //                val record = GenericData.Record(recordSchema)
    //                airbyteValue.values.forEach { (name, value) ->
    //                    val nameMangled = Transformations.toAvroSafeName(name)
    //                    recordSchema.getField(nameMangled)?.let { field ->
    //                        record.put(nameMangled, convert(value, field.schema()))
    //                    }
    //                }
    //                return record
    //            }
    //            is ArrayValue -> {
    //                val arraySchema =
    //                    if (schema.type == Schema.Type.UNION) {
    //                        schema.types.find { it.type == Schema.Type.ARRAY }
    //                            ?: throw IllegalArgumentException("Union must contain an array
    // type")
    //                    } else {
    //                        schema
    //                    }
    //                val array = GenericData.Array<Any>(airbyteValue.values.size, arraySchema)
    //                airbyteValue.values.forEach { value ->
    //                    array.add(convert(value, arraySchema.elementType))
    //                }
    //                return array
    //            }
    //            is BooleanValue -> return airbyteValue.value
    //            is DateValue ->
    //                throw IllegalArgumentException("String-based date types are not supported")
    //            is IntegerValue -> return airbyteValue.value.toLong()
    //            is IntValue -> return airbyteValue.value
    //            is NullValue -> return null
    //            is NumberValue -> return airbyteValue.value.toDouble()
    //            is StringValue -> return airbyteValue.value
    //            is TimeValue ->
    //                throw IllegalArgumentException("String-based time types are not supported")
    //            is TimestampValue ->
    //                throw IllegalArgumentException("String-based timestamp types are not
    // supported")
    //            is UnknownValue -> throw IllegalArgumentException("Unknown type is not supported")
    //        }
    //    }

    fun convert(airbyteValue: AirbyteValue, airbyteSchema: AirbyteType, schema: Schema): Any? {
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
                val array = GenericData.Array<Any>((airbyteValue as ArrayValue).values.size, schema)
                airbyteValue.values.forEach { value ->
                    array.add(convert(value, airbyteSchema.items.type, schema.elementType))
                }
                return array
            }
            BooleanType -> return (airbyteValue as BooleanValue).value
            DateType -> return (airbyteValue as IntValue).value // TODO: Remove IntType!
            IntegerType -> return (airbyteValue as IntegerValue).value.toLong()
            NumberType -> return (airbyteValue as NumberValue).value.toDouble()
            StringType -> return (airbyteValue as StringValue).value

            // Converted to strings upstream
            is UnknownType,
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
