/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.csv

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

fun ObjectValue.toCsvRecord(schema: ObjectType): List<Any> {
    return schema.properties.map { (key, _) ->
        values[key]?.let {
            when (it) {
                is ObjectValue -> it.toJson().serializeToString()
                is ArrayValue -> it.toJson().serializeToString()
                is StringValue -> it.value
                is IntegerValue -> it.value
                is NumberValue -> it.value
                is NullValue -> ""
                is TimestampValue -> it.value
                is BooleanValue -> it.value
                is DateValue -> it.value
                is IntValue -> it.value
                is TimeValue -> it.value
                is UnknownValue -> ""
            }
        }
            ?: ""
    }
}
