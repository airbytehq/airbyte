/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import io.debezium.spi.converter.RelationalColumn
import java.sql.Timestamp
import java.time.Duration
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.mockito.Mockito

internal class DebeziumConverterUtilsTest {
    @Test
    fun convertDefaultValueTest() {
        val relationalColumn = Mockito.mock(RelationalColumn::class.java)

        Mockito.`when`(relationalColumn.isOptional).thenReturn(true)
        var actualColumnDefaultValue = DebeziumConverterUtils.convertDefaultValue(relationalColumn)
        Assertions.assertNull(
            actualColumnDefaultValue,
            "Default value for optional relational column should be null"
        )

        Mockito.`when`(relationalColumn.isOptional).thenReturn(false)
        Mockito.`when`(relationalColumn.hasDefaultValue()).thenReturn(false)
        actualColumnDefaultValue = DebeziumConverterUtils.convertDefaultValue(relationalColumn)
        Assertions.assertNull(actualColumnDefaultValue)

        Mockito.`when`(relationalColumn.isOptional).thenReturn(false)
        Mockito.`when`(relationalColumn.hasDefaultValue()).thenReturn(true)
        val expectedColumnDefaultValue = "default value"
        Mockito.`when`(relationalColumn.defaultValue()).thenReturn(expectedColumnDefaultValue)
        actualColumnDefaultValue = DebeziumConverterUtils.convertDefaultValue(relationalColumn)
        Assertions.assertEquals(actualColumnDefaultValue, expectedColumnDefaultValue)
    }

    @Test
    fun convertLocalDate() {
        val localDate = LocalDate.of(2021, 1, 1)

        val actual = DebeziumConverterUtils.convertDate(localDate)
        Assertions.assertEquals("2021-01-01T00:00:00Z", actual)
    }

    @Test
    fun convertTLocalTime() {
        val localTime = LocalTime.of(8, 1, 1)
        val actual = DebeziumConverterUtils.convertDate(localTime)
        Assertions.assertEquals("08:01:01", actual)
    }

    @Test
    fun convertLocalDateTime() {
        val localDateTime = LocalDateTime.of(2021, 1, 1, 8, 1, 1)

        val actual = DebeziumConverterUtils.convertDate(localDateTime)
        Assertions.assertEquals("2021-01-01T08:01:01Z", actual)
    }

    @Test
    @Disabled
    fun convertDuration() {
        val duration = Duration.ofHours(100000)

        val actual = DebeziumConverterUtils.convertDate(duration)
        Assertions.assertEquals("1981-05-29T20:00:00Z", actual)
    }

    @Test
    fun convertTimestamp() {
        val localDateTime = LocalDateTime.of(2021, 1, 1, 8, 1, 1)
        val timestamp = Timestamp.valueOf(localDateTime)

        val actual = DebeziumConverterUtils.convertDate(timestamp)
        Assertions.assertEquals("2021-01-01T08:01:01.000000Z", actual)
    }

    @Test
    @Disabled
    fun convertNumber() {
        val number: Number = 100000

        val actual = DebeziumConverterUtils.convertDate(number)
        Assertions.assertEquals("1970-01-01T03:01:40Z", actual)
    }

    @Test
    fun convertStringDateFormat() {
        val stringValue = "2021-01-01T00:00:00Z"

        val actual = DebeziumConverterUtils.convertDate(stringValue)
        Assertions.assertEquals("2021-01-01T00:00:00Z", actual)
    }
}
