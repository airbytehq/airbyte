/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.load.data.iceberg.parquet

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
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.UnknownValue
import java.time.ZoneOffset
import org.apache.iceberg.Schema
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.types.Type
import org.apache.iceberg.types.Types.TimestampType

class AirbyteValueToIcebergRecord {
    fun convert(airbyteValue: AirbyteValue, type: Type): Any? {
        when (airbyteValue) {
            is ObjectValue -> {
                val recordSchema =
                    if (type.isStructType) {
                        type.asStructType().asSchema()
                    } else {
                        throw IllegalArgumentException("ObjectValue should be mapped to StructType")
                    }

                val record = GenericRecord.create(recordSchema)
                recordSchema
                    .columns()
                    .filter { column -> airbyteValue.values.containsKey(column.name()) }
                    .associate { column ->
                        column.name() to
                            convert(
                                airbyteValue.values.getOrDefault(column.name(), NullValue),
                                column.type(),
                            )
                    }
                    .forEach { (name, value) -> record.setField(name, value) }
                return record
            }
            is ArrayValue -> {
                val elementType =
                    if (type.isListType) {
                        type.asListType().elementType()
                    } else {
                        throw IllegalArgumentException("ArrayValue should be mapped to ListType")
                    }

                val array: MutableList<Any?> = mutableListOf()

                airbyteValue.values.forEach { value -> array.add(convert(value, elementType)) }
                return array
            }
            is BooleanValue -> return airbyteValue.value
            is DateValue -> return airbyteValue.value
            is IntegerValue -> return airbyteValue.value.toLong()
            is NullValue -> return null
            is NumberValue -> return airbyteValue.value.toDouble()
            is StringValue -> return airbyteValue.value
            is TimeWithTimezoneValue ->
                return when (type.typeId()) {
                    Type.TypeID.TIME -> airbyteValue.value.toLocalTime()
                    else ->
                        throw IllegalArgumentException(
                            "${type.typeId()} type is not allowed for TimeValue"
                        )
                }
            is TimeWithoutTimezoneValue ->
                return when (type.typeId()) {
                    Type.TypeID.TIME -> airbyteValue.value
                    else ->
                        throw IllegalArgumentException(
                            "${type.typeId()} type is not allowed for TimeValue"
                        )
                }
            is TimestampWithTimezoneValue ->
                return when (type.typeId()) {
                    Type.TypeID.TIMESTAMP -> {
                        val timestampType = type as TimestampType
                        val offsetDateTime = airbyteValue.value

                        if (timestampType.shouldAdjustToUTC()) {
                            offsetDateTime
                        } else {
                            offsetDateTime.toLocalDateTime()
                        }
                    }
                    else ->
                        throw IllegalArgumentException(
                            "${type.typeId()} type is not allowed for TimestampValue"
                        )
                }
            is TimestampWithoutTimezoneValue ->
                return when (type.typeId()) {
                    Type.TypeID.TIMESTAMP -> {
                        val timestampType = type as TimestampType
                        val localDateTime = airbyteValue.value

                        if (timestampType.shouldAdjustToUTC()) {
                            localDateTime.atOffset(ZoneOffset.UTC)
                        } else {
                            localDateTime
                        }
                    }
                    else ->
                        throw IllegalArgumentException(
                            "${type.typeId()} type is not allowed for TimestampValue"
                        )
                }
            is UnknownValue -> throw IllegalArgumentException("Unknown type is not supported")
        }
    }
}

fun ObjectValue.toIcebergRecord(schema: Schema): GenericRecord {
    val record = GenericRecord.create(schema)
    val airbyteValueToIcebergRecord = AirbyteValueToIcebergRecord()
    schema.asStruct().fields().forEach { field ->
        val value = this.values[field.name()]
        if (value != null) {
            record.setField(field.name(), airbyteValueToIcebergRecord.convert(value, field.type()))
        }
    }
    return record
}
