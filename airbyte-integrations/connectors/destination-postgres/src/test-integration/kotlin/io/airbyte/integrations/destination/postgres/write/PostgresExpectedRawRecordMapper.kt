/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord

/**
 * Mapper for raw table records in PostgreSQL. Raw tables store data in JSONB format, which:
 * - Filters out null values
 * - Strips null characters from strings (PostgreSQL doesn't support \u0000 in text)
 *
 * Note: Unlike typed tables, raw tables do NOT normalize timestamps to UTC because JSONB stores
 * timestamps as strings with their original timezone offset.
 */
object PostgresExpectedRawRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        // Null values are filtered from raw records, so remove them from the expected records.
        // Null characters are also removed from string values.
        val filtered = filterNullValues(expectedRecord.data) as ObjectValue
        val sanitized = removeNullCharacters(filtered) as ObjectValue
        return expectedRecord.copy(data = sanitized)
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

    private fun removeNullCharacters(value: AirbyteValue): AirbyteValue =
        when (value) {
            is StringValue -> StringValue(value.value.replace("\u0000", ""))
            is ArrayValue -> ArrayValue(value.values.map { removeNullCharacters(it) })
            is ObjectValue ->
                ObjectValue(
                    value.values.mapValuesTo(linkedMapOf()) { (_, v) -> removeNullCharacters(v) }
                )
            else -> value
        }
}
