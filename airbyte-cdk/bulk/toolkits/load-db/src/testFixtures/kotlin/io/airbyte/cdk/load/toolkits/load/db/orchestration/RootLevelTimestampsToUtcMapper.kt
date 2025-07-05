/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.load.db.orchestration

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import java.time.ZoneOffset

/** Many warehouse destinations store timestamps in UTC. This mapper implements that conversion. */
object RootLevelTimestampsToUtcMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val mappedData =
            ObjectValue(
                expectedRecord.data.values.mapValuesTo(linkedMapOf()) { (_, value) ->
                    when (value) {
                        is TimeWithTimezoneValue ->
                            TimeWithTimezoneValue(value.value.withOffsetSameInstant(ZoneOffset.UTC))
                        is TimestampWithTimezoneValue ->
                            TimestampWithTimezoneValue(
                                value.value.withOffsetSameInstant(ZoneOffset.UTC)
                            )
                        else -> value
                    }
                }
            )
        return expectedRecord.copy(data = mappedData)
    }
}
