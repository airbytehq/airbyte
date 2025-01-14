/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import java.time.format.DateTimeFormatter

fun interface ExpectedRecordMapper {
    fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord
}

object NoopExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord =
        expectedRecord
}

/**
 * Some destinations (e.g. JSONL files) don't have temporal types, we just write everything as
 * string. So we map expected records' temporal values back to string.
 */
object UncoercedExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val mappedData = mapTemporalValuesToString(expectedRecord.data)
        return expectedRecord.copy(data = mappedData as ObjectValue)
    }

    private fun mapTemporalValuesToString(value: AirbyteValue): AirbyteValue =
        when (value) {
            is DateValue -> StringValue(value.value.toString())
            // Use specific formatters that match our integration test input.
            is TimeWithTimezoneValue ->
                StringValue(value.value.format(DateTimeFormatter.ISO_OFFSET_TIME))
            is TimeWithoutTimezoneValue ->
                StringValue(value.value.format(DateTimeFormatter.ISO_LOCAL_TIME))
            is TimestampWithTimezoneValue ->
                StringValue(value.value.format(DateTimeFormatter.ISO_OFFSET_DATE_TIME))
            is TimestampWithoutTimezoneValue ->
                StringValue(value.value.format(DateTimeFormatter.ISO_LOCAL_DATE_TIME))
            is ArrayValue -> ArrayValue(value.values.map { mapTemporalValuesToString(it) })
            is ObjectValue ->
                ObjectValue(
                    value.values.mapValuesTo(linkedMapOf()) { (_, v) ->
                        mapTemporalValuesToString(v)
                    }
                )
            else -> value
        }
}
