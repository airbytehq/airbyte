/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueIdentityMapper
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.TimeValue
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.OffsetTime

private val logger = KotlinLogging.logger {}

/**
 * Iceberg doesn't have a TimeWithTimezone type. So map expectedRecords' TimeWithTimezone to
 * TimeWithoutTimezone.
 */
object IcebergExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val (mappedData, _) = TimeMapper.map(expectedRecord.data, schema)
        return expectedRecord.copy(data = mappedData as ObjectValue)
    }
}

private object TimeMapper : AirbyteValueIdentityMapper() {
    override fun mapTimeWithTimezone(
        value: AirbyteValue,
        context: Context
    ): Pair<AirbyteValue, Context> {
        try {
            if (value is TimeValue) {
                return TimeValue(OffsetTime.parse(value.value).toLocalTime().toString()) to context
            } else {
                logger.warn { "Expected a TimeValue, got: $value, $context" }
            }
        } catch (e: Exception) {
            // swallow exceptions
            logger.warn(e) { "Failed to parse TimeValue: $value, $context" }
        }
        return value to context
    }
}
