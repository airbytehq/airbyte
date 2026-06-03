/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc

import io.debezium.spi.converter.CustomConverter
import io.debezium.spi.converter.RelationalColumn
import io.mockk.every
import io.mockk.mockk
import io.mockk.slot
import java.util.HexFormat
import java.util.OptionalInt
import org.apache.kafka.connect.data.SchemaBuilder
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

/**
 * Tests the PostGIS geometry/geography handling on the CDC path. Before the fix these types matched
 * nothing in [PostgresCustomConverter.converterFor], so Debezium registered no converter and the
 * CDC path emitted NULL (DATA-442 / airbytehq/airbyte#79109).
 *
 * Unlike a test that feeds fabricated text, the conversion assertions use a real EWKB payload and
 * assert the actual canonical EWKT, so they would catch a handler that merely UTF-8-decodes raw WKB
 * bytes into garbage.
 */
class PostgresCustomConverterTest {

    private val converter = PostgresCustomConverter()

    // EWKB for SRID=4326;POINT(1 2). See PostgisGeometryTest for the byte breakdown.
    private val pointHex = "0101000020E6100000000000000000F03F0000000000000040"
    private val expectedEwkt = "SRID=4326;POINT(1 2)"

    private fun mockField(typeName: String): RelationalColumn {
        val field = mockk<RelationalColumn>()
        every { field.typeName() } returns typeName
        every { field.isOptional } returns true
        every { field.hasDefaultValue() } returns false
        every { field.defaultValue() } returns null
        every { field.scale() } returns OptionalInt.empty()
        every { field.length() } returns OptionalInt.empty()
        return field
    }

    private fun captureConverter(typeName: String): CustomConverter.Converter {
        val field = mockField(typeName)
        val registration = mockk<CustomConverter.ConverterRegistration<SchemaBuilder?>>()
        val converterSlot = slot<CustomConverter.Converter>()
        every { registration.register(any(), capture(converterSlot)) } returns Unit
        converter.converterFor(field, registration)
        assertTrue(converterSlot.isCaptured) {
            "Expected converterFor() to register a handler for PostGIS type '$typeName'"
        }
        return converterSlot.captured
    }

    @ParameterizedTest
    @ValueSource(strings = ["GEOMETRY", "GEOGRAPHY", "geometry", "geography"])
    fun `registers a handler for PostGIS types (case-insensitive)`(typeName: String) {
        captureConverter(typeName)
    }

    @ParameterizedTest
    @ValueSource(strings = ["GEOMETRY", "GEOGRAPHY"])
    fun `converts hex-EWKB to canonical EWKT`(typeName: String) {
        assertEquals(expectedEwkt, captureConverter(typeName).convert(pointHex))
    }

    @ParameterizedTest
    @ValueSource(strings = ["GEOMETRY", "GEOGRAPHY"])
    fun `converts raw WKB bytes to canonical EWKT`(typeName: String) {
        val wkbBytes: ByteArray = HexFormat.of().parseHex(pointHex)
        assertEquals(expectedEwkt, captureConverter(typeName).convert(wkbBytes))
    }

    @Test
    fun `returns null for a null geometry value`() {
        assertNull(captureConverter("GEOMETRY").convert(null))
    }
}
