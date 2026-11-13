/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.write

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import java.time.ZoneOffset

/**
 * Redshift-specific expected record mapper that handles:
 *
 * 1. TIMESTAMPTZ normalization: Redshift normalizes all TIMESTAMPTZ values to UTC internally.
 * ```
 *    For example, '2023-01-23T11:34:56-01:00' is stored and returned as '2023-01-23T12:34:56Z'.
 * ```
 * 2. Null character replacement: Redshift cannot store null characters (\u0000) in strings.
 * ```
 *    We replace them with spaces during insertion, so expected values need the same treatment.
 * ```
 */
object RedshiftExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        val mappedData = normalizeValues(expectedRecord.data)
        return expectedRecord.copy(data = mappedData as ObjectValue)
    }

    private fun normalizeValues(value: AirbyteValue): AirbyteValue =
        when (value) {
            is TimestampWithTimezoneValue -> {
                // Convert to the same instant but in UTC timezone
                val utcTime = value.value.withOffsetSameInstant(ZoneOffset.UTC)
                TimestampWithTimezoneValue(utcTime)
            }
            is StringValue -> {
                // Redshift cannot store null characters, we replace with space
                StringValue(value.value.replace("\u0000", " "))
            }
            is ArrayValue -> ArrayValue(value.values.map { normalizeValues(it) })
            is ObjectValue ->
                ObjectValue(
                    value.values.mapValuesTo(linkedMapOf()) { (_, v) -> normalizeValues(v) }
                )
            else -> value
        }
}
