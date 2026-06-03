/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres

import io.airbyte.integrations.source.postgres.cdc.PostgresCustomConverter
import io.debezium.spi.converter.CustomConverter
import io.debezium.spi.converter.RelationalColumn
import io.mockk.every
import io.mockk.mockk
import io.mockk.slot
import java.util.OptionalInt
import org.apache.kafka.connect.data.SchemaBuilder
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

class PostgresCustomConverterTest {

    private val converter = PostgresCustomConverter()

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

    /**
     * Verify that PostGIS geometry/geography types are handled by the converter (i.e., a converter
     * function IS registered). Before the fix, these types fell through converterFor() without
     * registering, causing Debezium to emit null values on the CDC path.
     */
    @ParameterizedTest
    @ValueSource(strings = ["GEOMETRY", "GEOGRAPHY", "geometry", "geography"])
    fun `converterFor registers a handler for PostGIS types`(typeName: String) {
        val field = mockField(typeName)
        val registration = mockk<CustomConverter.ConverterRegistration<SchemaBuilder?>>()

        val schemaSlot = slot<SchemaBuilder>()
        val converterSlot = slot<CustomConverter.Converter>()
        every { registration.register(capture(schemaSlot), capture(converterSlot)) } returns Unit

        converter.converterFor(field, registration)

        assert(schemaSlot.isCaptured) {
            "Expected converterFor() to register a handler for PostGIS type '$typeName', " +
                "but no handler was registered"
        }
    }

    /**
     * Verify that the registered converter for PostGIS types correctly converts non-null values to
     * their string representation via toString().
     */
    @ParameterizedTest
    @ValueSource(strings = ["GEOMETRY", "GEOGRAPHY"])
    fun `PostGIS converter converts values to string via toString`(typeName: String) {
        val field = mockField(typeName)
        val registration = mockk<CustomConverter.ConverterRegistration<SchemaBuilder?>>()

        val converterSlot = slot<CustomConverter.Converter>()
        every { registration.register(any(), capture(converterSlot)) } returns Unit

        converter.converterFor(field, registration)

        val capturedConverter = converterSlot.captured

        // Simulate a PostGIS value object whose toString() returns a WKB hex string
        val mockGeomValue =
            object {
                override fun toString(): String =
                    "0101000020E6100000000000000000F03F0000000000000040"
            }
        val result = capturedConverter.convert(mockGeomValue)
        assertEquals("0101000020E6100000000000000000F03F0000000000000040", result)
    }

    /** Verify that the converter returns null for null PostGIS values. */
    @Test
    fun `PostGIS converter returns null for null input`() {
        val field = mockField("GEOMETRY")
        every { field.hasDefaultValue() } returns false
        val registration = mockk<CustomConverter.ConverterRegistration<SchemaBuilder?>>()

        val converterSlot = slot<CustomConverter.Converter>()
        every { registration.register(any(), capture(converterSlot)) } returns Unit

        converter.converterFor(field, registration)
        val result = converterSlot.captured.convert(null)
        assertNull(result)
    }

    /** Verify that native geometric types (BOX, CIRCLE, etc.) are still handled. */
    @ParameterizedTest
    @ValueSource(strings = ["BOX", "CIRCLE", "LINE", "LSEG", "POINT", "POLYGON", "PATH"])
    fun `converterFor still registers handlers for native geometric types`(typeName: String) {
        val field = mockField(typeName)
        val registration = mockk<CustomConverter.ConverterRegistration<SchemaBuilder?>>()

        val schemaSlot = slot<SchemaBuilder>()
        every {
            registration.register(capture(schemaSlot), any<CustomConverter.Converter>())
        } returns Unit

        converter.converterFor(field, registration)

        assert(schemaSlot.isCaptured) {
            "Expected converterFor() to register a handler for native type '$typeName'"
        }
    }

    /** Verify that PostGIS converter handles byte array values (binary WKB from Debezium). */
    @Test
    fun `PostGIS converter handles byte array input`() {
        val field = mockField("GEOMETRY")
        val registration = mockk<CustomConverter.ConverterRegistration<SchemaBuilder?>>()

        val converterSlot = slot<CustomConverter.Converter>()
        every { registration.register(any(), capture(converterSlot)) } returns Unit

        converter.converterFor(field, registration)

        val wkbBytes = "POINT(1 2)".toByteArray(Charsets.UTF_8)
        val result = converterSlot.captured.convert(wkbBytes)
        // registerText calls getTextConvertedValue which converts ByteArray to UTF-8 string
        assertEquals("POINT(1 2)", result)
    }
}
