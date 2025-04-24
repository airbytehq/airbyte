/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.fixtures.legacy

import com.google.common.hash.Hashing
import io.airbyte.api.client.AirbyteApiClient
import io.airbyte.api.client.generated.DestinationApi
import io.airbyte.api.client.generated.SourceApi
import io.airbyte.api.client.model.generated.DestinationIdRequestBody
import io.airbyte.api.client.model.generated.DestinationUpdate
import io.airbyte.api.client.model.generated.SourceIdRequestBody
import io.airbyte.api.client.model.generated.SourceUpdate
import io.airbyte.protocol.models.Config
import io.airbyte.protocol.models.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.charset.StandardCharsets
import java.util.*

private val LOGGER = KotlinLogging.logger {}
/**
 * Helper class for workers to persist updates to Source/Destination configs emitted from
 * AirbyteControlMessages.
 *
 * This is in order to support connectors updating configs when running commands, which is specially
 * useful for migrating configuration to a new version or for enabling connectors that require
 * single-use or short-lived OAuth tokens.
 */
class ConnectorConfigUpdater(
    private val sourceApi: SourceApi,
    private val destinationApi: DestinationApi
) {
    /**
     * Updates the Source from a sync job ID with the provided Configuration. Secrets and OAuth
     * parameters will be masked when saving.
     */
    fun updateSource(sourceId: UUID?, config: Config) {
        val source =
            AirbyteApiClient.retryWithJitter(
                { sourceApi.getSource(SourceIdRequestBody().sourceId(sourceId)) },
                "get source"
            )!!

        val updatedSource =
            AirbyteApiClient.retryWithJitter(
                {
                    sourceApi.updateSource(
                        SourceUpdate()
                            .sourceId(sourceId)
                            .name(source.name)
                            .connectionConfiguration(Jsons.jsonNode(config.additionalProperties))
                    )
                },
                "update source"
            )!!

        LOGGER.info(
            "Persisted updated configuration for source {}. New config hash: {}.",
            sourceId,
            Hashing.sha256()
                .hashString(updatedSource.connectionConfiguration.asText(), StandardCharsets.UTF_8)
        )
    }

    /**
     * Updates the Destination from a sync job ID with the provided Configuration. Secrets and OAuth
     * parameters will be masked when saving.
     */
    fun updateDestination(destinationId: UUID?, config: Config) {
        val destination =
            AirbyteApiClient.retryWithJitter(
                {
                    destinationApi.getDestination(
                        DestinationIdRequestBody().destinationId(destinationId)
                    )
                },
                "get destination"
            )!!

        val updatedDestination =
            AirbyteApiClient.retryWithJitter(
                {
                    destinationApi.updateDestination(
                        DestinationUpdate()
                            .destinationId(destinationId)
                            .name(destination.name)
                            .connectionConfiguration(Jsons.jsonNode(config.additionalProperties))
                    )
                },
                "update destination"
            )!!

        LOGGER.info(
            "Persisted updated configuration for destination {}. New config hash: {}.",
            destinationId,
            Hashing.sha256()
                .hashString(
                    updatedDestination.connectionConfiguration.asText(),
                    StandardCharsets.UTF_8
                )
        )
    }

    companion object {}
}
