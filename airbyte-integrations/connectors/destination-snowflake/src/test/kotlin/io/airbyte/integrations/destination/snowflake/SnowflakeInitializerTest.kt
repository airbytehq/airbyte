/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake

import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.micronaut.context.event.StartupEvent
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Test

internal class SnowflakeInitializerTest {

    @Test
    fun testOnStartup() {
        val databaseName = "test-database"
        val schemaName = "test-schema"
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val snowflakeConfiguration =
            mockk<SnowflakeConfiguration> {
                every { database } returns databaseName
                every { schema } returns schemaName
            }
        val snowflakeSqlNameTransformer =
            mockk<SnowflakeSqlNameTransformer> { every { transform(any()) } answers { firstArg() } }
        val snowflakeInitializer =
            SnowflakeInitializer(
                snowflakeAirbyteClient = snowflakeAirbyteClient,
                snowflakeConfiguration = snowflakeConfiguration,
                snowflakeSqlNameTransformer = snowflakeSqlNameTransformer,
            )
        val startupEvent = mockk<StartupEvent>()
        snowflakeInitializer.onStartup(startupEvent)
        coVerify(exactly = 1) { snowflakeAirbyteClient.execute("USE DATABASE \"$databaseName\";") }
        coVerify(exactly = 1) { snowflakeAirbyteClient.execute("USE SCHEMA \"$schemaName\";") }
        coVerify(exactly = 1) { snowflakeAirbyteClient.createFileFormat() }
    }
}
