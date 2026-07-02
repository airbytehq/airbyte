/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.write.transform

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
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.ZoneOffset

@Singleton
class DorisCoercer : ValueCoercer {

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
                is NullValue -> abValue
            }
        return value
    }

    override fun validate(value: EnrichedAirbyteValue): ValidationResult =
        when (val abValue = value.abValue) {
            is NumberValue ->
                if (abValue.value <= DECIMAL_MIN || abValue.value >= DECIMAL_MAX) {
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
                if (days < DATE_MIN || days > DATE_MAX) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else ValidationResult.Valid
            }
            is TimestampWithTimezoneValue -> {
                val seconds = abValue.value.toEpochSecond()
                if (seconds < DATETIME_MIN || seconds > DATETIME_MAX) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else ValidationResult.Valid
            }
            is TimestampWithoutTimezoneValue -> {
                val seconds = abValue.value.toEpochSecond(ZoneOffset.UTC)
                if (seconds < DATETIME_MIN || seconds > DATETIME_MAX) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else ValidationResult.Valid
            }
            else -> ValidationResult.Valid
        }

    companion object {
        // Doris BIGINT range
        val INT64_MAX = BigInteger(Long.MAX_VALUE.toString())
        val INT64_MIN = BigInteger(Long.MIN_VALUE.toString())

        // Doris DECIMAL(38,9) limits
        val DECIMAL_MAX = BigDecimal("100000000000000000000000000000")
        val DECIMAL_MIN = BigDecimal("-100000000000000000000000000000")

        // Doris DATE range: 0000-01-01 ~ 9999-12-31 (more permissive than ClickHouse)
        private val DATE_MIN_RAW = LocalDate.of(1, 1, 1)
        private val DATE_MAX_RAW = LocalDate.of(9999, 12, 31)
        val DATE_MIN = DATE_MIN_RAW.toEpochDay()
        val DATE_MAX = DATE_MAX_RAW.toEpochDay()

        // Doris DATETIME range: 0000-01-01 00:00:00 ~ 9999-12-31 23:59:59
        val DATETIME_MIN =
            LocalDateTime.of(DATE_MIN_RAW, LocalTime.MIN).toEpochSecond(ZoneOffset.UTC)
        val DATETIME_MAX =
            LocalDateTime.of(DATE_MAX_RAW, LocalTime.MAX).toEpochSecond(ZoneOffset.UTC)
    }
}
