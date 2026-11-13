/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.debezium.spi.converter.CustomConverter
import io.debezium.spi.converter.RelationalColumn
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.slot
import java.sql.Timestamp
import java.sql.Types
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import org.apache.kafka.connect.data.SchemaBuilder
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

class MsSqlServerDebeziumConverterTest {

    @ParameterizedTest
    @MethodSource("temporalAliases")
    fun temporalAliasUsesStringConverterOfBaseType(jdbcType: Int, value: Any, expected: String) {
        val converter = registeredConverter("alias_type", jdbcType)
        Assertions.assertEquals(expected, converter?.convert(value))
    }

    @Test
    fun nonTemporalAliasRegistersNoConverter() {
        Assertions.assertNull(registeredConverter("alias_type", Types.VARCHAR))
    }

    private fun registeredConverter(
        typeName: String,
        jdbcType: Int,
    ): CustomConverter.Converter? {
        val column =
            mockk<RelationalColumn> {
                every { typeName() } returns typeName
                every { jdbcType() } returns jdbcType
                every { name() } returns "col"
            }
        val converter = slot<CustomConverter.Converter>()
        val registration =
            mockk<CustomConverter.ConverterRegistration<SchemaBuilder>> {
                every { register(any(), capture(converter)) } just runs
            }
        MsSqlServerDebeziumConverter().converterFor(column, registration)
        return if (converter.isCaptured) converter.captured else null
    }

    companion object {
        @JvmStatic
        fun temporalAliases(): List<Arguments> =
            listOf(
                Arguments.of(
                    Types.TIMESTAMP,
                    Timestamp.valueOf(LocalDateTime.of(2026, 10, 17, 0, 0)),
                    "2026-10-17T00:00:00.000000",
                ),
                Arguments.of(Types.DATE, LocalDate.of(2026, 10, 17), "2026-10-17"),
                Arguments.of(Types.TIME, LocalTime.of(15, 0, 3, 987654000), "15:00:03.987654"),
            )
    }
}
