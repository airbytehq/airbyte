/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.fixtures

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import java.time.LocalTime
import java.time.ZoneOffset

object ClickhouseExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val mappedData =
            ObjectValue(
                expectedRecord.data.values.mapValuesTo(linkedMapOf()) { (_, value) ->
                    when (value) {
                        is TimeWithTimezoneValue -> StringValue(value.value.toString())
                        is TimeWithoutTimezoneValue -> StringValue(value.value.toString())
                        is TimestampWithoutTimezoneValue ->
                            TimestampWithTimezoneValue(value.value.atOffset(ZoneOffset.UTC))
                        is TimestampWithTimezoneValue ->
                            TimestampWithTimezoneValue(
                                value.value.withOffsetSameInstant(ZoneOffset.UTC)
                            )
                        is DateValue ->
                            TimestampWithTimezoneValue(
                                value.value.atTime(LocalTime.MIDNIGHT).atOffset(ZoneOffset.UTC)
                            )
                        else -> value
                    }
                }
            )
        return expectedRecord.copy(data = mappedData)
    }
}
