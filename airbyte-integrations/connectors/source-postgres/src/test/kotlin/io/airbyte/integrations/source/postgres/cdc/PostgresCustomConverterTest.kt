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
import kotlin.test.assertEquals
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
    fun `microsecondsToPgInterval decomposes microseconds into days hours minutes seconds`() {
        val result = PostgresCustomConverter().microsecondsToPgInterval(90_061_000_000L)

        assertEquals(PGInterval(0, 0, 1, 1, 1, 1.0), result)
    }

    @Test
    fun `microsecondsToPgInterval decomposes negative microseconds`() {
        val result = PostgresCustomConverter().microsecondsToPgInterval(-90_061_000_000L)

        assertEquals(PGInterval(0, 0, -1, -1, -1, -1.0), result)
    }

    private fun converterFor(defaultValue: Long): CustomConverter.Converter {
        val field = mockk<RelationalColumn>()
        every { field.typeName() } returns "interval"
        every { field.isOptional() } returns false
        every { field.hasDefaultValue() } returns true
        every { field.defaultValue() } returns defaultValue

        val registration = mockk<CustomConverter.ConverterRegistration<SchemaBuilder?>>()
        val converter = slot<CustomConverter.Converter>()
        every { registration.register(any(), capture(converter)) } returns Unit

        PostgresCustomConverter().converterFor(field, registration)

        verify { registration.register(any(), any()) }
        return converter.captured
    }
}
