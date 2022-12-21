/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import com.google.common.hash.Hashing;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.generated.DestinationApi;
import io.airbyte.api.client.generated.SourceApi;
import io.airbyte.api.client.model.generated.DestinationIdRequestBody;
import io.airbyte.api.client.model.generated.DestinationRead;
import io.airbyte.api.client.model.generated.DestinationUpdate;
import io.airbyte.api.client.model.generated.SourceIdRequestBody;
import io.airbyte.api.client.model.generated.SourceRead;
import io.airbyte.api.client.model.generated.SourceUpdate;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.Config;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Helper class for workers to persist updates to Source/Destination configs emitted from
 * AirbyteControlMessages.
 *
 * This is in order to support connectors updating configs when running commands, which is specially
 * useful for migrating configuration to a new version or for enabling connectors that require
 * single-use or short-lived OAuth tokens.
 */
public class ConnectorConfigUpdater {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConnectorConfigUpdater.class);

  private final SourceApi sourceApi;
  private final DestinationApi destinationApi;

  public ConnectorConfigUpdater(final SourceApi sourceApi, final DestinationApi destinationApi) {
    this.sourceApi = sourceApi;
    this.destinationApi = destinationApi;
  }

  /**
   * Updates the Source from a sync job ID with the provided Configuration. Secrets and OAuth
   * parameters will be masked when saving.
   */
  public void updateSource(final UUID sourceId, final Config config) {
    final SourceRead source = AirbyteApiClient.retryWithJitter(
        () -> sourceApi.getSource(new SourceIdRequestBody().sourceId(sourceId)),
        "get source");

    final SourceRead updatedSource = AirbyteApiClient.retryWithJitter(
        () -> sourceApi
            .updateSource(new SourceUpdate()
                .sourceId(sourceId)
                .name(source.getName())
                .connectionConfiguration(Jsons.jsonNode(config.getAdditionalProperties()))),
        "update source");

    LOGGER.info("Persisted updated configuration for source {}. New config hash: {}.", sourceId,
        Hashing.sha256().hashString(updatedSource.getConnectionConfiguration().asText(), StandardCharsets.UTF_8));

  }

  /**
   * Updates the Destination from a sync job ID with the provided Configuration. Secrets and OAuth
   * parameters will be masked when saving.
   */
  public void updateDestination(final UUID destinationId, final Config config) {
    final DestinationRead destination = AirbyteApiClient.retryWithJitter(
        () -> destinationApi.getDestination(new DestinationIdRequestBody().destinationId(destinationId)),
        "get destination");

    final DestinationRead updatedDestination = AirbyteApiClient.retryWithJitter(
        () -> destinationApi
            .updateDestination(new DestinationUpdate()
                .destinationId(destinationId)
                .name(destination.getName())
                .connectionConfiguration(Jsons.jsonNode(config.getAdditionalProperties()))),
        "update destination");

    LOGGER.info("Persisted updated configuration for destination {}. New config hash: {}.", destinationId,
        Hashing.sha256().hashString(updatedDestination.getConnectionConfiguration().asText(), StandardCharsets.UTF_8));
  }

}
