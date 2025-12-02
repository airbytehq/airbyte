/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.write.transform

import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.integrations.destination.clickhouse.write.transform.ClickhouseCoercer.Constants.DATE32_MAX
import io.airbyte.integrations.destination.clickhouse.write.transform.ClickhouseCoercer.Constants.DATE32_MIN
import io.airbyte.integrations.destination.clickhouse.write.transform.ClickhouseCoercer.Constants.DATETIME64_MAX
import io.airbyte.integrations.destination.clickhouse.write.transform.ClickhouseCoercer.Constants.DATETIME64_MIN
import io.airbyte.integrations.destination.clickhouse.write.transform.ClickhouseCoercer.Constants.DECIMAL128_MAX
import io.airbyte.integrations.destination.clickhouse.write.transform.ClickhouseCoercer.Constants.DECIMAL128_MIN
import io.airbyte.integrations.destination.clickhouse.write.transform.ClickhouseCoercer.Constants.INT64_MAX
import io.airbyte.integrations.destination.clickhouse.write.transform.ClickhouseCoercer.Constants.INT64_MIN
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.ZoneOffset

@Singleton
class ClickhouseCoercer : ValueCoercer {

    override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        return when (value.type) {
            is UnionType -> toJsonStringValue(value)
            else -> value
        }
    }

    private fun toJsonStringValue(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        value.abValue =
            when (val abValue = value.abValue) {
                is ObjectValue -> StringValue(abValue.values.serializeToString())
                is ArrayValue -> StringValue(abValue.values.serializeToString())
                is BooleanValue -> StringValue(abValue.value.serializeToString())
                is IntegerValue -> StringValue(abValue.value.serializeToString())
                is NumberValue -> StringValue(abValue.value.serializeToString())
                is DateValue -> StringValue(abValue.value.serializeToString())
                is TimeWithTimezoneValue -> StringValue(abValue.value.serializeToString())
                is TimeWithoutTimezoneValue -> StringValue(abValue.value.serializeToString())
                is TimestampWithTimezoneValue -> StringValue(abValue.value.serializeToString())
                is TimestampWithoutTimezoneValue -> StringValue(abValue.value.serializeToString())
                is StringValue -> StringValue(abValue.value.serializeToString())
                is NullValue -> abValue // Consider null a valid string
            }

        return value
    }

    override fun validate(value: EnrichedAirbyteValue): ValidationResult =
        when (val abValue = value.abValue) {
            is NumberValue ->
                if (abValue.value <= DECIMAL128_MIN || abValue.value >= DECIMAL128_MAX) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else ValidationResult.Valid
            is IntegerValue ->
                if (abValue.value < INT64_MIN || abValue.value > INT64_MAX) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else ValidationResult.Valid
            is DateValue -> {
                val days = abValue.value.toEpochDay()
                if (days < DATE32_MIN || days > DATE32_MAX) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else ValidationResult.Valid
            }
            is TimestampWithTimezoneValue -> {
                val seconds = abValue.value.toEpochSecond()
                if (seconds < DATETIME64_MIN || seconds > DATETIME64_MAX) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else ValidationResult.Valid
            }
            is TimestampWithoutTimezoneValue -> {
                val seconds = abValue.value.toEpochSecond(ZoneOffset.UTC)
                if (seconds < DATETIME64_MIN || seconds > DATETIME64_MAX) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else ValidationResult.Valid
            }
            else -> {
                ValidationResult.Valid
            }
        }

    object Constants {
        // CH will overflow ints without erroring
        val INT64_MAX = BigInteger(Long.MAX_VALUE.toString())
        val INT64_MIN = BigInteger(Long.MIN_VALUE.toString())

        // below are copied from "deprecated" but still actively used
        // com.clickhouse.data.format.BinaryStreamUtils
        // we can't directly use them because the deprecated status causes a
        // compiler warning which we don't tolerate in CI :smithers:
        //
        // Further scale the CH defined limits by -9 (our defined scale for decimals) to mimic their
        // scaling without the overhead (they multiply every value by the scale before comparison).
        val DECIMAL128_MAX = BigDecimal("100000000000000000000000000000")
        val DECIMAL128_MIN = BigDecimal("-100000000000000000000000000000")

        // used by both date 32 and date time 64
        val DATE32_MAX_RAW = LocalDate.of(2299, 12, 31)
        val DATE32_MIN_RAW = LocalDate.of(1900, 1, 1)

        val DATE32_MAX = DATE32_MAX_RAW.toEpochDay()
        val DATE32_MIN = DATE32_MIN_RAW.toEpochDay()

        val DATETIME64_MAX =
            LocalDateTime.of(DATE32_MAX_RAW, LocalTime.MAX).toEpochSecond(ZoneOffset.UTC)
        val DATETIME64_MIN =
            LocalDateTime.of(DATE32_MIN_RAW, LocalTime.MIN).toEpochSecond(ZoneOffset.UTC)
    }
}
