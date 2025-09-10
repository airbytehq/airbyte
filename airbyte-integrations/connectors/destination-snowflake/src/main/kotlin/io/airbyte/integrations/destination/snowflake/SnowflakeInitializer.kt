/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake

import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.micronaut.context.event.StartupEvent
import io.micronaut.runtime.event.annotation.EventListener
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking

/**
 * Singleton that performs any once-per-run startup initialization required to interact
 * with Snowflake.
 */
@Singleton
class SnowflakeInitializer(
    private val snowflakeAirbyteClient: SnowflakeAirbyteClient,
) {

    @EventListener
    internal fun onStartup(@Suppress("unused") event: StartupEvent) {
        runBlocking { snowflakeAirbyteClient.createFileFormat() }
    }
}
