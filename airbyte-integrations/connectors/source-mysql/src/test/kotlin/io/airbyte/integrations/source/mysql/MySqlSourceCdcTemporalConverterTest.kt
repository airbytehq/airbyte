/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.read.cdc.Converted
import io.debezium.spi.converter.RelationalColumn
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class MySqlSourceCdcTemporalConverterTest {

    @Test
    fun `DATETIME zero date in NOT NULL column is converted to epoch`() {
        val handler = MySqlSourceCdcTemporalConverter.DatetimeMicrosHandler()

        handler.matches(column("DATETIME", isOptional = false, length = 6))

        assertEquals(
            Converted("1970-01-01T00:00:00.000000"),
            handler.partialConverters.first().maybeConvert(null),
        )
    }

    @Test
    fun `DATETIME zero date in nullable column remains null`() {
        val handler = MySqlSourceCdcTemporalConverter.DatetimeMillisHandler()

        handler.matches(column("DATETIME", isOptional = true, length = 3))

        assertEquals(Converted(null), handler.partialConverters.first().maybeConvert(null))
    }

    @Test
    fun `DATE zero date in NOT NULL column is converted to epoch date`() {
        val handler = MySqlSourceCdcTemporalConverter.DateHandler()

        handler.matches(column("DATE", isOptional = false))

        assertEquals(Converted("1970-01-01"), handler.partialConverters.first().maybeConvert(null))
    }

    private fun column(typeName: String, isOptional: Boolean, length: Int = 0): RelationalColumn =
        mockk {
            every { this@mockk.typeName() } returns typeName
            every { this@mockk.isOptional } returns isOptional
            every { this@mockk.length() } returns java.util.OptionalInt.of(length)
        }
}
