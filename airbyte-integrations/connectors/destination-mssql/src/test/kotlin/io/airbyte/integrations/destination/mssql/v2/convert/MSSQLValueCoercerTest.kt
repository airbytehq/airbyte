/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2.convert

import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.util.deserializeToNode
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test

class MSSQLValueCoercerTest {

    // ── helpers ──────────────────────────────────────────────────────────────────

    private fun makeTimestampValue(ts: LocalDateTime): EnrichedAirbyteValue =
        EnrichedAirbyteValue(
            abValue = TimestampWithoutTimezoneValue(ts),
            type = TimestampTypeWithoutTimezone,
            name = "test_timestamp",
            airbyteMetaField = null,
        )

    private fun makeIntegerValue(v: BigInteger): EnrichedAirbyteValue =
        EnrichedAirbyteValue(
            abValue = IntegerValue(v),
            type = IntegerType,
            name = "test_integer",
            airbyteMetaField = null,
        )

    private fun makeNumberValue(v: BigDecimal): EnrichedAirbyteValue =
        EnrichedAirbyteValue(
            abValue = NumberValue(v),
            type = NumberType,
            name = "test_number",
            airbyteMetaField = null,
        )

    // ── validateTimestamp ────────────────────────────────────────────────────────

    @Nested
    inner class ValidateTimestampTests {

        @Test
        fun `passes through value within DATETIME range`() {
            val value = makeTimestampValue(LocalDateTime.of(2023, 6, 15, 12, 34, 56))
            val result = MSSQLValueCoercer.validateTimestamp(value)
            assertNotNull(result)
            assertEquals(LocalDateTime.of(2023, 6, 15, 12, 34, 56), result)
            assertTrue(value.abValue is TimestampWithoutTimezoneValue)
        }

        @Test
        fun `passes through value at exact lower boundary`() {
            val value = makeTimestampValue(LocalDateTime.of(1753, 1, 1, 0, 0, 0))
            val result = MSSQLValueCoercer.validateTimestamp(value)
            assertNotNull(result)
            assertEquals(LocalDateTime.of(1753, 1, 1, 0, 0, 0), result)
            assertTrue(value.abValue is TimestampWithoutTimezoneValue)
        }

        @Test
        fun `nullifies value below DATETIME lower boundary`() {
            val value = makeTimestampValue(LocalDateTime.of(1752, 12, 31, 23, 59, 59))
            val result = MSSQLValueCoercer.validateTimestamp(value)
            assertNull(result)
            assertTrue(value.abValue is NullValue)
            assertEquals(1, value.changes.size)
        }

        @Test
        fun `nullifies pre-1753 date`() {
            val value = makeTimestampValue(LocalDateTime.of(1, 1, 1, 0, 0, 0))
            val result = MSSQLValueCoercer.validateTimestamp(value)
            assertNull(result)
            assertTrue(value.abValue is NullValue)
            assertEquals(1, value.changes.size)
        }
    }

    // ── validateInteger ─────────────────────────────────────────────────────────

    @Nested
    inner class ValidateIntegerTests {

        @Test
        fun `passes through value within BIGINT range`() {
            val value = makeIntegerValue(BigInteger("42"))
            val result = MSSQLValueCoercer.validateInteger(value)
            assertNotNull(result)
            assertEquals(BigInteger("42"), result)
            assertTrue(value.abValue is IntegerValue)
        }

        @Test
        fun `passes through MAX_BIGINT`() {
            val value = makeIntegerValue(MSSQLValueCoercer.MAX_BIGINT)
            val result = MSSQLValueCoercer.validateInteger(value)
            assertNotNull(result)
            assertEquals(MSSQLValueCoercer.MAX_BIGINT, result)
        }

        @Test
        fun `passes through MIN_BIGINT`() {
            val value = makeIntegerValue(MSSQLValueCoercer.MIN_BIGINT)
            val result = MSSQLValueCoercer.validateInteger(value)
            assertNotNull(result)
            assertEquals(MSSQLValueCoercer.MIN_BIGINT, result)
        }

        @Test
        fun `nullifies value above MAX_BIGINT`() {
            val value = makeIntegerValue(MSSQLValueCoercer.MAX_BIGINT + BigInteger.ONE)
            val result = MSSQLValueCoercer.validateInteger(value)
            assertNull(result)
            assertTrue(value.abValue is NullValue)
            assertEquals(1, value.changes.size)
        }

        @Test
        fun `nullifies value below MIN_BIGINT`() {
            val value = makeIntegerValue(MSSQLValueCoercer.MIN_BIGINT - BigInteger.ONE)
            val result = MSSQLValueCoercer.validateInteger(value)
            assertNull(result)
            assertTrue(value.abValue is NullValue)
            assertEquals(1, value.changes.size)
        }
    }

    // ── validateNumber ──────────────────────────────────────────────────────────

    @Nested
    inner class ValidateNumberTests {

        @Test
        fun `passes through value within DECIMAL range`() {
            val value = makeNumberValue(BigDecimal("123.456"))
            val result = MSSQLValueCoercer.validateNumber(value)
            assertNotNull(result)
            assertEquals(BigDecimal("123.456"), result)
        }

        @Test
        fun `nullifies value above MAX_NUMERIC`() {
            val value = makeNumberValue(MSSQLValueCoercer.MAX_NUMERIC + BigDecimal.ONE)
            val result = MSSQLValueCoercer.validateNumber(value)
            assertNull(result)
            assertTrue(value.abValue is NullValue)
            assertEquals(1, value.changes.size)
        }

        @Test
        fun `nullifies value below MIN_NUMERIC`() {
            val value = makeNumberValue(MSSQLValueCoercer.MIN_NUMERIC - BigDecimal.ONE)
            val result = MSSQLValueCoercer.validateNumber(value)
            assertNull(result)
            assertTrue(value.abValue is NullValue)
            assertEquals(1, value.changes.size)
        }
    }

