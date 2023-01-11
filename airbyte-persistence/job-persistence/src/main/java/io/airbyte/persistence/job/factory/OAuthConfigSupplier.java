/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job.factory;

import static com.fasterxml.jackson.databind.node.JsonNodeType.ARRAY;
import static com.fasterxml.jackson.databind.node.JsonNodeType.OBJECT;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.oauth.MoreOAuthParameters;
import io.airbyte.persistence.job.tracker.TrackingMetadata;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.BiConsumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OAuthConfigSupplier {

  private static final Logger LOGGER = LoggerFactory.getLogger(OAuthConfigSupplier.class);

  public static final String PATH_IN_CONNECTOR_CONFIG = "path_in_connector_config";
  private static final String PROPERTIES = "properties";
  final private ConfigRepository configRepository;
  private final TrackingClient trackingClient;

  public OAuthConfigSupplier(final ConfigRepository configRepository, final TrackingClient trackingClient) {
    this.configRepository = configRepository;
    this.trackingClient = trackingClient;
  }

  public static boolean hasOAuthConfigSpecification(final ConnectorSpecification spec) {
    return spec != null && spec.getAdvancedAuth() != null && spec.getAdvancedAuth().getOauthConfigSpecification() != null;
  }

  public JsonNode maskSourceOAuthParameters(final UUID sourceDefinitionId, final UUID workspaceId, final JsonNode sourceConnectorConfig)
      throws IOException {
    try {
      final StandardSourceDefinition sourceDefinition = configRepository.getStandardSourceDefinition(sourceDefinitionId);
      MoreOAuthParameters.getSourceOAuthParameter(configRepository.listSourceOAuthParam().stream(), workspaceId, sourceDefinitionId)
          .ifPresent(sourceOAuthParameter -> {
            maskOauthParameters(sourceDefinition.getName(), sourceDefinition.getSpec(), sourceConnectorConfig);
          });
      return sourceConnectorConfig;
    } catch (final JsonValidationException | ConfigNotFoundException e) {
      throw new IOException(e);
    }
  }

  public JsonNode maskDestinationOAuthParameters(final UUID destinationDefinitionId,
                                                 final UUID workspaceId,
                                                 final JsonNode destinationConnectorConfig)
      throws IOException {
    try {
      final StandardDestinationDefinition destinationDefinition = configRepository.getStandardDestinationDefinition(destinationDefinitionId);
      MoreOAuthParameters.getDestinationOAuthParameter(configRepository.listDestinationOAuthParam().stream(), workspaceId, destinationDefinitionId)
          .ifPresent(destinationOAuthParameter -> {
            maskOauthParameters(destinationDefinition.getName(), destinationDefinition.getSpec(), destinationConnectorConfig);
          });
      return destinationConnectorConfig;
    } catch (final JsonValidationException | ConfigNotFoundException e) {
      throw new IOException(e);
    }
  }

  public JsonNode injectSourceOAuthParameters(final UUID sourceDefinitionId, final UUID workspaceId, final JsonNode sourceConnectorConfig)
      throws IOException {
    try {
      final StandardSourceDefinition sourceDefinition = configRepository.getStandardSourceDefinition(sourceDefinitionId);
      MoreOAuthParameters.getSourceOAuthParameter(configRepository.listSourceOAuthParam().stream(), workspaceId, sourceDefinitionId)
          .ifPresent(sourceOAuthParameter -> {
            if (injectOAuthParameters(sourceDefinition.getName(), sourceDefinition.getSpec(), sourceOAuthParameter.getConfiguration(),
                sourceConnectorConfig)) {
              final Map<String, Object> metadata = TrackingMetadata.generateSourceDefinitionMetadata(sourceDefinition);
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
      final StandardDestinationDefinition destinationDefinition = configRepository.getStandardDestinationDefinition(destinationDefinitionId);
      MoreOAuthParameters.getDestinationOAuthParameter(configRepository.listDestinationOAuthParam().stream(), workspaceId, destinationDefinitionId)
          .ifPresent(destinationOAuthParameter -> {
            if (injectOAuthParameters(destinationDefinition.getName(), destinationDefinition.getSpec(), destinationOAuthParameter.getConfiguration(),
                destinationConnectorConfig)) {
              final Map<String, Object> metadata = TrackingMetadata.generateDestinationDefinitionMetadata(destinationDefinition);
              Exceptions.swallow(() -> trackingClient.track(workspaceId, "OAuth Injection - Backend", metadata));
            }
          });
      return destinationConnectorConfig;
    } catch (final JsonValidationException | ConfigNotFoundException e) {
      throw new IOException(e);
    }
  }

  /**
   * Gets the OAuth parameter paths as specified in the connector spec and traverses through them
   */
  private static void traverseOAuthOutputPaths(final ConnectorSpecification spec,
                                               final String connectorName,
                                               final BiConsumer<String, List<String>> consumer) {
    final JsonNode outputSpecTop = spec.getAdvancedAuth().getOauthConfigSpecification().getCompleteOauthServerOutputSpecification();
    final JsonNode outputSpec;
    if (outputSpecTop.has(PROPERTIES)) {
      outputSpec = outputSpecTop.get(PROPERTIES);
    } else {
      LOGGER.error(String.format("In %s's advanced_auth spec, completeOAuthServerOutputSpecification does not declare properties.", connectorName));
      return;
    }

    for (final String key : Jsons.keys(outputSpec)) {
      final JsonNode node = outputSpec.get(key);
      if (node.getNodeType() == OBJECT) {
        final JsonNode pathNode = node.get(PATH_IN_CONNECTOR_CONFIG);
        if (pathNode != null && pathNode.getNodeType() == ARRAY) {
          final List<String> propertyPath = new ArrayList<>();
          final ArrayNode arrayNode = (ArrayNode) pathNode;
          for (int i = 0; i < arrayNode.size(); ++i) {
            propertyPath.add(arrayNode.get(i).asText());
          }
          if (!propertyPath.isEmpty()) {
            consumer.accept(key, propertyPath);
          } else {
            LOGGER.error(String.format("In %s's advanced_auth spec, completeOAuthServerOutputSpecification includes an invalid empty %s for %s",
                connectorName, PATH_IN_CONNECTOR_CONFIG, key));
          }
        } else {
          LOGGER.error(
              String.format("In %s's advanced_auth spec, completeOAuthServerOutputSpecification does not declare an Array<String> %s for %s",
                  connectorName, PATH_IN_CONNECTOR_CONFIG, key));
        }
      } else {
        LOGGER.error(String.format("In %s's advanced_auth spec, completeOAuthServerOutputSpecification does not declare an ObjectNode for %s",
            connectorName, key));
      }
    }
  }

  private static void maskOauthParameters(final String connectorName, final ConnectorSpecification spec, final JsonNode connectorConfig) {
    if (!hasOAuthConfigSpecification(spec)) {
      return;
    }
    if (!checkOAuthPredicate(spec.getAdvancedAuth().getPredicateKey(), spec.getAdvancedAuth().getPredicateValue(), connectorConfig)) {
      // OAuth is not applicable in this connectorConfig due to the predicate not being verified
      return;
    }

    traverseOAuthOutputPaths(spec, connectorName, (_key, propertyPath) -> {
      Jsons.replaceNestedValue(connectorConfig, propertyPath, Jsons.jsonNode(MoreOAuthParameters.SECRET_MASK));
    });

  }

  private static boolean injectOAuthParameters(final String connectorName,
                                               final ConnectorSpecification spec,
                                               final JsonNode oAuthParameters,
                                               final JsonNode connectorConfig) {
    if (!hasOAuthConfigSpecification(spec)) {
      // keep backward compatible behavior if connector does not declare an OAuth config spec
      MoreOAuthParameters.mergeJsons((ObjectNode) connectorConfig, (ObjectNode) oAuthParameters);
      return true;
    }
    if (!checkOAuthPredicate(spec.getAdvancedAuth().getPredicateKey(), spec.getAdvancedAuth().getPredicateValue(), connectorConfig)) {
      // OAuth is not applicable in this connectorConfig due to the predicate not being verified
      return false;
    }

    // TODO: if we write a migration to flatten persisted configs in db, we don't need to flatten
    // here see https://github.com/airbytehq/airbyte/issues/7624
    final JsonNode flatOAuthParameters = MoreOAuthParameters.flattenOAuthConfig(oAuthParameters);

    final AtomicBoolean result = new AtomicBoolean(false);
    traverseOAuthOutputPaths(spec, connectorName, (key, propertyPath) -> {
      Jsons.replaceNestedValue(connectorConfig, propertyPath, flatOAuthParameters.get(key));
      result.set(true);
    });

    return result.get();
  }

  private static boolean checkOAuthPredicate(final List<String> predicateKey, final String predicateValue, final JsonNode connectorConfig) {
    if (predicateKey != null && !predicateKey.isEmpty()) {
      JsonNode node = connectorConfig;
      for (final String key : predicateKey) {
        if (node.has(key)) {
          node = node.get(key);
        } else {
          return false;
        }
      }
      if (predicateValue != null && !predicateValue.isBlank()) {
        return node.asText().equals(predicateValue);
      } else {
        return true;
      }
    }
    return true;
  }

}
