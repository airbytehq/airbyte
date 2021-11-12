/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_factory;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.MoreOAuthParameters;
import io.airbyte.scheduler.persistence.job_tracker.TrackingMetadata;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.UUID;

public class OAuthConfigSupplier {

  final private ConfigRepository configRepository;
  private final boolean maskSecrets;
  private final TrackingClient trackingClient;

  public OAuthConfigSupplier(final ConfigRepository configRepository, final boolean maskSecrets, final TrackingClient trackingClient) {
    this.configRepository = configRepository;
    this.maskSecrets = maskSecrets;
    this.trackingClient = trackingClient;
  }

  public JsonNode injectSourceOAuthParameters(final UUID sourceDefinitionId, final UUID workspaceId, final JsonNode sourceConnectorConfig)
      throws IOException {
    try {
      final ImmutableMap<String, Object> metadata = generateSourceMetadata(sourceDefinitionId);
      // TODO there will be cases where we shouldn't write oauth params. See
      // https://github.com/airbytehq/airbyte/issues/5989
      MoreOAuthParameters.getSourceOAuthParameter(configRepository.listSourceOAuthParam().stream(), workspaceId, sourceDefinitionId)
          .ifPresent(
              sourceOAuthParameter -> {
                if (maskSecrets) {
                  // when maskSecrets = true, no real oauth injections is happening, only masked values
                  Jsons.mergeJsons(
                      (ObjectNode) sourceConnectorConfig,
                      (ObjectNode) sourceOAuthParameter.getConfiguration(),
                      Jsons.getSecretMask());
                } else {
                  Jsons.mergeJsons((ObjectNode) sourceConnectorConfig, (ObjectNode) sourceOAuthParameter.getConfiguration());
                  Exceptions.swallow(() -> trackingClient.track(workspaceId, "OAuth Injection - Backend", metadata));
                }
              });
      return sourceConnectorConfig;
    } catch (final JsonValidationException | ConfigNotFoundException e) {
      throw new IOException(e);
    }
  }

  public JsonNode injectDestinationOAuthParameters(final UUID destinationDefinitionId,
                                                   final UUID workspaceId,
                                                   final JsonNode destinationConnectorConfig)
      throws IOException {
    try {
      final ImmutableMap<String, Object> metadata = generateDestinationMetadata(destinationDefinitionId);
      MoreOAuthParameters.getDestinationOAuthParameter(configRepository.listDestinationOAuthParam().stream(), workspaceId, destinationDefinitionId)
          .ifPresent(destinationOAuthParameter -> {
            if (maskSecrets) {
              // when maskSecrets = true, no real oauth injections is happening, only masked values
              Jsons.mergeJsons(
                  (ObjectNode) destinationConnectorConfig,
                  (ObjectNode) destinationOAuthParameter.getConfiguration(),
                  Jsons.getSecretMask());
            } else {
              Jsons.mergeJsons((ObjectNode) destinationConnectorConfig, (ObjectNode) destinationOAuthParameter.getConfiguration());
              Exceptions.swallow(() -> trackingClient.track(workspaceId, "OAuth Injection - Backend", metadata));
            }
          });
      return destinationConnectorConfig;
    } catch (final JsonValidationException | ConfigNotFoundException e) {
      throw new IOException(e);
    }
  }

  private ImmutableMap<String, Object> generateSourceMetadata(final UUID sourceDefinitionId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardSourceDefinition sourceDefinition = configRepository.getStandardSourceDefinition(sourceDefinitionId);
    return TrackingMetadata.generateSourceDefinitionMetadata(sourceDefinition);
  }

  private ImmutableMap<String, Object> generateDestinationMetadata(final UUID destinationDefinitionId)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardDestinationDefinition destinationDefinition = configRepository.getStandardDestinationDefinition(destinationDefinitionId);
    return TrackingMetadata.generateDestinationDefinitionMetadata(destinationDefinition);
  }

}
