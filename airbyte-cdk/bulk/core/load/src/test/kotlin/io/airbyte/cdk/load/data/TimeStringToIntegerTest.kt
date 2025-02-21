/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class TimeStringToIntegerTest {

    @Test
    fun testMapDate() {
        val mapper = TimeStringToInteger()
        Assertions.assertEquals(
            IntegerValue(18628),
            mapper.mapDate(DateValue("2021-01-01"), AirbyteValueIdentityMapper.Context()).first,
        )
    }

    @Test
    fun testMapTimestampWithTimezone() {
        val mapper = TimeStringToInteger()
        Assertions.assertEquals(
            IntegerValue(1609462861000000),
            mapper
                .mapTimestampWithTimezone(
                    TimestampWithTimezoneValue("2021-01-01T01:01:01Z"),
                    AirbyteValueIdentityMapper.Context()
                )
                .first,
        )
    }

    @Test
    fun testMapTimestampWithoutTimezone() {
        val mapper = TimeStringToInteger()
        Assertions.assertEquals(
            IntegerValue(1537012800000000),
            mapper
                .mapTimestampWithoutTimezone(
                    TimestampWithoutTimezoneValue("2018-09-15T12:00:00"),
                    AirbyteValueIdentityMapper.Context()
                )
                .first,
        )
    }

    @Test
    fun testTimeWithTimezone() {
        val mapper = TimeStringToInteger()
        Assertions.assertEquals(
            IntegerValue(39600000000),
            mapper
                .mapTimeWithTimezone(
                    TimeWithTimezoneValue("12:00:00.000000+01:00"),
                    AirbyteValueIdentityMapper.Context()
                )
                .first,
        )
    }

    @Test
    fun testTimeWithoutTimezone() {
        val mapper = TimeStringToInteger()
        Assertions.assertEquals(
            IntegerValue(3661000000),
            mapper
                .mapTimeWithoutTimezone(
                    TimeWithoutTimezoneValue("01:01:01"),
                    AirbyteValueIdentityMapper.Context()
                )
                .first,
        )
    }
}
