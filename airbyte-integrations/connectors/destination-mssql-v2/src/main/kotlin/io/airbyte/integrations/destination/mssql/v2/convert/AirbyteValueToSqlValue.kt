/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.convert

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
import io.airbyte.cdk.load.util.serializeToJsonBytes
import java.sql.Date
import java.sql.Time
import java.sql.Timestamp

/** CDK pipeline [AirbyteValue] to SQL values converter. */
class AirbyteValueToSqlValue {

    /**
     * Converts an [AirbyteValue] to the associated SQL value.
     *
     * @param airbyteValue The [AirbyteValue] from an Airbyte record
     * @return The corresponding SQL value for the given [AirbyteValue].
     * @throws IllegalArgumentException if the [AirbyteValue] is not supported.
     */
    fun convert(airbyteValue: AirbyteValue): Any? {
        return when (airbyteValue) {
            is ObjectValue -> {
                val convertedValues =
                    airbyteValue.values.entries.associate { (name, value) ->
                        name to convert(value)
                    }
                convertedValues
            }
            is ArrayValue -> airbyteValue.values.map { convert(it) }
            is BooleanValue -> airbyteValue.value
            is DateValue -> Date.valueOf(airbyteValue.value)
            is IntegerValue -> airbyteValue.value
            is NullValue -> null
            is NumberValue -> airbyteValue.value.toDouble().toBigDecimal()
            is StringValue -> airbyteValue.value
            is UnknownValue -> airbyteValue.value.serializeToJsonBytes()
            is TimeWithTimezoneValue -> Time.valueOf(airbyteValue.value.toLocalTime())
            is TimeWithoutTimezoneValue -> Time.valueOf(airbyteValue.value)
            is TimestampWithTimezoneValue -> Timestamp.valueOf(airbyteValue.value.toLocalDateTime())
            is TimestampWithoutTimezoneValue -> Timestamp.valueOf(airbyteValue.value)
        }
    }
}
