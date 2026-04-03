/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.read.cdc.ConverterFactory
import io.debezium.spi.converter.RelationalColumn
import io.mockk.every
import io.mockk.mockk
import java.sql.Timestamp
import java.time.Instant
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class MySqlSourceCdcTemporalConverterTest {
    @Test
    fun `timestamp handler converts snapshot mode sql timestamp`() {
        val converter =
            ConverterFactory(MySqlSourceCdcTemporalConverter::class.java).build(
                relationalColumn("TIMESTAMP"),
                MySqlSourceCdcTemporalConverter.TimestampHandler.partialConverters
            )

        val result = converter.convert(Timestamp.from(Instant.parse("2026-03-17T11:05:01Z")))

        assertEquals("2026-03-17T11:05:01.000000Z", result)
    }

    @Test
    fun `timestamp handler converts instant values`() {
        val converter =
            ConverterFactory(MySqlSourceCdcTemporalConverter::class.java).build(
                relationalColumn("TIMESTAMP"),
                MySqlSourceCdcTemporalConverter.TimestampHandler.partialConverters
            )

        val result = converter.convert(Instant.parse("2026-03-17T11:05:01.123456Z"))

        assertEquals("2026-03-17T11:05:01.123456Z", result)
    }

    private fun relationalColumn(typeName: String): RelationalColumn {
        val column = mockk<RelationalColumn>()
        every { column.typeName() } returns typeName
        every { column.isOptional } returns false
        every { column.hasDefaultValue() } returns false
        every { column.dataCollection() } returns "airbyte_test.orders"
        every { column.name() } returns "updated_at"
        return column
    }
}
