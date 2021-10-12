/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_factory;

import static com.fasterxml.jackson.databind.node.JsonNodeType.OBJECT;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Strings;
import com.google.common.collect.ImmutableMap;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.MoreOAuthParameters;
import io.airbyte.scheduler.persistence.job_tracker.TrackingMetadata;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OAuthConfigSupplier {

  private static final Logger LOGGER = LoggerFactory.getLogger(OAuthConfigSupplier.class);

  public static final String SECRET_MASK = "******";
  final private ConfigRepository configRepository;
  private final boolean maskSecrets;
  private final TrackingClient trackingClient;

  public OAuthConfigSupplier(ConfigRepository configRepository, boolean maskSecrets, TrackingClient trackingClient) {
    this.configRepository = configRepository;
    this.maskSecrets = maskSecrets;
    this.trackingClient = trackingClient;
  }

  public JsonNode injectSourceOAuthParameters(UUID sourceDefinitionId, UUID workspaceId, JsonNode sourceConnectorConfig)
      throws IOException {
    try {
      final ImmutableMap<String, Object> metadata = generateSourceMetadata(sourceDefinitionId);
      // TODO there will be cases where we shouldn't write oauth params. See
      // https://github.com/airbytehq/airbyte/issues/5989
      MoreOAuthParameters.getSourceOAuthParameter(configRepository.listSourceOAuthParam().stream(), workspaceId, sourceDefinitionId)
          .ifPresent(
              sourceOAuthParameter -> {
                injectJsonNode((ObjectNode) sourceConnectorConfig, (ObjectNode) sourceOAuthParameter.getConfiguration());
                if (!maskSecrets) {
                  // when maskSecrets = true, no real oauth injections is happening
                  trackingClient.track(workspaceId, "OAuth Injection - Backend", metadata);
                }
              });
      return sourceConnectorConfig;
    } catch (JsonValidationException | ConfigNotFoundException e) {
      throw new IOException(e);
    }
  }

  public JsonNode injectDestinationOAuthParameters(UUID destinationDefinitionId, UUID workspaceId, JsonNode destinationConnectorConfig)
      throws IOException {
    try {
      final ImmutableMap<String, Object> metadata = generateDestinationMetadata(destinationDefinitionId);
      MoreOAuthParameters.getDestinationOAuthParameter(configRepository.listDestinationOAuthParam().stream(), workspaceId, destinationDefinitionId)
          .ifPresent(destinationOAuthParameter -> {
            injectJsonNode((ObjectNode) destinationConnectorConfig,
                (ObjectNode) destinationOAuthParameter.getConfiguration());
            if (!maskSecrets) {
              // when maskSecrets = true, no real oauth injections is happening
              trackingClient.track(workspaceId, "OAuth Injection - Backend", metadata);
            }
          });
      return destinationConnectorConfig;
    } catch (JsonValidationException | ConfigNotFoundException e) {
      throw new IOException(e);
    }
  }

  @VisibleForTesting
  void injectJsonNode(ObjectNode mainConfig, ObjectNode fromConfig) {
    // TODO this method might make sense to have as a general utility in Jsons
    for (String key : Jsons.keys(fromConfig)) {
      if (fromConfig.get(key).getNodeType() == OBJECT) {
        // nested objects are merged rather than overwrite the contents of the equivalent object in config
        if (mainConfig.get(key) == null) {
          injectJsonNode(mainConfig.putObject(key), (ObjectNode) fromConfig.get(key));
        } else if (mainConfig.get(key).getNodeType() == OBJECT) {
          injectJsonNode((ObjectNode) mainConfig.get(key), (ObjectNode) fromConfig.get(key));
        } else {
          throw new IllegalStateException("Can't merge an object node into a non-object node!");
        }
      } else {
        if (maskSecrets) {
          // TODO secrets should be masked with the correct type
          // https://github.com/airbytehq/airbyte/issues/5990
          // In the short-term this is not world-ending as all secret fields are currently strings
          LOGGER.debug(String.format("Masking instance wide parameter %s in config", key));
          mainConfig.set(key, Jsons.jsonNode(SECRET_MASK));
        } else {
          if (!mainConfig.has(key) || isSecretMask(mainConfig.get(key).asText())) {
            LOGGER.debug(String.format("injecting instance wide parameter %s into config", key));
            mainConfig.set(key, fromConfig.get(key));
          }
        }
      }

    }
  }

  private static boolean isSecretMask(String input) {
    return Strings.isNullOrEmpty(input.replaceAll("\\*", ""));
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
