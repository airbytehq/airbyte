/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake

import io.airbyte.cdk.Operation
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.micronaut.context.annotation.Requires
import io.micronaut.context.event.StartupEvent
import io.micronaut.runtime.event.annotation.EventListener
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking

/**
 * Singleton that performs any once-per-run startup initialization required to interact with
 * Snowflake.
 */
@Singleton
@Requires(property = Operation.PROPERTY, notEquals = "spec")
class SnowflakeInitializer(
    private val snowflakeAirbyteClient: SnowflakeAirbyteClient,
) {

    @EventListener
    internal fun onStartup(@Suppress("UNUSED_PARAMETER") event: StartupEvent) {
        runBlocking { snowflakeAirbyteClient.createFileFormat() }
    }
}
