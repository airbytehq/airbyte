/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.annotation.Value
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton

/**
 * Micronaut factory for the [ConfiguredAirbyteCatalog] singleton.
 *
 * The value may be defined via two Micronaut properties:
 * - `airbyte.connector.catalog.json` for use by [ConnectorCommandLinePropertySource],
 * - `airbyte.connector.catalog.resource` for use in unit tests.
 */
@Factory
class ConfiguredCatalogFactory {
    @Singleton
    @Requires(missingProperty = "${CONNECTOR_CATALOG_PREFIX}.resource")
    fun make(
        @Value("\${${CONNECTOR_CATALOG_PREFIX}.json}") json: String?,
    ): ConfiguredAirbyteCatalog =
        ValidatedJsonUtils.parseOne(ConfiguredAirbyteCatalog::class.java, json ?: "{}").also {
            for (configuredStream in it.streams) {
                validateConfiguredStream(configuredStream)
            }
        }

    private fun validateConfiguredStream(configuredStream: ConfiguredAirbyteStream) {
        val stream: AirbyteStream = configuredStream.stream
        if (stream.name == null) {
            throw ConfigErrorException("Configured catalog is missing stream name.")
        }
        // TODO: add more validation?
    }

    @Singleton
    @Requires(env = [Environment.TEST])
    @Requires(notEnv = [Environment.CLI])
    @Requires(property = "${CONNECTOR_CATALOG_PREFIX}.resource")
    fun makeFromTestResource(
        @Value("\${${CONNECTOR_CATALOG_PREFIX}.resource}") resource: String,
    ): ConfiguredAirbyteCatalog = make(ResourceUtils.readResource(resource))
}
