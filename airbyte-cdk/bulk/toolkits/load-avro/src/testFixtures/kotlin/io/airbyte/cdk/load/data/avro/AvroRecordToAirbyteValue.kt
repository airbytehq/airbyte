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
import io.airbyte.cdk.load.data.DateValue
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
import io.airbyte.cdk.load.data.TimeValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import java.time.Instant
import org.apache.avro.generic.GenericArray
import org.apache.avro.generic.GenericRecord
import org.apache.avro.util.Utf8

class AvroRecordToAirbyteValue {
    fun convert(avroValue: Any?, schema: AirbyteType, top: Boolean = false): AirbyteValue {
        if (avroValue == null) {
            return NullValue
        }
        when (schema) {
            is ObjectType -> {
                val properties = LinkedHashMap<String, AirbyteValue>()
                schema.properties.forEach { (name, field) ->
                    val value = (avroValue as GenericRecord).get(name)
                    if ((value != null) || top) {
                        properties[name] = convert(value, field.type)
                    }
                }
                return ObjectValue(properties)
            }
            is ArrayType -> {
                val items = schema.items
                val values = (avroValue as GenericArray<*>).map { convert(it, items.type) }
                return ArrayValue(values)
            }
            is ArrayTypeWithoutSchema ->
                throw UnsupportedOperationException("ArrayTypeWithoutSchema is not supported")
            is BooleanType -> return BooleanValue(avroValue as Boolean)
            is DateType ->
                return DateValue(
                    Instant.ofEpochMilli((avroValue as Int).toLong() * 86400000).toString()
                )
            is IntegerType -> return IntegerValue(avroValue as Long)
            is NumberType -> return NumberValue((avroValue as Double).toBigDecimal())
            is ObjectTypeWithEmptySchema ->
                throw UnsupportedOperationException("ObjectTypeWithEmptySchema is not supported")
            is ObjectTypeWithoutSchema ->
                throw UnsupportedOperationException("ObjectTypeWithoutSchema is not supported")
            is StringType ->
                return StringValue(
                    when (avroValue) {
                        is Utf8 -> avroValue.toString() // Avro
                        is String -> avroValue // Avro via Parquet
                        else ->
                            throw IllegalArgumentException("Unsupported string type: $avroValue")
                    }
                )
            is TimeTypeWithoutTimezone,
            is TimeTypeWithTimezone ->
                return TimeValue(
                    Instant.ofEpochMilli((avroValue as Long) / 1000).toString().substring(11)
                )
            is TimestampTypeWithoutTimezone,
            is TimestampTypeWithTimezone ->
                return TimestampValue(Instant.ofEpochMilli(avroValue as Long).toString())
            is UnionType -> return tryConvertUnion(avroValue, schema)
            is UnknownType -> throw UnsupportedOperationException("UnknownType is not supported")
            else -> throw IllegalArgumentException("Unsupported schema type: $schema")
        }
    }

    private fun tryConvertUnion(avroValue: Any?, schema: UnionType): AirbyteValue {
        for (type in schema.options) {
            try {
                return convert(avroValue, type)
            } catch (e: Exception) {
                continue
            }
        }
        throw IllegalArgumentException("Could not convert value to any of the union types")
    }
}

fun GenericRecord.toAirbyteValue(schema: AirbyteType): AirbyteValue {
    return AvroRecordToAirbyteValue().convert(this, schema, true)
}
