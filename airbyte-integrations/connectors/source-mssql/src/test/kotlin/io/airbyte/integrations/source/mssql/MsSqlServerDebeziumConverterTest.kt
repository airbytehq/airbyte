/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.debezium.spi.converter.CustomConverter
import io.debezium.spi.converter.RelationalColumn
import java.sql.Timestamp
import java.sql.Types
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import org.apache.kafka.connect.data.Schema
import org.apache.kafka.connect.data.SchemaBuilder
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Test
import org.mockito.ArgumentCaptor
import org.mockito.Mockito.mock
import org.mockito.Mockito.verify
import org.mockito.Mockito.verifyNoInteractions
import org.mockito.Mockito.`when`

class MsSqlServerDebeziumConverterTest {

    private val converter = MsSqlServerDebeziumConverter()

    @Test
    fun `registers string converters for temporal alias JDBC types`() {
        val cases =
            listOf(
                Triple(
                    "Fecha",
                    Types.TIMESTAMP,
                    Timestamp.valueOf(LocalDateTime.of(2026, 10, 17, 0, 0)),
                ),
                Triple("FechaD", Types.DATE, LocalDate.of(2026, 10, 17)),
                Triple("Hora", Types.TIME, LocalTime.of(15, 0, 3, 987654000)),
            )

        for ((typeName, jdbcType, value) in cases) {
            val registration = registration()
            converter.converterFor(column(typeName, jdbcType), registration)

            val schemaCaptor = ArgumentCaptor.forClass(SchemaBuilder::class.java)
            val converterCaptor = ArgumentCaptor.forClass(CustomConverter.Converter::class.java)
            verify(registration).register(schemaCaptor.capture(), converterCaptor.capture())
            assertEquals(Schema.Type.STRING, schemaCaptor.value.type())

            val baseType = when (jdbcType) {
                Types.TIMESTAMP -> "DATETIME"
                Types.DATE -> "DATE"
                Types.TIME -> "TIME"
                else -> error("Unexpected JDBC type: $jdbcType")
            }
            val baseRegistration = registration()
            converter.converterFor(column(baseType, jdbcType), baseRegistration)
            val baseConverterCaptor =
                ArgumentCaptor.forClass(CustomConverter.Converter::class.java)
            verify(baseRegistration).register(
                org.mockito.ArgumentMatchers.any(SchemaBuilder::class.java),
                baseConverterCaptor.capture(),
            )

            assertEquals(baseConverterCaptor.value.convert(value), converterCaptor.value.convert(value))
        }
    }

    @Test
    fun `does not register a converter for an unknown non-temporal alias`() {
        val registration = registration()

        converter.converterFor(column("AliasText", Types.VARCHAR), registration)

        verifyNoInteractions(registration)
    }

    @Test
    fun `continues to register converter for base type names`() {
        val registration = registration()

        converter.converterFor(column("DATETIME", Types.TIMESTAMP), registration)

        val converterCaptor = ArgumentCaptor.forClass(CustomConverter.Converter::class.java)
        verify(registration).register(
            org.mockito.ArgumentMatchers.any(SchemaBuilder::class.java),
            converterCaptor.capture(),
        )
        assertNotNull(converterCaptor.value)
        assertEquals(
            "2026-10-17T00:00:00.000000",
            converterCaptor.value.convert(Timestamp.valueOf(LocalDateTime.of(2026, 10, 17, 0, 0))),
        )
    }

    private fun column(typeName: String, jdbcType: Int): RelationalColumn =
        mock(RelationalColumn::class.java).also {
            `when`(it.typeName()).thenReturn(typeName)
            `when`(it.jdbcType()).thenReturn(jdbcType)
            `when`(it.name()).thenReturn("column")
        }

    @Suppress("UNCHECKED_CAST")
    private fun registration(): CustomConverter.ConverterRegistration<SchemaBuilder> =
        mock(CustomConverter.ConverterRegistration::class.java)
            as CustomConverter.ConverterRegistration<SchemaBuilder>
}
