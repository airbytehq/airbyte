/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.fixtures

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.integrations.destination.mysql.config.toMySQLCompatibleName
import java.math.RoundingMode
import java.time.ZoneOffset

object MySQLExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val mappedData =
            ObjectValue(
                expectedRecord.data.values
                    .mapValuesTo(linkedMapOf()) { (_, value) -> mapAirbyteValue(value) }
                    .mapKeysTo(linkedMapOf()) { it.key.toMySQLCompatibleName() }
            )
        return expectedRecord.copy(data = mappedData)
    }

    private fun mapAirbyteValue(value: AirbyteValue): AirbyteValue {
        return when (value) {
            is TimestampWithoutTimezoneValue ->
                TimestampWithTimezoneValue(value.value.atOffset(ZoneOffset.UTC))
            is TimestampWithTimezoneValue ->
                TimestampWithTimezoneValue(value.value.withOffsetSameInstant(ZoneOffset.UTC))
            // MySQL TIME type doesn't support timezone - convert to without timezone
            is TimeWithTimezoneValue ->
                TimeWithoutTimezoneValue(value.value.toLocalTime())
            is ObjectValue ->
                ObjectValue(
                    values = value.values.mapValuesTo(linkedMapOf()) { mapAirbyteValue(it.value) }
                )
            is NumberValue -> NumberValue(value.value.setScale(9, RoundingMode.HALF_UP))
            else -> value
        }
    }
}
