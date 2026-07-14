/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.write.transform

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
class MySQLCoercer : ValueCoercer {

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
                val year = abValue.value.year
                if (year < DATE_MIN_YEAR || year > DATE_MAX_YEAR) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else ValidationResult.Valid
            }
            is TimestampWithTimezoneValue -> {
                val year = abValue.value.year
                if (year < DATETIME_MIN_YEAR || year > DATETIME_MAX_YEAR) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else ValidationResult.Valid
            }
            is TimestampWithoutTimezoneValue -> {
                val year = abValue.value.year
                if (year < DATETIME_MIN_YEAR || year > DATETIME_MAX_YEAR) {
                    ValidationResult.ShouldNullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                } else ValidationResult.Valid
            }
            else -> {
                ValidationResult.Valid
            }
        }

    companion object {
        // MySQL BIGINT range
        val INT64_MAX = BigInteger(Long.MAX_VALUE.toString())
        val INT64_MIN = BigInteger(Long.MIN_VALUE.toString())

        // MySQL DECIMAL(38, 9) range (scaled by 10^-9 for 9 decimal places)
        val DECIMAL_MAX = BigDecimal("100000000000000000000000000000")
        val DECIMAL_MIN = BigDecimal("-100000000000000000000000000000")

        // MySQL DATE range: '1000-01-01' to '9999-12-31'
        const val DATE_MIN_YEAR = 1000
        const val DATE_MAX_YEAR = 9999

        // MySQL DATETIME range: '1000-01-01 00:00:00' to '9999-12-31 23:59:59'
        const val DATETIME_MIN_YEAR = 1000
        const val DATETIME_MAX_YEAR = 9999
    }
}
