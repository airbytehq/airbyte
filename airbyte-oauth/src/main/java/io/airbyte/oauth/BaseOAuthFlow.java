/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

/**
 * Abstract Class implementing common base methods for managing: - oAuth config (instance-wide)
 * parameters - oAuth specifications
 */
public abstract class BaseOAuthFlow implements OAuthFlowImplementation {

  private final ConfigRepository configRepository;

  public BaseOAuthFlow(final ConfigRepository configRepository) {
    this.configRepository = configRepository;
  }

  protected JsonNode getSourceOAuthParamConfig(final UUID workspaceId, final UUID sourceDefinitionId) throws IOException, ConfigNotFoundException {
    try {
      final Optional<SourceOAuthParameter> param = MoreOAuthParameters.getSourceOAuthParameter(
          configRepository.listSourceOAuthParam().stream(), workspaceId, sourceDefinitionId);
      if (param.isPresent()) {
        return param.get().getConfiguration();
      } else {
        throw new ConfigNotFoundException(ConfigSchema.SOURCE_OAUTH_PARAM, "Undefined OAuth Parameter.");
      }
    } catch (final JsonValidationException e) {
      throw new IOException("Failed to load OAuth Parameters", e);
    }
  }

  protected JsonNode getDestinationOAuthParamConfig(final UUID workspaceId, final UUID destinationDefinitionId)
      throws IOException, ConfigNotFoundException {
    try {
      final Optional<DestinationOAuthParameter> param = MoreOAuthParameters.getDestinationOAuthParameter(
          configRepository.listDestinationOAuthParam().stream(), workspaceId, destinationDefinitionId);
      if (param.isPresent()) {
        return param.get().getConfiguration();
      } else {
        throw new ConfigNotFoundException(ConfigSchema.DESTINATION_OAUTH_PARAM, "Undefined OAuth Parameter.");
      }
    } catch (final JsonValidationException e) {
      throw new IOException("Failed to load OAuth Parameters", e);
    }
  }

  /**
   * Throws an exception if the client ID cannot be extracted. Subclasses should override this to
   * parse the config differently.
   *
   * @return The configured Client ID used for this oauth flow
   */
  protected String getClientIdUnsafe(final JsonNode oauthConfig) {
    final List<String> path = new ArrayList<>(getDefaultOAuthOutputPath());
    path.add("client_id");
    JsonNode result = oauthConfig;
    for (final String node : path) {
      if (result.get(node) != null) {
        result = result.get(node);
      } else {
        throw new IllegalArgumentException(String.format("Undefined parameter '%s' necessary for the OAuth Flow.", String.join(".", path)));
      }
    }
    return result.asText();
  }

  /**
   * Throws an exception if the client secret cannot be extracted. Subclasses should override this to
   * parse the config differently.
   *
   * @return The configured client secret for this OAuthFlow
   */
  protected String getClientSecretUnsafe(final JsonNode oauthConfig) {
    final List<String> path = new ArrayList<>(getDefaultOAuthOutputPath());
    path.add("client_secret");
    JsonNode result = oauthConfig;
    for (final String node : path) {
      if (result.get(node) != null) {
        result = result.get(node);
      } else {
        throw new IllegalArgumentException(String.format("Undefined parameter '%s' necessary for the OAuth Flow.", String.join(".", path)));
      }
    }
    return result.asText();
  }

  /**
   * completeOAuth calls should output a flat map of fields produced by the oauth flow to be forwarded
   * back to the connector config. This function is in charge of formatting such flat map of fields
   * into nested Map accordingly to follow the expected @param outputPath.
   *
   */
  protected Map<String, Object> formatOAuthOutput(final JsonNode oAuthParamConfig,
                                                  final Map<String, Object> oauthOutput,
                                                  final List<String> outputPath) {
    Map<String, Object> result = oauthOutput;
    for (final String node : outputPath) {
      result = Map.of(node, result);
    }
    // TODO chris to implement injection of oAuthParamConfig in outputs
    return result;
  }

  /**
   * This function should be redefined in each OAuthFlow implementation to isolate such "hardcoded"
   * values.
   */
  protected abstract List<String> getDefaultOAuthOutputPath();

}
