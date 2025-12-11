/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
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
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.integrations.destination.snowflake.write.SnowflakeExpectedRecordMapper.mapAirbyteMetadata
import io.airbyte.integrations.destination.snowflake.write.transform.INT_MAX
import io.airbyte.integrations.destination.snowflake.write.transform.INT_MIN
import java.math.BigDecimal

val INT_MIN_NUMBER = INT_MIN.toBigDecimal()
val INT_MAX_NUMBER = INT_MAX.toBigDecimal()

object SnowflakeExpectedRawRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        // Map values to align with Snowflake values
        val mappedData = mapValues(expectedRecord.data) as ObjectValue
        // Map the metadata to account for invalid values
        val mappedMetadata =
            mapAirbyteMetadata(
                originalData = expectedRecord.data,
                mappedData =
                    mappedData.values.entries.associateTo(linkedMapOf()) {
                        it.key.uppercase() to it.value
                    },
                airbyteMetadata = expectedRecord.airbyteMeta
            )
        // Null values are filtered from raw records, so remove them from the expected records.
        val filtered =
            ObjectValue(LinkedHashMap(mappedData.values.filter { (_, v) -> v !is NullValue }))
        return expectedRecord.copy(data = filtered, airbyteMeta = mappedMetadata)
    }

    /**
     * The date/time/timestamp handling is copied from
     * [io.airbyte.cdk.load.test.util.UncoercedExpectedRecordMapper], as you cannot inherit from
     * objects in Kotlin. This "override" changes the time-based values to match the formatting done
     * in the destination to work with Snowflake's types.
     *
     * Additionally, Snowflake VARIANT automatically converts integral numbers to integers. For
     * example, 1.0 is stored as 1. We perform the same conversion here.
     */
    private fun mapValues(value: AirbyteValue): AirbyteValue =
        when (value) {
            is DateValue -> StringValue(value.value.toString())
            is TimeWithTimezoneValue -> StringValue(value.value.toString())
            is TimeWithoutTimezoneValue -> StringValue(value.value.toString())
            is TimestampWithTimezoneValue -> StringValue(value.value.toString())
            is TimestampWithoutTimezoneValue -> StringValue(value.value.toString())
            is NumberValue ->
                // TODO This is a hack -
                // https://github.com/airbytehq/airbyte-internal-issues/issues/15359
                // If we're within the weird clamping range, then clamp to 9.999e38
                if (
                    BigDecimal("-1.00000000000000001526e39") < value.value &&
                        value.value < INT_MIN_NUMBER
                ) {
                    NumberValue(BigDecimal("-9.999999999999999e38"))
                } else if (
                    INT_MAX_NUMBER < value.value &&
                        value.value < BigDecimal("1.00000000000000001526e39")
                ) {
                    NumberValue(BigDecimal("9.999999999999999e38"))
                } else if (INT_MIN_NUMBER < value.value && value.value < INT_MAX_NUMBER) {
                    // If we're within snowflake's NUMBER(38, 0) range, then translate to int
                    try {
                        // If the value is exactly an integer, turn it into an IntegerValue
                        IntegerValue(value.value.toBigIntegerExact())
                    } catch (_: ArithmeticException) {
                        // If the value wasn't an integer, then toBigIntegerExact will throw.
                        // So just return the original NumberValue.
                        value
                    }
                } else {
                    // otherwise, leave the value unchanged
                    value
                }
            is ArrayValue -> ArrayValue(value.values.map { mapValues(it) })
            is ObjectValue ->
                ObjectValue(value.values.mapValuesTo(linkedMapOf()) { (_, v) -> mapValues(v) })
            else -> value
        }
}
