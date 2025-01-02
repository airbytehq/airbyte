package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.load.data.TimeValue
import io.airbyte.cdk.load.data.TimestampValue
import io.airbyte.integrations.destination.mssql.v2.MSSQLQueryBuilder.Companion.toTimeWithTimezone
import io.airbyte.integrations.destination.mssql.v2.MSSQLQueryBuilder.Companion.toTimeWithoutTimezone
import io.airbyte.integrations.destination.mssql.v2.MSSQLQueryBuilder.Companion.toTimestampWithTimezone
import io.airbyte.integrations.destination.mssql.v2.MSSQLQueryBuilder.Companion.toTimestampWithoutTimezone
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class MSSQLQueryBuilderTest {
    @Test
    fun `test TimeWithTimezone read`() {
        val actual = "1970-01-01 12:34:56.0000000 +00:00".toTimeWithTimezone()
        val expected = TimeValue("12:34:56Z")
        assertEquals(expected, actual)
    }

    @Test
    fun `test TimeWithoutTimezone read`() {
        val actual = "12:34:56.0000000".toTimeWithoutTimezone()
        val expected = TimeValue("12:34:56")
        assertEquals(expected, actual)
    }

    @Test
    fun `test TimestampWithTimezone read`() {
        val actual = "2023-01-23 12:34:56.0000000 +00:00".toTimestampWithTimezone()
        val expected = TimestampValue("2023-01-23T12:34:56Z")
        assertEquals(expected, actual)
    }

    @Test
    fun `test TimestampWithoutTimezone read`() {
        val actual = "2023-01-23 12:34:56.0".toTimestampWithoutTimezone()
        val expected = TimestampValue("2023-01-23T12:34:56")
        assertEquals(expected, actual)
    }

}
