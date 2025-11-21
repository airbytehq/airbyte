/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.integrations.destination.snowflake.write.SnowflakeExpectedRecordMapper.mapAirbyteMetadata
import io.airbyte.integrations.destination.snowflake.write.transform.SnowflakeValueCoercer

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
    private fun mapValues(value: AirbyteValue): AirbyteValue {
        val validationResult =
            SnowflakeValueCoercer()
                .validate(
                    EnrichedAirbyteValue(
                        value,
                        value.airbyteType,
                        name = "unused",
                        airbyteMetaField = null,
                    )
                )
        return when (validationResult) {
            is ValidationResult.ShouldNullify -> NullValue
            is ValidationResult.ShouldTruncate -> validationResult.truncatedValue
            ValidationResult.Valid ->
                when (value) {
                    is DateValue -> StringValue(value.value.toString())
                    is TimeWithTimezoneValue -> StringValue(value.value.toString())
                    is TimeWithoutTimezoneValue -> StringValue(value.value.toString())
                    is TimestampWithTimezoneValue -> StringValue(value.value.toString())
                    is TimestampWithoutTimezoneValue -> StringValue(value.value.toString())
                    is NumberValue ->
                        try {
                            // If the value is exactly an integer, turn it into an IntegerValue
                            IntegerValue(value.value.toBigIntegerExact())
                        } catch (_: ArithmeticException) {
                            // If the value wasn't an integer, then toBigIntegerExact will throw.
                            // So just return the original NumberValue.
                            value
                        }
                    is ArrayValue -> ArrayValue(value.values.map { mapValues(it) })
                    is ObjectValue ->
                        ObjectValue(
                            value.values.mapValuesTo(linkedMapOf()) { (_, v) -> mapValues(v) }
                        )
                    else -> value
                }
        }
    }
}
