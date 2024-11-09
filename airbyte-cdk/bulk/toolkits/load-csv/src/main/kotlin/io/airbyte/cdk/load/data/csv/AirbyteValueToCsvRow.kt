/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.csv

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeValue
import io.airbyte.cdk.load.data.TimestampValue
import io.airbyte.cdk.load.data.UnknownValue
import io.airbyte.cdk.load.data.json.toJson
import io.airbyte.cdk.load.util.serializeToString

class AirbyteValueToCsvRow {
    fun convert(value: ObjectValue, schema: ObjectType): Array<String> {
        return schema.properties
            .map { (key, _) -> value.values[key]?.let { convertInner(it) } ?: "" }
            .toTypedArray()
    }

    private fun convertInner(value: AirbyteValue): String {
        return when (value) {
            is ObjectValue -> value.toJson().serializeToString()
            is ArrayValue -> value.toJson().serializeToString()
            is StringValue -> value.value
            is IntegerValue -> value.value.toString()
            is NumberValue -> value.value.toString()
            is NullValue -> ""
            is TimestampValue -> value.value
            is BooleanValue -> value.value.toString()
            is DateValue -> value.value
            is IntValue -> value.value.toString()
            is TimeValue -> value.value
            is UnknownValue -> ""
        }
    }
}

fun ObjectValue.toCsvRecord(schema: ObjectType): Array<String> {
    return AirbyteValueToCsvRow().convert(this, schema)
}
