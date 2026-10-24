/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.write.transform

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Test

class StarrocksValueCoercerTest {

    private val coercer = StarrocksValueCoercer()

    private fun enriched(value: AirbyteValue, type: AirbyteType) =
        EnrichedAirbyteValue(abValue = value, type = type, name = "col", airbyteMetaField = null)

    private fun assertValid(value: AirbyteValue, type: AirbyteType) =
        assertEquals(ValidationResult.Valid, coercer.validate(enriched(value, type)))

    private fun assertNullified(value: AirbyteValue, type: AirbyteType) {
        val result = coercer.validate(enriched(value, type))
        val nullify = assertInstanceOf(ValidationResult.ShouldNullify::class.java, result)
        assertEquals(
            AirbyteRecordMessageMetaChange.Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            nullify.reason,
        )
    }

    @Test
    fun `integers within BIGINT range are valid, out-of-range are nullified`() {
        assertValid(IntegerValue(BigInteger.ZERO), IntegerType)
        assertValid(IntegerValue(BigInteger.valueOf(Long.MAX_VALUE)), IntegerType)
        assertValid(IntegerValue(BigInteger.valueOf(Long.MIN_VALUE)), IntegerType)

        assertNullified(
            IntegerValue(BigInteger.valueOf(Long.MAX_VALUE).add(BigInteger.ONE)),
            IntegerType
        )
        assertNullified(
            IntegerValue(BigInteger.valueOf(Long.MIN_VALUE).subtract(BigInteger.ONE)),
            IntegerType
        )
    }

    @Test
    fun `decimals within DECIMAL(38,9) magnitude are valid, overflow is nullified`() {
        assertValid(NumberValue(BigDecimal("123.456")), NumberType)
        assertValid(NumberValue(BigDecimal.TEN.pow(28)), NumberType) // 10^28, 29 integer digits
        assertValid(NumberValue(BigDecimal.TEN.pow(28).negate()), NumberType)

        assertNullified(
            NumberValue(BigDecimal.TEN.pow(29)),
            NumberType
        ) // 10^29 -> 30 integer digits
        assertNullified(NumberValue(BigDecimal.TEN.pow(29).negate()), NumberType)
        assertNullified(NumberValue(BigDecimal("1E40")), NumberType)
    }

    @Test
    fun `dates within DATE range are valid, out-of-range are nullified`() {
        assertValid(DateValue(LocalDate.of(2026, 6, 25)), DateType)
        assertValid(DateValue(LocalDate.of(9999, 12, 31)), DateType)
        assertValid(DateValue(LocalDate.of(0, 1, 1)), DateType)

        assertNullified(DateValue(LocalDate.of(10000, 1, 1)), DateType)
        assertNullified(DateValue(LocalDate.of(-1, 12, 31)), DateType)
    }

    @Test
    fun `timestamps within DATETIME range are valid, out-of-range are nullified`() {
        val tzIn = OffsetDateTime.of(2026, 6, 25, 12, 0, 0, 0, ZoneOffset.UTC)
        val tzOut = OffsetDateTime.of(10000, 1, 1, 0, 0, 0, 0, ZoneOffset.UTC)
        assertValid(TimestampWithTimezoneValue(tzIn), TimestampTypeWithTimezone)
        assertNullified(TimestampWithTimezoneValue(tzOut), TimestampTypeWithTimezone)

        val ntzIn = LocalDateTime.of(2026, 6, 25, 12, 0, 0)
        val ntzOut = LocalDateTime.of(10000, 1, 1, 0, 0, 0)
        assertValid(TimestampWithoutTimezoneValue(ntzIn), TimestampTypeWithoutTimezone)
        assertNullified(TimestampWithoutTimezoneValue(ntzOut), TimestampTypeWithoutTimezone)
    }

    @Test
    fun `unconstrained types pass through as valid`() {
        assertValid(StringValue("anything"), StringType)
        assertValid(BooleanValue(true), BooleanType)
    }

    @Test
    fun `map is identity (buffers serialize every value type already)`() {
        val v = enriched(IntegerValue(BigInteger.ONE), IntegerType)
        assertSame(v, coercer.map(v))
    }
}
