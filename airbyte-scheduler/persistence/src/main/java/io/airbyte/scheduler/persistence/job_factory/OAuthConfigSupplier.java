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
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.MoreOAuthParameters;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.OAuth2Specification;
import io.airbyte.scheduler.persistence.job_tracker.TrackingMetadata;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OAuthConfigSupplier {

  private static final Logger LOGGER = LoggerFactory.getLogger(OAuthConfigSupplier.class);

  public static final String SECRET_MASK = "******";
  final private ConfigRepository configRepository;
  private final boolean maskSecrets;
  private final TrackingClient trackingClient;

  public OAuthConfigSupplier(final ConfigRepository configRepository, final boolean maskSecrets, final TrackingClient trackingClient) {
    this.configRepository = configRepository;
    this.maskSecrets = maskSecrets;
    this.trackingClient = trackingClient;
  }

  public JsonNode injectSourceOAuthParameters(final UUID sourceDefinitionId,
                                              final UUID workspaceId,
                                              final JsonNode sourceConnectorConfig,
                                              final ConnectorSpecification spec)
      throws IOException {
    try {
      final ImmutableMap<String, Object> metadata = generateSourceMetadata(sourceDefinitionId);
      MoreOAuthParameters.getSourceOAuthParameter(configRepository.listSourceOAuthParam().stream(), workspaceId, sourceDefinitionId)
          .ifPresent(
              sourceOAuthParameter -> {
                injectParametersFromConfig((ObjectNode) sourceConnectorConfig, (ObjectNode) sourceOAuthParameter.getConfiguration(), spec);
                if (!maskSecrets) {
                  // when maskSecrets = true, no real oauth injections is happening
                  Exceptions.swallow(() -> trackingClient.track(workspaceId, "OAuth Injection - Backend", metadata));
                }
              });
      return sourceConnectorConfig;
    } catch (final JsonValidationException | ConfigNotFoundException e) {
      throw new IOException(e);
    }
  }

  /**
   * Inject oAuth config into connector's config according to oAuth flow specified in spec.
   *
   * @param sourceConnectorConfig Json representing current connectrs config.
   * @param oAuthParameters config json with instance wide parameters from config repository.
   * @param spec connector specification obtained by executing "spec" command.
   */
  private void injectParametersFromConfig(final ObjectNode sourceConnectorConfig,
                                          final ObjectNode oAuthParameters,
                                          final ConnectorSpecification spec) {
    final OAuth2Specification oAuth2Spec = spec.getAuthSpecification().getOauth2Specification();
    final List<String> rootObject = oAuth2Spec.getRootObject();
    final List<List<String>> oAuthFlowInitParameters = oAuth2Spec.getOauthFlowInitParameters();
    final ObjectNode configRoot;
    if (rootObject.isEmpty()) {
      configRoot = sourceConnectorConfig;
    } else {
      configRoot = (ObjectNode) sourceConnectorConfig.get(rootObject.get(0));
    }
    if (rootObject.size() == 2) {
      // In case if root object contains 2 elements first if root index and
      // second is oneOf object index. We need to check if oAuth parameters
      // injection needed.
      final ImmutablePair<String, String> expectedConstValue = getExpectedConstValue(spec.getConnectionSpecification(), rootObject);
      if (!configRoot.has(expectedConstValue.getLeft()) ||
          !configRoot.get(expectedConstValue.getLeft()).asText().equals(expectedConstValue.getRight())) {
        return;
      }
    }
    oAuthFlowInitParameters.forEach((parameter) -> {
      final String fieldName = parameter.get(parameter.size() - 1);
      ObjectNode fieldRoot = configRoot;
      for (String nextField : parameter.subList(0, parameter.size() - 1)) {
        fieldRoot = (ObjectNode) fieldRoot.get(nextField);
      }
      if (maskSecrets) {
        fieldRoot.set(fieldName, Jsons.jsonNode(SECRET_MASK));
      } else {
        fieldRoot.set(fieldName, oAuthParameters.get(fieldName));
      }
    });
  }

  /**
   * Find signature key-value pair for oAuth flow specified by connector's spec rootObject parameter.
   * Its logic based on airbyte spec oneOf requirment
   * https://docs.airbyte.io/connector-development/connector-specification-reference#using-oneofs Each
   * of oneOf object should contain one common const field.
   *
   * @param schema jsonschema from connector's spec.
   * @param rootObject root object config from connector oAuth flow config. For this method should
   *        have 2 elements: first is root object name and second is index inside oneOf array.
   * @return Pair representing field name and value of expected oAuth parameter in user config. If
   *         user config missed this name/value that means it is not required to do oAuth injection
   */
  private ImmutablePair<String, String> getExpectedConstValue(final JsonNode schema, List<String> rootObject) {
    int index = Integer.parseInt(rootObject.get(1));
    final ObjectNode targetObject = (ObjectNode) schema.get("properties").get(rootObject.get(0)).get("oneOf").get(index);
    Iterator<Map.Entry<String, JsonNode>> fields = targetObject.get("properties").fields();
    while (fields.hasNext()) {
      Map.Entry<String, JsonNode> entry = fields.next();
      if (entry.getValue().has("const")) {
        return ImmutablePair.of(entry.getKey(), entry.getValue().get("const").asText());
      }
    }
    return ImmutablePair.of("", "");

  }

  public JsonNode injectDestinationOAuthParameters(final UUID destinationDefinitionId,
                                                   final UUID workspaceId,
                                                   final JsonNode destinationConnectorConfig)
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
    } catch (final JsonValidationException | ConfigNotFoundException e) {
      throw new IOException(e);
    }
  }

  @VisibleForTesting
  void injectJsonNode(final ObjectNode mainConfig, final ObjectNode fromConfig) {
    // TODO this method might make sense to have as a general utility in Jsons
    for (final String key : Jsons.keys(fromConfig)) {
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

  private static boolean isSecretMask(final String input) {
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
