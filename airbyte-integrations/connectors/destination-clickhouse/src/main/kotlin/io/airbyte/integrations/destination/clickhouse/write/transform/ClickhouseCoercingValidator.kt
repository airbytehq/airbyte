/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.write.transform

import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.integrations.destination.clickhouse.write.transform.ClickhouseCoercingValidator.Constants.DATE32_MAX
import io.airbyte.integrations.destination.clickhouse.write.transform.ClickhouseCoercingValidator.Constants.DATE32_MIN
import io.airbyte.integrations.destination.clickhouse.write.transform.ClickhouseCoercingValidator.Constants.DATETIME64_MAX
import io.airbyte.integrations.destination.clickhouse.write.transform.ClickhouseCoercingValidator.Constants.DATETIME64_MIN
import io.airbyte.integrations.destination.clickhouse.write.transform.ClickhouseCoercingValidator.Constants.DECIMAL128_MAX
import io.airbyte.integrations.destination.clickhouse.write.transform.ClickhouseCoercingValidator.Constants.DECIMAL128_MIN
import io.airbyte.integrations.destination.clickhouse.write.transform.ClickhouseCoercingValidator.Constants.INT64_MAX
import io.airbyte.integrations.destination.clickhouse.write.transform.ClickhouseCoercingValidator.Constants.INT64_MIN
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.ZoneOffset

@Singleton
class ClickhouseCoercingValidator {
    /*
     * Mutative for performance reasons.
     */
    fun validateAndCoerce(value: EnrichedAirbyteValue): EnrichedAirbyteValue {
        when (val abValue = value.abValue) {
            is NumberValue ->
                if (abValue.value <= DECIMAL128_MIN || abValue.value >= DECIMAL128_MAX) {
                    value.nullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                }
            is IntegerValue ->
                if (abValue.value < INT64_MIN || abValue.value > INT64_MAX) {
                    value.nullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                }
            is DateValue -> {
                val days = abValue.value.toEpochDay()
                if (days < DATE32_MIN || days > DATE32_MAX) {
                    value.nullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                }
            }
            is TimestampWithTimezoneValue -> {
                val seconds = abValue.value.toEpochSecond()
                if (seconds < DATETIME64_MIN || seconds > DATETIME64_MAX) {
                    value.nullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                }
            }
            is TimestampWithoutTimezoneValue -> {
                val seconds = abValue.value.toEpochSecond(ZoneOffset.UTC)
                if (seconds < DATETIME64_MIN || seconds > DATETIME64_MAX) {
                    value.nullify(
                        AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION
                    )
                }
            }
            else -> {}
        }

        return value
    }

    object Constants {
        // CH will overflow ints without erroring
        val INT64_MAX = BigInteger(Long.MAX_VALUE.toString())
        val INT64_MIN = BigInteger(Long.MIN_VALUE.toString())

        // below are copied from "deprecated" but still actively used
        // com.clickhouse.data.format.BinaryStreamUtils.DECIMAL64_MAX
        // we can't directly use them because the deprecated status causes a
        // compiler warning which we don't tolerate in CI :smithers:
        val DECIMAL128_MAX = BigDecimal("100000000000000000000000000000000000000")
        val DECIMAL128_MIN = BigDecimal("-100000000000000000000000000000000000000")

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
