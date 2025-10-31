/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord

object PostgresExpectedRawRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        // Null values are filtered from raw records, so remove them from the expected records.
        val filtered = filterNullValues(expectedRecord.data) as ObjectValue
        return expectedRecord.copy(data = filtered)
    }

    private fun filterNullValues(value: AirbyteValue): AirbyteValue =
        when (value) {
            is ArrayValue -> ArrayValue(value.values.map { filterNullValues(it) })
            is ObjectValue ->
                ObjectValue(
                    value.values
                        .filter { (_, v) -> v !is NullValue }
                        .mapValuesTo(linkedMapOf()) { (_, v) -> filterNullValues(v) }
                )
            else -> value
        }
}
