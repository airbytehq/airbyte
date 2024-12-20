/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeValue
import io.airbyte.cdk.load.data.TimestampValue
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord

/**
 * JSON doesn't have temporal types, we just write everything as string. So we map expected records'
 * temporal values back to string.
 */
object JsonExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val mappedData = mapTemporalValuesToString(expectedRecord.data)
        return expectedRecord.copy(data = mappedData as ObjectValue)
    }

    private fun mapTemporalValuesToString(value: AirbyteValue): AirbyteValue =
        when (value) {
            is DateValue -> StringValue(value.value)
            is TimeValue -> StringValue(value.value)
            is TimestampValue -> StringValue(value.value)
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
