/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.csv

import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.UnknownValue
import io.airbyte.cdk.load.data.json.toJson
import io.airbyte.cdk.load.util.serializeToString

sealed interface CsvFormat {
    data object Standard : CsvFormat
    data object MsSql : CsvFormat
}

fun ObjectValue.toCsvRecord(schema: ObjectType, format: CsvFormat = CsvFormat.Standard): List<Any> {
    return schema.properties.map { (key, _) -> values[key]?.convertToCsvValue(format) ?: "" }
}

private fun Any.convertToCsvValue(format: CsvFormat): Any =
    when (this) {
        is ObjectValue -> toJson().serializeToString()
        is ArrayValue -> toJson().serializeToString()
        is StringValue -> value
        is IntegerValue -> value
        is NumberValue -> value
        is NullValue -> ""
        is TimestampWithTimezoneValue -> value
        is TimestampWithoutTimezoneValue -> value
        is BooleanValue ->
            when (format) {
                CsvFormat.MsSql -> if (value) 1 else 0
                CsvFormat.Standard -> value
            }
        is DateValue -> value
        is TimeWithTimezoneValue -> value
        is TimeWithoutTimezoneValue -> value
        is UnknownValue -> ""
        else -> ""
    }

fun ObjectValue.toMssqlCsvRecord(schema: ObjectType): List<Any> =
    toCsvRecord(schema, CsvFormat.MsSql)
