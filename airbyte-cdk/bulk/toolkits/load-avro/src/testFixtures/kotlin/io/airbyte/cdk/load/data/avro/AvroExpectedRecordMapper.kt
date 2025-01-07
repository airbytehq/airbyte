/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.avro

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import java.time.LocalDate
import java.time.ZoneOffset
import java.time.temporal.ChronoField
import java.time.temporal.TemporalAccessor

object AvroExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord {
        return expectedRecord.copy(data = timestampsToInteger(expectedRecord.data) as ObjectValue)
    }

    /**
     * Avro doesn't have true temporal types. Instead, we write dates as epoch days, and other
     * temporal types as epochMicros. Therefore, in expected records, we should convert from real
     * temporal types to IntegerValue.
     */
    private fun timestampsToInteger(value: AirbyteValue): AirbyteValue =
        when (value) {
            is DateValue -> IntegerValue(value.value.toEpochDay())
            is TimestampWithTimezoneValue -> {
                val micros = getMicros(value.value)
                val epochSecond = value.value.toEpochSecond()
                integerValue(epochSecond, micros)
            }
            is TimestampWithoutTimezoneValue -> {
                val micros = getMicros(value.value)
                val epochSecond = value.value.toEpochSecond(ZoneOffset.UTC)
                integerValue(epochSecond, micros)
            }
            is TimeWithTimezoneValue -> {
                val micros = getMicros(value.value)
                val epochSecond = value.value.toEpochSecond(LocalDate.EPOCH)
                integerValue(epochSecond, micros)
            }
            is TimeWithoutTimezoneValue -> {
                val micros = getMicros(value.value)
                val epochSecond = value.value.toEpochSecond(LocalDate.EPOCH, ZoneOffset.UTC)
                integerValue(epochSecond, micros)
            }
            is ArrayValue -> ArrayValue(value.values.map { timestampsToInteger(it) })
            is ObjectValue ->
                ObjectValue(
                    value.values.mapValuesTo(linkedMapOf()) { (_, v) -> timestampsToInteger(v) }
                )
            else -> value
        }

    private fun getMicros(value: TemporalAccessor) = value.getLong(ChronoField.MICRO_OF_SECOND)

    private fun integerValue(epochSecond: Long, micros: Long) =
        IntegerValue(epochSecond * 1_000_000 + micros)
}
