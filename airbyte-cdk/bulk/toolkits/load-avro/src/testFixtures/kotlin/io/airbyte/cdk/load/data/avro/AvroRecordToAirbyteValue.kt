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
            is GenericArray<*> ->
                ArrayValue(
                    avroValue.map { convert(it, findType(schema, Schema.Type.ARRAY).elementType) }
                )
            is Boolean -> BooleanValue(avroValue)
            is Int -> handleInt(avroValue.toLong(), schema)
            is Long -> handleInt(avroValue, schema)
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

private fun findType(schema: Schema, vararg types: Schema.Type): Schema =
    if (schema.isUnion) {
        schema.types.firstOrNull { types.contains(it.type) }
            ?: throw IllegalArgumentException(
                "Expected $schema to be a union containing at least one of $types"
            )
    } else if (types.contains(schema.type)) {
        schema
    } else {
        throw IllegalArgumentException("Expected $schema to be one of $types")
    }

private fun handleInt(l: Long, schema: Schema): AirbyteValue {
    val logicalType =
        if (schema.isUnion) {
            findType(schema, Schema.Type.LONG, Schema.Type.INT).logicalType
        } else {
            schema.logicalType
        }

    fun instantOfMicros(): Instant = Instant.ofEpochMilli(l / 1000).plusNanos(l % 1000 * 1000)

    return when (logicalType) {
        LogicalTypes.date() -> DateValue(LocalDate.ofEpochDay(l))
        LogicalTypes.timeMicros() ->
            TimeWithTimezoneValue(OffsetTime.ofInstant(instantOfMicros(), ZoneOffset.UTC))
        LogicalTypes.timestampMillis() ->
            TimestampWithTimezoneValue(Instant.ofEpochMilli(l).atOffset(ZoneOffset.UTC))
        LogicalTypes.timestampMicros() ->
            TimestampWithTimezoneValue(instantOfMicros().atOffset(ZoneOffset.UTC))
        else -> IntegerValue(l)
    }
}

fun GenericRecord.toAirbyteValue(): AirbyteValue {
    return AvroRecordToAirbyteValue.convert(this, this.schema)
}
