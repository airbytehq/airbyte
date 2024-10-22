/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import io.airbyte.cdk.load.util.serializeToString

class AirbyteValueToCsvRow {
    fun convert(value: ObjectValue): Array<String> {
        return value.values.map { convertInner(it.value) }.toTypedArray()
    }

    private fun convertInner(value: AirbyteValue): String {
        return when (value) {
            is ObjectValue -> value.toJson().serializeToString()
            is ArrayValue -> value.toJson().serializeToString()
            is StringValue -> value.value
            is IntegerValue -> value.value.toString()
            is NumberValue -> value.value.toString()
            else -> value.toString()
        }
    }
}

fun ObjectValue.toCsvRecord(): Array<String> {
    return AirbyteValueToCsvRow().convert(this)
}
