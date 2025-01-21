/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.avro

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import java.time.ZoneOffset

object AvroExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        return expectedRecord.copy(data = timestampsToInteger(expectedRecord.data) as ObjectValue)
    }

    /**
     * Avro doesn't distinguish between temporal types having/not having timezone. So we map
     * all temporal types to their "with timezone" variant, defaulting to UTC.
     */
    private fun timestampsToInteger(value: AirbyteValue): AirbyteValue =
        when (value) {
            is TimestampWithoutTimezoneValue ->
                TimestampWithTimezoneValue(value.value.atOffset(ZoneOffset.UTC))
            is TimeWithoutTimezoneValue ->
                TimeWithTimezoneValue(value.value.atOffset(ZoneOffset.UTC))
            is ArrayValue -> ArrayValue(value.values.map { timestampsToInteger(it) })
            is ObjectValue ->
                ObjectValue(
                    value.values.mapValuesTo(linkedMapOf()) { (_, v) -> timestampsToInteger(v) }
                )
            else -> value
        }
}
