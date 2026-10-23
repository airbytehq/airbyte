/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.postgres.cdc

import io.debezium.spi.converter.CustomConverter
import io.debezium.spi.converter.RelationalColumn
import io.mockk.every
import io.mockk.mockk
import io.mockk.slot
import io.mockk.verify
import java.math.BigDecimal
import kotlin.test.assertEquals
import kotlin.test.assertNull
import org.apache.kafka.connect.data.SchemaBuilder
import org.junit.jupiter.api.Test
import org.postgresql.util.PGInterval

class PostgresCustomConverterTest {

    @Test
    fun `converts interval default value represented as microseconds`() {
        val converter = converterFor(defaultValue = 90_061_000_000L)

        assertEquals("1 days 01:01:01", converter.convert(null))
    }

    @Test
    fun `converts interval PGInterval value`() {
        val converter = converterFor(defaultValue = 0L)

        assertEquals("1 days 02:03:04", converter.convert(PGInterval(0, 0, 1, 2, 3, 4.0)))
    }

    @Test
    fun `converts negative interval default value represented as microseconds`() {
        val converter = converterFor(defaultValue = -90_061_000_000L)

        assertEquals("-1 days -01:01:01", converter.convert(null))
    }

    @Test
    fun `preserves precision of large numeric values`() {
        val converter = converterFor(typeName = "numeric")

        assertEquals(
            "12345678901234567890123456789012345",
            converter.convert(BigDecimal("12345678901234567890123456789012345")),
        )
        assertEquals("9007199254740993", converter.convert(BigDecimal("9007199254740993")))
        assertEquals(
            "99999999999999999999",
            converter.convert(BigDecimal("99999999999999999999")),
        )
    }

    @Test
    fun `preserves fractional numeric precision`() {
        val converter = converterFor(typeName = "numeric")

        assertEquals(
            "1234567890.123456789",
            converter.convert(BigDecimal("1234567890.1234567890")),
        )
    }

    @Test
    fun `strips trailing zeros from numeric values`() {
        val converter = converterFor(typeName = "numeric")

        assertEquals("123", converter.convert(BigDecimal("123.000")))
        assertEquals("0", converter.convert(BigDecimal("0.00")))
    }

    @Test
    fun `returns null for a null numeric value without a default`() {
        val converter =
            converterFor(
                typeName = "numeric",
                defaultValue = null,
                hasDefaultValue = false,
            )

        assertNull(converter.convert(null))
    }

    @Test
    fun `microsecondsToPgInterval decomposes microseconds into days hours minutes seconds`() {
        val result = PostgresCustomConverter().microsecondsToPgInterval(90_061_000_000L)

        assertEquals(PGInterval(0, 0, 1, 1, 1, 1.0), result)
    }

    @Test
    fun `microsecondsToPgInterval decomposes negative microseconds`() {
        val result = PostgresCustomConverter().microsecondsToPgInterval(-90_061_000_000L)

        assertEquals(PGInterval(0, 0, -1, -1, -1, -1.0), result)
    }

    private fun converterFor(
        defaultValue: Any? = 0L,
        typeName: String = "interval",
        hasDefaultValue: Boolean = true,
    ): CustomConverter.Converter {
        val field = mockk<RelationalColumn>()
        every { field.typeName() } returns typeName
        every { field.isOptional() } returns false
        every { field.hasDefaultValue() } returns hasDefaultValue
        every { field.defaultValue() } returns defaultValue

        val registration = mockk<CustomConverter.ConverterRegistration<SchemaBuilder?>>()
        val converter = slot<CustomConverter.Converter>()
        every { registration.register(any(), capture(converter)) } returns Unit

        PostgresCustomConverter().converterFor(field, registration)

        verify { registration.register(any(), any()) }
        return converter.captured
    }
}
