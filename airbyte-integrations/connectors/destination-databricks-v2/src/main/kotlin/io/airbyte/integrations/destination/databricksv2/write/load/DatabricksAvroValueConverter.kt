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
import java.math.RoundingMode
import java.nio.ByteBuffer
import java.time.ZoneOffset

/**
 * Converts [AirbyteValue] instances to Avro-compatible values for writing into Avro
 * [org.apache.avro.generic.GenericRecord] fields.
 */
object DatabricksAvroValueConverter {

    /** Scale used for DECIMAL(38, 10) columns -- must match [DatabricksAvroSchemaBuilder]. */
    private const val DECIMAL_SCALE = 10

    /** Converts an [AirbyteValue] to an Avro-compatible value. */
    fun convert(value: AirbyteValue?): Any? {
        if (value == null || value is NullValue) return null

        return when (value) {
            is StringValue -> value.value
            is BooleanValue -> value.value
            is IntegerValue -> value.value.toLong()
            is NumberValue -> {
                // Rescale to match the Avro DECIMAL(38, 10) schema so the reader interprets the
                // bytes correctly.
                val scaled = value.value.setScale(DECIMAL_SCALE, RoundingMode.HALF_UP)
                ByteBuffer.wrap(scaled.unscaledValue().toByteArray())
            }
            is DateValue -> value.value.toEpochDay().toInt()
            is TimestampWithTimezoneValue ->
                toMicros(value.value.toEpochSecond(), value.value.nano.toLong())
            is TimestampWithoutTimezoneValue ->
                toMicros(value.value.toEpochSecond(ZoneOffset.UTC), value.value.nano.toLong())
            is TimeWithTimezoneValue -> value.value.toString()
            is TimeWithoutTimezoneValue -> value.value.toString()
            is ObjectValue -> value.toJson().serializeToString()
            is ArrayValue -> value.toJson().serializeToString()
            is NullValue -> null
        }
    }

    /** Converts epoch seconds + nanos to microseconds (Avro timestamp precision). */
    private fun toMicros(epochSecond: Long, nanos: Long): Long =
        epochSecond * 1_000_000L + nanos / 1_000L
}
