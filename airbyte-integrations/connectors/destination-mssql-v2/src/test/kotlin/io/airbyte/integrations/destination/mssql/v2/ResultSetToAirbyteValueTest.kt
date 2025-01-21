/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.integrations.destination.mssql.v2.convert.ResultSetToAirbyteValue.Companion.toTimeWithTimezone
import io.airbyte.integrations.destination.mssql.v2.convert.ResultSetToAirbyteValue.Companion.toTimeWithoutTimezone
import io.airbyte.integrations.destination.mssql.v2.convert.ResultSetToAirbyteValue.Companion.toTimestampWithTimezone
import io.airbyte.integrations.destination.mssql.v2.convert.ResultSetToAirbyteValue.Companion.toTimestampWithoutTimezone
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class ResultSetToAirbyteValueTest {
    @Test
    fun `test TimeWithTimezone read`() {
        val actual = "1970-01-01 12:34:56.0000000 +00:00".toTimeWithTimezone()
        val expected = TimeWithTimezoneValue("12:34:56Z")
        assertEquals(expected, actual)
    }

    @Test
    fun `test TimeWithoutTimezone read`() {
        val actual = "12:34:56.0000000".toTimeWithoutTimezone()
        val expected = TimeWithoutTimezoneValue("12:34:56")
        assertEquals(expected, actual)
    }

    @Test
    fun `test TimestampWithTimezone read`() {
        val actual = "2023-01-23 12:34:56.0000000 +00:00".toTimestampWithTimezone()
        val expected = TimestampWithTimezoneValue("2023-01-23T12:34:56Z")
        assertEquals(expected, actual)
    }

    @Test
    fun `test TimestampWithoutTimezone read`() {
        val actual = "2023-01-23 12:34:56.0".toTimestampWithoutTimezone()
        val expected = TimestampWithoutTimezoneValue("2023-01-23T12:34:56")
        assertEquals(expected, actual)
    }
}
