/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.write.transform

import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.integrations.destination.starrocks.write.transform.StarrocksValueCoercer.Constants.BIGINT_MAX
import io.airbyte.integrations.destination.starrocks.write.transform.StarrocksValueCoercer.Constants.BIGINT_MIN
import io.airbyte.integrations.destination.starrocks.write.transform.StarrocksValueCoercer.Constants.DATETIME_MAX
import io.airbyte.integrations.destination.starrocks.write.transform.StarrocksValueCoercer.Constants.DATETIME_MIN
import io.airbyte.integrations.destination.starrocks.write.transform.StarrocksValueCoercer.Constants.DATE_MAX
import io.airbyte.integrations.destination.starrocks.write.transform.StarrocksValueCoercer.Constants.DATE_MIN
import io.airbyte.integrations.destination.starrocks.write.transform.StarrocksValueCoercer.Constants.DECIMAL_MAX
import io.airbyte.integrations.destination.starrocks.write.transform.StarrocksValueCoercer.Constants.DECIMAL_MIN
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.ZoneOffset

/**
 * Nullifies values that fall outside the range of their target StarRocks column, recording an
 * Airbyte meta change (`DESTINATION_FIELD_SIZE_LIMITATION`) instead of letting Stream Load reject
 * the whole batch or silently store a wrong value. Issue #27.
 *
 * The schema mapper fixes these column types (see `StarrocksTableSchemaMapper`):
 * - Integer -> BIGINT signed 64-bit (the Long range)
 * - Number -> DECIMAL(38, 9) 29 integer digits, so |value| must be < 10^29
 * - Date -> DATE 0000-01-01 .. 9999-12-31
 * - Timestamp -> DATETIME 0000-01-01 00:00:00 .. 9999-12-31 23:59:59
 *
 * Mirrors destination-clickhouse's `ClickhouseCoercer` / destination-postgres's
 * `PostgresValueCoercer`. Registered as the active [ValueCoercer]: the CDK's default `NoOpCoercer`
 * is `@Secondary`, so this `@Singleton` takes precedence with no extra wiring.
 */
@Singleton
class StarrocksValueCoercer : ValueCoercer {

    /**
     * No structural remapping needed. The CSV/JSON Stream Load buffers already serialize every
     * [io.airbyte.cdk.load.data.AirbyteValue] subtype exhaustively (objects/arrays/unions all land
     * as text), so — unlike ClickHouse/Postgres — there is nothing to coerce here.
     */
    override fun map(value: EnrichedAirbyteValue): EnrichedAirbyteValue = value

    override fun validate(value: EnrichedAirbyteValue): ValidationResult =
        when (val abValue = value.abValue) {
            is IntegerValue ->
                if (abValue.value < BIGINT_MIN || abValue.value > BIGINT_MAX) sizeLimit()
                else ValidationResult.Valid
            is NumberValue ->
                // 10^29 itself overflows DECIMAL(38, 9) (30 integer digits), hence `<=`/`>=`.
                if (abValue.value <= DECIMAL_MIN || abValue.value >= DECIMAL_MAX) sizeLimit()
                else ValidationResult.Valid
            is DateValue -> {
                val days = abValue.value.toEpochDay()
                if (days < DATE_MIN || days > DATE_MAX) sizeLimit() else ValidationResult.Valid
            }
            is TimestampWithTimezoneValue -> {
                val seconds = abValue.value.toEpochSecond()
                if (seconds < DATETIME_MIN || seconds > DATETIME_MAX) sizeLimit()
                else ValidationResult.Valid
            }
            is TimestampWithoutTimezoneValue -> {
                val seconds = abValue.value.toEpochSecond(ZoneOffset.UTC)
                if (seconds < DATETIME_MIN || seconds > DATETIME_MAX) sizeLimit()
                else ValidationResult.Valid
            }
            else -> ValidationResult.Valid
        }

    private fun sizeLimit(): ValidationResult.ShouldNullify =
        ValidationResult.ShouldNullify(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
        )

    object Constants {
        // BIGINT is signed 64-bit: exactly the Long range (both bounds inclusive).
        val BIGINT_MAX: BigInteger = BigInteger.valueOf(Long.MAX_VALUE)
        val BIGINT_MIN: BigInteger = BigInteger.valueOf(Long.MIN_VALUE)

        // DECIMAL(38, 9) keeps 29 integer digits; any |value| >= 10^29 overflows. Excess fractional
        // digits are rounded by StarRocks (not rejected), so only the magnitude is checked.
        val DECIMAL_MAX: BigDecimal = BigDecimal.TEN.pow(29)
        val DECIMAL_MIN: BigDecimal = DECIMAL_MAX.negate()

        // StarRocks DATE/DATETIME both span 0000-01-01 .. 9999-12-31.
        private val MIN_DATE: LocalDate = LocalDate.of(0, 1, 1)
        private val MAX_DATE: LocalDate = LocalDate.of(9999, 12, 31)

        val DATE_MIN: Long = MIN_DATE.toEpochDay()
        val DATE_MAX: Long = MAX_DATE.toEpochDay()

        val DATETIME_MIN: Long =
            LocalDateTime.of(MIN_DATE, LocalTime.MIN).toEpochSecond(ZoneOffset.UTC)
        val DATETIME_MAX: Long =
            LocalDateTime.of(MAX_DATE, LocalTime.MAX).toEpochSecond(ZoneOffset.UTC)
    }
}