    // ── coerce ──────────────────────────────────────────────────────────────────

    @Nested
    inner class CoerceTests {

        @Test
        fun `is a no-op for NullValue`() {
            val value =
                EnrichedAirbyteValue(
                    abValue = NullValue,
                    type = IntegerType,
                    name = "n",
                    airbyteMetaField = null,
                )
            MSSQLValueCoercer.coerce(value)
            assertTrue(value.abValue is NullValue)
        }

        @Test
        fun `does not modify valid integers`() {
            val value = makeIntegerValue(BigInteger("100"))
            MSSQLValueCoercer.coerce(value)
            assertEquals(IntegerValue(BigInteger("100")), value.abValue)
        }

        @Test
        fun `nullifies out-of-range integers`() {
            val value = makeIntegerValue(MSSQLValueCoercer.MAX_BIGINT + BigInteger.ONE)
            MSSQLValueCoercer.coerce(value)
            assertTrue(value.abValue is NullValue)
        }

        @Test
        fun `does not modify valid numbers`() {
            val value = makeNumberValue(BigDecimal("3.14"))
            MSSQLValueCoercer.coerce(value)
            assertEquals(NumberValue(BigDecimal("3.14")), value.abValue)
        }

        @Test
        fun `nullifies out-of-range numbers`() {
            val value = makeNumberValue(MSSQLValueCoercer.MAX_NUMERIC + BigDecimal.ONE)
            MSSQLValueCoercer.coerce(value)
            assertTrue(value.abValue is NullValue)
        }

        @Test
        fun `validates but does not modify valid timestamps without timezone`() {
            val ts = LocalDateTime.of(2023, 6, 15, 12, 0, 0)
            val value = makeTimestampValue(ts)
            MSSQLValueCoercer.coerce(value)
            assertEquals(TimestampWithoutTimezoneValue(ts), value.abValue)
        }

        @Test
        fun `nullifies pre-1753 timestamps without timezone`() {
            val value = makeTimestampValue(LocalDateTime.of(1, 1, 1, 0, 0, 0))
            MSSQLValueCoercer.coerce(value)
            assertTrue(value.abValue is NullValue)
        }

        @Test
        fun `serialises ObjectValue to StringValue`() {
            val obj = ObjectValue.from(mapOf("key" to StringValue("val")))
            val value =
                EnrichedAirbyteValue(
                    abValue = obj,
                    type = ObjectType(linkedMapOf("key" to FieldType(StringType, true))),
                    name = "obj_field",
                    airbyteMetaField = null,
                )
            MSSQLValueCoercer.coerce(value)
            assertTrue(value.abValue is StringValue)
        }

        @Test
        fun `serialises ArrayValue to StringValue`() {
            val arr = ArrayValue(listOf(IntegerValue(1), IntegerValue(2)))
            val value =
                EnrichedAirbyteValue(
                    abValue = arr,
                    type = ArrayType(FieldType(IntegerType, true)),
                    name = "arr_field",
                    airbyteMetaField = null,
                )
            MSSQLValueCoercer.coerce(value)
            assertTrue(value.abValue is StringValue)
        }

        @Test
        fun `serialises UnknownType to StringValue`() {
            val value =
                EnrichedAirbyteValue(
                    abValue = StringValue("unknown_blob"),
                    type = UnknownType("\"custom\"".deserializeToNode()),
                    name = "unk_field",
                    airbyteMetaField = null,
                )
            MSSQLValueCoercer.coerce(value)
            assertTrue(value.abValue is StringValue)
        }

        @Test
        fun `does not modify booleans (path-specific concern)`() {
            val value =
                EnrichedAirbyteValue(
                    abValue = BooleanValue(true),
                    type = BooleanType,
                    name = "flag",
                    airbyteMetaField = null,
                )
            MSSQLValueCoercer.coerce(value)
            assertEquals(BooleanValue(true), value.abValue)
        }

        @Test
        fun `does not modify dates`() {
            val value =
                EnrichedAirbyteValue(
                    abValue = DateValue("2023-06-15"),
                    type = DateType,
                    name = "dt",
                    airbyteMetaField = null,
                )
            MSSQLValueCoercer.coerce(value)
            assertEquals(DateValue("2023-06-15"), value.abValue)
        }

        @Test
        fun `does not modify strings`() {
            val value =
                EnrichedAirbyteValue(
                    abValue = StringValue("hello"),
                    type = StringType,
                    name = "s",
                    airbyteMetaField = null,
                )
            MSSQLValueCoercer.coerce(value)
            assertEquals(StringValue("hello"), value.abValue)
        }

        @Test
        fun `does not modify timestamps with timezone`() {
            val ts = OffsetDateTime.of(2023, 6, 15, 12, 0, 0, 0, ZoneOffset.UTC)
            val value =
                EnrichedAirbyteValue(
                    abValue = TimestampWithTimezoneValue(ts),
                    type = TimestampTypeWithTimezone,
                    name = "ts_tz",
                    airbyteMetaField = null,
                )
            MSSQLValueCoercer.coerce(value)
            assertEquals(TimestampWithTimezoneValue(ts), value.abValue)
        }
    }
}
