/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.check

import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.db.toSnowflakeCompatibleName
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

internal class SnowflakeCheckerTest {

    @Test
    fun testSuccessfulCheck() {
        val snowflakeAirbyteClient: SnowflakeAirbyteClient =
            mockk(relaxed = true) { coEvery { countTable(any()) } returns 1L }

        val testSchema = "test-schema"
        val snowflakeConfiguration: SnowflakeConfiguration = mockk {
            every { schema } returns testSchema
        }

        val checker =
            SnowflakeChecker(
                snowflakeAirbyteClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
            )
        checker.check()

        coVerify(exactly = 1) {
            snowflakeAirbyteClient.createNamespace(testSchema.toSnowflakeCompatibleName())
        }
        coVerify(exactly = 1) { snowflakeAirbyteClient.createTable(any(), any(), any(), any()) }
        coVerify(exactly = 1) { snowflakeAirbyteClient.dropTable(any()) }
    }

    @Test
    fun testUnsuccessfulCheck() {
        val snowflakeAirbyteClient: SnowflakeAirbyteClient =
            mockk(relaxed = true) { coEvery { countTable(any()) } returns 0L }

        val testSchema = "test-schema"
        val snowflakeConfiguration: SnowflakeConfiguration = mockk {
            every { schema } returns testSchema
        }

        val checker =
            SnowflakeChecker(
                snowflakeAirbyteClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
            )

        assertThrows<IllegalArgumentException> { checker.check() }

        coVerify(exactly = 1) {
            snowflakeAirbyteClient.createNamespace(testSchema.toSnowflakeCompatibleName())
        }
        coVerify(exactly = 1) { snowflakeAirbyteClient.createTable(any(), any(), any(), any()) }
        coVerify(exactly = 1) { snowflakeAirbyteClient.dropTable(any()) }
    }
}
