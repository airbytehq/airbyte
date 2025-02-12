/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import java.time.ZoneOffset

/**
 * Iceberg doesn't have a TimeWithTimezone type. So map expectedRecords' TimeWithTimezone to
 * TimeWithoutTimezone.
 */
object S3DataLakeExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val mappedData = mapTemporalTypesToUtc(expectedRecord.data)
        return expectedRecord.copy(data = mappedData as ObjectValue)
    }

    /**
     * We write parquet, which stores all X_with_timezone types in UTC. So we need to map the
     * expected values into UTC.
     */
    private fun mapTemporalTypesToUtc(value: AirbyteValue): AirbyteValue =
        when (value) {
            is TimeWithTimezoneValue ->
                TimeWithoutTimezoneValue(
                    value.value.withOffsetSameInstant(ZoneOffset.UTC).toLocalTime()
                )
            is TimestampWithTimezoneValue ->
                TimestampWithTimezoneValue(value.value.withOffsetSameInstant(ZoneOffset.UTC))
            is ArrayValue -> ArrayValue(value.values.map { mapTemporalTypesToUtc(it) })
            is ObjectValue ->
                ObjectValue(
                    value.values.mapValuesTo(linkedMapOf()) { (_, v) -> mapTemporalTypesToUtc(v) }
                )
            else -> value
        }
}
