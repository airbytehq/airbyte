/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake

import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.event.StartupEvent
import io.micronaut.runtime.event.annotation.EventListener
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking

private val logger = KotlinLogging.logger {}

/**
 * Singleton that performs any once-per-run startup initialization required to interact with
 * Snowflake.
 */
@Singleton
class SnowflakeInitializer(
    private val snowflakeAirbyteClient: SnowflakeAirbyteClient,
    private val snowflakeConfiguration: SnowflakeConfiguration,
    private val snowflakeSqlNameTransformer: SnowflakeSqlNameTransformer,
) {

    @EventListener
    internal fun onStartup(@Suppress("UNUSED_PARAMETER") event: StartupEvent) {
        runBlocking {
            logger.info { "Initializing Snowflake destination..." }
            snowflakeAirbyteClient.execute("USE DATABASE \"${snowflakeConfiguration.database}\";")
            snowflakeAirbyteClient.execute(
                "USE SCHEMA \"${snowflakeSqlNameTransformer.transform(snowflakeConfiguration.schema)}\";"
            )
            snowflakeAirbyteClient.createFileFormat()
            logger.info {
                "Snowflake destination initialized for database ${snowflakeConfiguration.database} and schema ${snowflakeConfiguration.schema}."
            }
        }
    }
}
