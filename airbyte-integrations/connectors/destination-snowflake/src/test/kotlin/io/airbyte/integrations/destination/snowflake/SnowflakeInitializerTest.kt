/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake

import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.micronaut.context.event.StartupEvent
import io.mockk.coVerify
import io.mockk.mockk
import org.junit.jupiter.api.Test

internal class SnowflakeInitializerTest {

    @Test
    fun testOnStartup() {
        val snowflakeAirbyteClient = mockk<SnowflakeAirbyteClient>(relaxed = true)
        val snowflakeInitializer = SnowflakeInitializer(snowflakeAirbyteClient)
        val startupEvent = mockk<StartupEvent>()
        snowflakeInitializer.onStartup(startupEvent)
        coVerify(exactly = 1) { snowflakeAirbyteClient.createFileFormat() }
    }
}
