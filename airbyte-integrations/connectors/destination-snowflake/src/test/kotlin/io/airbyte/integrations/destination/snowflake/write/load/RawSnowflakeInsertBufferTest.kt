/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.mockk.mockk
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.fail
import org.junit.jupiter.api.Test

internal class RawSnowflakeInsertBufferTest {

    @Test
    fun testAccumulate() {
        val tableName = mockk<TableName>()
        val column = "columnName"
        val nullColumn = "nullColumnName"
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record = mapOf(column to AirbyteValue.from("test-value"), nullColumn to NullValue)
        val buffer =
            RawSnowflakeInsertBuffer(
                tableName = tableName,
                snowflakeClient = snowflakeAirbyteClient,
            )

        buffer.accumulate(record)

        assertEquals(1, buffer.recordQueue.size)
        assertEquals(StringValue("test-value"), buffer.recordQueue.poll()[column])
    }

    @Test
    fun testFlush() {
        val tableName = mockk<TableName>()
        val column = "columnName"
        val nullColumn = "nullColumnName"
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val record = mapOf(column to AirbyteValue.from("test-value"), nullColumn to NullValue)
        val buffer =
            RawSnowflakeInsertBuffer(
                tableName = tableName,
                snowflakeClient = snowflakeAirbyteClient,
            )

        runBlocking {
            buffer.accumulate(record)
            buffer.flush()
        }

        fail<String>("TODO: implement")
    }
}
