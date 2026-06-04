/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.write.load

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
import io.airbyte.cdk.load.data.json.toJson
import io.airbyte.cdk.load.util.serializeToString
import java.nio.ByteBuffer
import java.time.ZoneOffset

/**
 * Converts [AirbyteValue] instances to Avro-compatible values for writing into Avro
 * [org.apache.avro.generic.GenericRecord] fields.
 *
 * Upstream guarantees that values are valid and correctly typed/scaled, so no schema inspection or
 * validation is performed during conversion.
 */
object DatabricksAvroValueConverter {

    /** Converts an [AirbyteValue] to an Avro-compatible value. */
    fun convert(value: AirbyteValue?): Any? {
        if (value == null || value is NullValue) return null

        return when (value) {
            is StringValue -> value.value
            is BooleanValue -> value.value
            is IntegerValue -> value.value.toLong()
            is NumberValue -> ByteBuffer.wrap(value.value.unscaledValue().toByteArray())
            is DateValue -> value.value.toEpochDay().toInt()
            is TimestampWithTimezoneValue -> {
                val odt = value.value
                odt.toEpochSecond() * 1_000_000L + odt.nano.toLong() / 1_000L
            }
            is TimestampWithoutTimezoneValue -> {
                val epochSecond = value.value.toEpochSecond(ZoneOffset.UTC)
                epochSecond * 1_000_000L + value.value.nano.toLong() / 1_000L
            }
            is TimeWithTimezoneValue -> value.value.toString()
            is TimeWithoutTimezoneValue -> value.value.toString()
            is ObjectValue -> value.toJson().serializeToString()
            is ArrayValue -> value.toJson().serializeToString()
            is NullValue -> null
        }
    }
}
