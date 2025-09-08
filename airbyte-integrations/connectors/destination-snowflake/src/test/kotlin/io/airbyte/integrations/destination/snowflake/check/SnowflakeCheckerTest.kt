/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.check

import io.airbyte.integrations.destination.snowflake.SnowflakeSqlNameTransformer
import io.airbyte.integrations.destination.snowflake.client.AirbyteSnowflakeClient
import io.airbyte.integrations.destination.snowflake.client.SnowflakeSqlGenerator
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
        val airbyteSnowflakeClient: AirbyteSnowflakeClient =
            mockk(relaxed = true) { coEvery { countTable(any()) } returns 1L }
        val snowflakeSqlNameTransformer: SnowflakeSqlNameTransformer = mockk {
            every { transform(any()) } answers { firstArg() }
        }
        val snowflakeSqlGenerator: SnowflakeSqlGenerator = mockk()

        val testSchema = "test-schema"
        val snowflakeConfiguration: SnowflakeConfiguration = mockk {
            every { schema } returns testSchema
        }

        val checker =
            SnowflakeChecker(
                airbyteSnowflakeClient = airbyteSnowflakeClient,
                snowflakeSqlNameTransformer = snowflakeSqlNameTransformer,
                snowflakeSqlGenerator = snowflakeSqlGenerator,
            )
        checker.check(snowflakeConfiguration)

        coVerify(exactly = 1) { airbyteSnowflakeClient.createNamespace(testSchema) }
        coVerify(exactly = 1) { airbyteSnowflakeClient.createTable(any(), any(), any(), any()) }
        coVerify(exactly = 1) { airbyteSnowflakeClient.dropTable(any()) }
    }

    @Test
    fun testUnsuccessfulCheck() {
        val airbyteSnowflakeClient: AirbyteSnowflakeClient =
            mockk(relaxed = true) { coEvery { countTable(any()) } returns 0L }
        val snowflakeSqlNameTransformer: SnowflakeSqlNameTransformer = mockk {
            every { transform(any()) } answers { firstArg() }
        }
        val snowflakeSqlGenerator: SnowflakeSqlGenerator = mockk()

        val testSchema = "test-schema"
        val snowflakeConfiguration: SnowflakeConfiguration = mockk {
            every { schema } returns testSchema
        }

        val checker =
            SnowflakeChecker(
                airbyteSnowflakeClient = airbyteSnowflakeClient,
                snowflakeSqlNameTransformer = snowflakeSqlNameTransformer,
                snowflakeSqlGenerator = snowflakeSqlGenerator,
            )

        assertThrows<IllegalArgumentException> { checker.check(snowflakeConfiguration) }

        coVerify(exactly = 1) { airbyteSnowflakeClient.createNamespace(testSchema) }
        coVerify(exactly = 1) { airbyteSnowflakeClient.createTable(any(), any(), any(), any()) }
        coVerify(exactly = 1) { airbyteSnowflakeClient.dropTable(any()) }
    }
}
