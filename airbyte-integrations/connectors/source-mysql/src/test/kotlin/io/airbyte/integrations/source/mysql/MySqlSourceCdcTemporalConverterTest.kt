/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.debezium.spi.converter.CustomConverter
import io.debezium.spi.converter.RelationalColumn
import io.mockk.CapturingSlot
import io.mockk.Runs
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.slot
import java.time.LocalDate
import java.time.LocalDateTime
import java.util.OptionalInt
import org.apache.kafka.connect.data.SchemaBuilder
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

class MySqlSourceCdcTemporalConverterTest {

    @ParameterizedTest
    @MethodSource("requiredDateAndDatetimeZeroDateCases")
    fun `required DATE and DATETIME null values convert to epoch`(
        typeName: String,
        length: Int,
        expected: String,
    ) {
        val converter = registeredConverter(typeName, length, optional = false)

        assertEquals(expected, converter.convert(null))
    }

    @ParameterizedTest
    @MethodSource("nullableDateAndDatetimeZeroDateCases")
    fun `nullable DATE and DATETIME null values stay null`(
        typeName: String,
        length: Int,
    ) {
        val converter = registeredConverter(typeName, length, optional = true)

        assertNull(converter.convert(null))
    }

    @ParameterizedTest
    @MethodSource("dateAndDatetimeValueCases")
    fun `DATE and DATETIME values still convert normally`(
        typeName: String,
        length: Int,
        input: Any,
        expected: String,
    ) {
        val converter = registeredConverter(typeName, length, optional = false)

        assertEquals(expected, converter.convert(input))
    }

    companion object {
        @JvmStatic
        fun requiredDateAndDatetimeZeroDateCases(): List<Arguments> =
            listOf(
                Arguments.of("DATE", 0, "1970-01-01"),
                Arguments.of("DATETIME", 0, "1970-01-01T00:00:00.000000"),
                Arguments.of("DATETIME", 6, "1970-01-01T00:00:00.000000"),
            )

        @JvmStatic
        fun nullableDateAndDatetimeZeroDateCases(): List<Arguments> =
            listOf(
                Arguments.of("DATE", 0),
                Arguments.of("DATETIME", 0),
                Arguments.of("DATETIME", 6)
            )

        @JvmStatic
        fun dateAndDatetimeValueCases(): List<Arguments> =
            listOf(
                Arguments.of("DATE", 0, LocalDate.parse("2026-05-13"), "2026-05-13"),
                Arguments.of(
                    "DATETIME",
                    0,
                    LocalDateTime.parse("2026-05-13T12:34:56"),
                    "2026-05-13T12:34:56.000000",
                ),
                Arguments.of(
                    "DATETIME",
                    6,
                    LocalDateTime.parse("2026-05-13T12:34:56.123456"),
                    "2026-05-13T12:34:56.123456",
                ),
            )

        private fun registeredConverter(
            typeName: String,
            length: Int,
            optional: Boolean,
        ): CustomConverter.Converter {
            val column =
                mockk<RelationalColumn>(relaxed = true) {
                    every { this@mockk.typeName() } returns typeName
                    every { this@mockk.length() } returns OptionalInt.of(length)
                    every { isOptional } returns optional
                    every { hasDefaultValue() } returns false
                }
            val converterSlot: CapturingSlot<CustomConverter.Converter> = slot()
            val registration =
                mockk<CustomConverter.ConverterRegistration<SchemaBuilder>> {
                    every { register(any(), capture(converterSlot)) } just Runs
                }

            MySqlSourceCdcTemporalConverter().converterFor(column, registration)

            return converterSlot.captured
        }
    }
}
