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
import java.util.Optional;
import java.util.UUID;

/*
 * Class with methods for getting oAuth config parameters for source and destination oAuth flow from
 * config repository.
 */
public abstract class BaseOAuthConfig implements OAuthFlowImplementation {

  private final ConfigRepository configRepository;

  public BaseOAuthConfig(final ConfigRepository configRepository) {
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
    if (oauthConfig.get("client_id") != null) {
      return oauthConfig.get("client_id").asText();
    } else {
      throw new IllegalArgumentException("Undefined parameter 'client_id' necessary for the OAuth Flow.");
    }
  }

  /**
   * Throws an exception if the client secret cannot be extracted. Subclasses should override this to
   * parse the config differently.
   *
   * @return The configured client secret for this OAuthFlow
   */
  protected String getClientSecretUnsafe(final JsonNode oauthConfig) {
    if (oauthConfig.get("client_secret") != null) {
      return oauthConfig.get("client_secret").asText();
    } else {
      throw new IllegalArgumentException("Undefined parameter 'client_secret' necessary for the OAuth Flow.");
    }
  }

}
