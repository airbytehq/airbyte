/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import java.io.Serializable
import org.apache.spark.sql.Row
import org.apache.spark.sql.RowFactory

class AirbyteValueToSparkRow : Serializable {
    fun convert(value: AirbyteValue): Row = convertInner(value) as Row

    private fun convertInner(value: AirbyteValue): Any? {
        return when (value) {
            is ObjectValue ->
                RowFactory.create(*(value.values.values.map { convertInner(it) }.toTypedArray()))
            is ArrayValue ->
                RowFactory.create(*(value.values.map { convertInner(it) }.toTypedArray()))
            is BooleanValue -> value.value
            is DateValue -> TODO("Date?")
            is IntegerValue -> value.value
            is NullValue -> null
            is NumberValue -> value.value
            is StringValue -> value.value
            is TimeValue -> TODO("Time?")
            is TimestampValue -> TODO("Timestamp?")
            is UnknownValue -> throw IllegalArgumentException("Unknown value: $value")
        }
    }
}
