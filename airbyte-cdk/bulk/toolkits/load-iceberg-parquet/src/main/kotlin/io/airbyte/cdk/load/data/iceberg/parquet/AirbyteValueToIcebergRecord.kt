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
import io.airbyte.cdk.load.data.TimeValue
import io.airbyte.cdk.load.data.TimestampValue
import io.airbyte.cdk.load.data.UnknownValue
import org.apache.iceberg.Schema
import org.apache.iceberg.data.GenericRecord
import org.apache.iceberg.types.Type

class AirbyteValueToIcebergRecord {
    fun convert(airbyteValue: AirbyteValue, type: Type): Any? {
        when (airbyteValue) {
            is ObjectValue -> {
                val recordSchema =
                    if (type.isStructType) {
                        type.asStructType().asSchema()
                    } else {
                        throw IllegalArgumentException("ObjectValue should be mapped to ObjectType")
                    }
                val associate = recordSchema.columns().associate { it.name() to it.type() }
                val record = GenericRecord.create(recordSchema)
                airbyteValue.values.forEach { (name, value) ->
                    associate[name]?.let { field -> record.setField(name, convert(value, field)) }
                }
                return record
            }
            is ArrayValue -> {
                val elementType =
                    if (type.isListType) {
                        type.asListType().elementType()
                    } else {
                        throw IllegalArgumentException("ArrayValue should be mapped to ArrayType")
                    }

                val array: MutableList<Any?> = mutableListOf()

                airbyteValue.values.forEach { value -> array.add(convert(value, elementType)) }
                return array
            }
            is BooleanValue -> return airbyteValue.value
            is DateValue ->
                throw IllegalArgumentException("String-based date types are not supported")
            is IntegerValue -> return airbyteValue.value.toLong()
            is NullValue -> return null
            is NumberValue -> return airbyteValue.value.toDouble()
            is StringValue -> return airbyteValue.value
            is TimeValue ->
                throw IllegalArgumentException("String-based time types are not supported")
            is TimestampValue ->
                throw IllegalArgumentException("String-based timestamp types are not supported")
            is UnknownValue -> throw IllegalArgumentException("Unknown type is not supported")
        }
    }
}

fun ObjectValue.toIcebergRecord(schema: Schema): GenericRecord {

    val associate = schema.columns().associate { it.name() to it.type() }
    val create = GenericRecord.create(schema)
    val airbyteValueToIcebergRecord = AirbyteValueToIcebergRecord()
    this.values.forEach { (name, value) ->
        associate[name]?.let { field ->
            create.setField(name, airbyteValueToIcebergRecord.convert(value, field))
        }
    }
    return create
}
