/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceOAuthParameter;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.OAuthConfigSpecification;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.function.BiConsumer;

/**
 * Abstract Class implementing common base methods for managing oAuth config (instance-wide) and
 * oAuth specifications
 */
public abstract class BaseOAuthFlow implements OAuthFlowImplementation {

  public static final String PROPERTIES = "properties";
  private final ConfigRepository configRepository;

  public BaseOAuthFlow(final ConfigRepository configRepository) {
    this.configRepository = configRepository;
  }

  protected JsonNode getSourceOAuthParamConfig(final UUID workspaceId, final UUID sourceDefinitionId) throws IOException, ConfigNotFoundException {
    try {
      final Optional<SourceOAuthParameter> param = MoreOAuthParameters.getSourceOAuthParameter(
          configRepository.listSourceOAuthParam().stream(), workspaceId, sourceDefinitionId);
      if (param.isPresent()) {
        // TODO: if we write a flyway migration to flatten persisted configs in db, we don't need to flatten
        // here see https://github.com/airbytehq/airbyte/issues/7624
        return MoreOAuthParameters.flattenOAuthConfig(param.get().getConfiguration());
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
        // TODO: if we write a migration to flatten persisted configs in db, we don't need to flatten
        // here see https://github.com/airbytehq/airbyte/issues/7624
        return MoreOAuthParameters.flattenOAuthConfig(param.get().getConfiguration());
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
    return getConfigValueUnsafe(oauthConfig, "client_id");
  }

  /**
   * Throws an exception if the client secret cannot be extracted. Subclasses should override this to
   * parse the config differently.
   *
   * @return The configured client secret for this OAuthFlow
   */
  protected String getClientSecretUnsafe(final JsonNode oauthConfig) {
    return getConfigValueUnsafe(oauthConfig, "client_secret");
  }

  protected static String getConfigValueUnsafe(final JsonNode oauthConfig, final String fieldName) {
    if (oauthConfig.get(fieldName) != null) {
      return oauthConfig.get(fieldName).asText();
    } else {
      throw new IllegalArgumentException(String.format("Undefined parameter '%s' necessary for the OAuth Flow.", fieldName));
    }
  }

  /**
   * completeOAuth calls should output a flat map of fields produced by the oauth flow to be forwarded
   * back to the connector config. This @deprecated function is used when the connector's oauth
   * specifications are unknown. So it ends up using hard-coded output path in the OAuth Flow
   * implementation instead of relying on the connector's specification to determine where the outputs
   * should be stored.
   */
  @Deprecated
  protected Map<String, Object> formatOAuthOutput(final JsonNode oAuthParamConfig,
                                                  final Map<String, Object> oauthOutput,
                                                  final List<String> outputPath) {
    Map<String, Object> result = new HashMap<>(oauthOutput);
    for (final String key : Jsons.keys(oAuthParamConfig)) {
      result.put(key, MoreOAuthParameters.SECRET_MASK);
    }
    for (final String node : outputPath) {
      result = Map.of(node, result);
    }
    return result;
  }

  /**
   * completeOAuth calls should output a flat map of fields produced by the oauth flow to be forwarded
   * back to the connector config. This function follows the connector's oauth specifications of which
   * outputs are expected and filters them accordingly.
   */
  protected Map<String, Object> formatOAuthOutput(final JsonNode oAuthParamConfig,
                                                  final Map<String, Object> completeOAuthFlow,
                                                  final OAuthConfigSpecification oAuthConfigSpecification)
      throws JsonValidationException {
    final JsonSchemaValidator validator = new JsonSchemaValidator();

    final Map<String, Object> oAuthOutputs = formatOAuthOutput(
        validator,
        oAuthConfigSpecification.getCompleteOauthOutputSpecification(),
        completeOAuthFlow.keySet(),
        (resultMap, key) -> resultMap.put(key, completeOAuthFlow.get(key)));

    final Map<String, Object> oAuthServerOutputs = formatOAuthOutput(
        validator,
        oAuthConfigSpecification.getCompleteOauthServerOutputSpecification(),
        Jsons.keys(oAuthParamConfig),
        // TODO secrets should be masked with the correct type
        // https://github.com/airbytehq/airbyte/issues/5990
        // In the short-term this is not world-ending as all secret fields are currently strings
        (resultMap, key) -> resultMap.put(key, MoreOAuthParameters.SECRET_MASK));

    return MoreMaps.merge(oAuthServerOutputs, oAuthOutputs);
  }

  private static Map<String, Object> formatOAuthOutput(final JsonSchemaValidator validator,
                                                       final JsonNode outputSchema,
                                                       final Collection<String> keys,
                                                       final BiConsumer<Builder<String, Object>, String> replacement)
      throws JsonValidationException {
    Map<String, Object> result = Map.of();
    if (outputSchema != null && outputSchema.has(PROPERTIES)) {
      final Builder<String, Object> mapBuilder = ImmutableMap.builder();
      for (final String key : keys) {
        if (outputSchema.get(PROPERTIES).has(key)) {
          replacement.accept(mapBuilder, key);
        }
      }
      result = mapBuilder.build();
      validator.ensure(outputSchema, Jsons.jsonNode(result));
    }
    return result;
  }

  /**
   * This function should be redefined in each OAuthFlow implementation to isolate such "hardcoded"
   * values. It is being @deprecated because the output path should not be "hard-coded" in the OAuth
   * flow implementation classes anymore but will be specified as part of the OAuth Specification
   * object
   */
  @Deprecated
  public abstract List<String> getDefaultOAuthOutputPath();

}
