/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.fixtures

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.integrations.destination.clickhouse.schema.toClickHouseCompatibleName
import java.math.RoundingMode
import java.time.LocalTime
import java.time.ZoneOffset

object ClickhouseExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val mappedData =
            ObjectValue(
                expectedRecord.data.values
                    .mapValuesTo(linkedMapOf()) { (_, value) -> mapAirbyteValue(value) }
                    .mapKeysTo(linkedMapOf()) { it.key.toClickHouseCompatibleName() }
            )
        return expectedRecord.copy(data = mappedData)
    }

    private fun mapAirbyteValue(value: AirbyteValue): AirbyteValue {
        return when (value) {
            is TimeWithTimezoneValue -> StringValue(value.value.toString())
            is TimeWithoutTimezoneValue -> StringValue(value.value.toString())
            is TimestampWithoutTimezoneValue ->
                TimestampWithTimezoneValue(value.value.atOffset(ZoneOffset.UTC))
            is TimestampWithTimezoneValue ->
                TimestampWithTimezoneValue(value.value.withOffsetSameInstant(ZoneOffset.UTC))
            is DateValue ->
                TimestampWithTimezoneValue(
                    value.value.atTime(LocalTime.MIDNIGHT).atOffset(ZoneOffset.UTC)
                )
            is ObjectValue ->
                ObjectValue(
                    values = value.values.mapValuesTo(linkedMapOf()) { mapAirbyteValue(it.value) }
                )
            is NumberValue -> NumberValue(value.value.setScale(1, RoundingMode.HALF_UP))
            else -> value
        }
    }
}
