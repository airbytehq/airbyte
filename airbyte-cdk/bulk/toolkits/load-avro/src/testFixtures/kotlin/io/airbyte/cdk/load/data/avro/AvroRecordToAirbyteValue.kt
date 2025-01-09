/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.avro

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import org.apache.avro.generic.GenericArray
import org.apache.avro.generic.GenericRecord
import org.apache.avro.util.Utf8

object AvroRecordToAirbyteValue {
    fun convert(avroValue: Any?): AirbyteValue {
        return when (avroValue) {
            null -> NullValue
            is GenericRecord ->
                ObjectValue(
                    avroValue.schema.fields.associateTo(linkedMapOf()) { field ->
                        field.name() to convert(avroValue.get(field.name()))
                    }
                )
            is GenericArray<*> -> ArrayValue(avroValue.map { convert(it) })
            is Boolean -> BooleanValue(avroValue)
            is Int -> IntegerValue(avroValue.toLong())
            is Long -> IntegerValue(avroValue)
            is Double -> NumberValue(avroValue.toBigDecimal())
            is Utf8 -> StringValue(avroValue.toString())
            is String -> StringValue(avroValue)
            else ->
                throw IllegalArgumentException(
                    "Unrecognized avro value type: ${avroValue::class.qualifiedName} with value: $avroValue"
                )
        }
    }
}

fun GenericRecord.toAirbyteValue(): AirbyteValue {
    return AvroRecordToAirbyteValue.convert(this)
}
