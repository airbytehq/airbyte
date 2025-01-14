/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.avro

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import java.time.Instant
import java.time.LocalDate
import java.time.OffsetTime
import java.time.ZoneOffset
import org.apache.avro.LogicalType
import org.apache.avro.LogicalTypes
import org.apache.avro.Schema
import org.apache.avro.generic.GenericArray
import org.apache.avro.generic.GenericRecord
import org.apache.avro.util.Utf8

object AvroRecordToAirbyteValue {
    fun convert(avroValue: Any?, schema: Schema): AirbyteValue {
        return when (avroValue) {
            null -> NullValue
            is GenericRecord ->
                ObjectValue(
                    avroValue.schema.fields.associateTo(linkedMapOf()) { field ->
                        field.name() to convert(avroValue.get(field.name()), field.schema())
                    }
                )
            is GenericArray<*> -> ArrayValue(avroValue.map { convert(it, schema.elementType) })
            is Boolean -> BooleanValue(avroValue)
            is Int -> handleInt(avroValue.toLong(), schema.logicalType)
            is Long -> handleInt(avroValue, schema.logicalType)
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

private fun handleInt(l: Long, logicalType: LogicalType?): AirbyteValue =
    when (logicalType) {
        LogicalTypes.date() -> DateValue(LocalDate.ofEpochDay(l))
        LogicalTypes.timeMicros() ->
            TimeWithTimezoneValue(OffsetTime.ofInstant(Instant.ofEpochMilli(l), ZoneOffset.UTC))
        LogicalTypes.timestampMicros() ->
            TimestampWithTimezoneValue(Instant.ofEpochMilli(l).atOffset(ZoneOffset.UTC))
        else -> IntegerValue(l)
    }

fun GenericRecord.toAirbyteValue(): AirbyteValue {
    return AvroRecordToAirbyteValue.convert(this, this.schema)
}
