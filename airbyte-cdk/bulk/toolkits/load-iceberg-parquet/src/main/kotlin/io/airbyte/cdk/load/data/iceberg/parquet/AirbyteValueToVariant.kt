/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
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
import java.math.BigDecimal
import java.math.BigInteger
import java.time.Instant
import java.time.LocalTime
import java.time.ZoneOffset
import java.time.temporal.ChronoUnit
import org.apache.iceberg.variants.Variant
import org.apache.iceberg.variants.VariantMetadata
import org.apache.iceberg.variants.VariantValue
import org.apache.iceberg.variants.Variants

/**
 * Converts an [AirbyteValue] tree into an Iceberg [Variant].
 *
 * Iceberg ships no JSON parser for variants, and we don't need one: the values are already typed,
 * so numbers, timestamps and booleans keep their types instead of collapsing into JSON text.
 */
class AirbyteValueToVariant {

    fun convert(airbyteValue: AirbyteValue): Variant {
        val metadata = Variants.metadata(collectFieldNames(airbyteValue))
        return Variant.of(metadata, toVariantValue(airbyteValue, metadata))
    }

    /**
     * The metadata dictionary must hold every object key in the value before any of them can be
     * written, so the tree is walked once up front.
     */
    private fun collectFieldNames(airbyteValue: AirbyteValue): Set<String> {
        val names = linkedSetOf<String>()
        fun recurse(value: AirbyteValue) {
            when (value) {
                is ObjectValue ->
                    value.values.forEach { (name, child) ->
                        names.add(name)
                        recurse(child)
                    }
                is ArrayValue -> value.values.forEach { recurse(it) }
                else -> {}
            }
        }
        recurse(airbyteValue)
        return names
    }

    private fun toVariantValue(
        airbyteValue: AirbyteValue,
        metadata: VariantMetadata
    ): VariantValue =
        when (airbyteValue) {
            is ObjectValue -> {
                val obj = Variants.`object`(metadata)
                airbyteValue.values.forEach { (name, value) ->
                    obj.put(name, toVariantValue(value, metadata))
                }
                obj
            }
            is ArrayValue -> {
                val array = Variants.array()
                airbyteValue.values.forEach { array.add(toVariantValue(it, metadata)) }
                array
            }
            is BooleanValue -> Variants.of(airbyteValue.value)
            is DateValue -> Variants.ofDate(airbyteValue.value.toEpochDay().toInt())
            is IntegerValue -> convertInteger(airbyteValue.value)
            is NullValue -> Variants.ofNull()
            is NumberValue -> convertNumber(airbyteValue.value)
            is StringValue -> Variants.of(airbyteValue.value)
            // Variant has no time-with-timezone type, so normalize to UTC and drop the offset,
            // matching how these values are written to a plain Iceberg time column.
            is TimeWithTimezoneValue ->
                Variants.ofTime(
                    micros(
                        airbyteValue.value.withOffsetSameInstant(ZoneOffset.UTC).toLocalTime(),
                    ),
                )
            is TimeWithoutTimezoneValue -> Variants.ofTime(micros(airbyteValue.value))
            is TimestampWithTimezoneValue ->
                Variants.ofTimestamptz(micros(airbyteValue.value.toInstant()))
            is TimestampWithoutTimezoneValue ->
                Variants.ofTimestampntz(micros(airbyteValue.value.toInstant(ZoneOffset.UTC)))
        }

    /** Integers too wide for int64 fall back to decimal, and beyond that to double. */
    private fun convertInteger(value: BigInteger): VariantValue =
        if (value.bitLength() < Long.SIZE_BITS) {
            Variants.of(value.toLong())
        } else {
            convertNumber(value.toBigDecimal())
        }

    /** Variant decimals are capped at precision 38; wider values are stored as doubles. */
    private fun convertNumber(value: BigDecimal): VariantValue =
        if (value.precision() <= MAX_DECIMAL_PRECISION && value.scale() >= 0) {
            Variants.of(value)
        } else {
            Variants.of(value.toDouble())
        }

    private fun micros(time: LocalTime): Long = time.toNanoOfDay() / 1_000

    private fun micros(instant: Instant): Long = ChronoUnit.MICROS.between(Instant.EPOCH, instant)

    companion object {
        private const val MAX_DECIMAL_PRECISION = 38
    }
}
