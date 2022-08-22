/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.oauth;

import static com.fasterxml.jackson.databind.node.JsonNodeType.OBJECT;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.base.Strings;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationOAuthParameter;
import io.airbyte.config.SourceOAuthParameter;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MoreOAuthParameters {

  private static final Logger LOGGER = LoggerFactory.getLogger(Jsons.class);
  public static final String SECRET_MASK = "******";

  public static Optional<SourceOAuthParameter> getSourceOAuthParameter(
                                                                       final Stream<SourceOAuthParameter> stream,
                                                                       final UUID workspaceId,
                                                                       final UUID sourceDefinitionId) {
    return stream
        .filter(p -> sourceDefinitionId.equals(p.getSourceDefinitionId()))
        .filter(p -> p.getWorkspaceId() == null || workspaceId.equals(p.getWorkspaceId()))
        // we prefer params specific to a workspace before global ones (ie workspace is null)
        .min(Comparator.comparing(SourceOAuthParameter::getWorkspaceId, Comparator.nullsLast(Comparator.naturalOrder()))
            .thenComparing(SourceOAuthParameter::getOauthParameterId));
  }

  public static Optional<DestinationOAuthParameter> getDestinationOAuthParameter(
                                                                                 final Stream<DestinationOAuthParameter> stream,
                                                                                 final UUID workspaceId,
                                                                                 final UUID destinationDefinitionId) {
    return stream
        .filter(p -> destinationDefinitionId.equals(p.getDestinationDefinitionId()))
        .filter(p -> p.getWorkspaceId() == null || workspaceId.equals(p.getWorkspaceId()))
        // we prefer params specific to a workspace before global ones (ie workspace is null)
        .min(Comparator.comparing(DestinationOAuthParameter::getWorkspaceId, Comparator.nullsLast(Comparator.naturalOrder()))
            .thenComparing(DestinationOAuthParameter::getOauthParameterId));
  }

  public static JsonNode flattenOAuthConfig(final JsonNode config) {
    if (config.getNodeType() == OBJECT) {
      return flattenOAuthConfig((ObjectNode) Jsons.emptyObject(), (ObjectNode) config);
    } else {
      throw new IllegalStateException("Config is not an Object config, unable to flatten");
    }
  }

  private static ObjectNode flattenOAuthConfig(final ObjectNode flatConfig, final ObjectNode configToFlatten) {
    final List<String> keysToFlatten = new ArrayList<>();
    for (final String key : Jsons.keys(configToFlatten)) {
      if (configToFlatten.get(key).getNodeType() == OBJECT) {
        keysToFlatten.add(key);
      } else if (!flatConfig.has(key)) {
        flatConfig.set(key, configToFlatten.get(key));
      } else {
        throw new IllegalStateException(String.format("OAuth Config's key '%s' already exists", key));
      }
    }
    keysToFlatten.forEach(key -> flattenOAuthConfig(flatConfig, (ObjectNode) configToFlatten.get(key)));
    return flatConfig;
  }

  public static JsonNode mergeJsons(final ObjectNode mainConfig, final ObjectNode fromConfig) {
    for (final String key : Jsons.keys(fromConfig)) {
      if (fromConfig.get(key).getNodeType() == OBJECT) {
        // nested objects are merged rather than overwrite the contents of the equivalent object in config
        if (mainConfig.get(key) == null) {
          mergeJsons(mainConfig.putObject(key), (ObjectNode) fromConfig.get(key));
        } else if (mainConfig.get(key).getNodeType() == OBJECT) {
          mergeJsons((ObjectNode) mainConfig.get(key), (ObjectNode) fromConfig.get(key));
        } else {
          throw new IllegalStateException("Can't merge an object node into a non-object node!");
        }
      } else {
        if (!mainConfig.has(key) || isSecretMask(mainConfig.get(key).asText())) {
          LOGGER.debug(String.format("injecting instance wide parameter %s into config", key));
          mainConfig.set(key, fromConfig.get(key));
        }
      }
    }
    return mainConfig;
  }

  private static boolean isSecretMask(final String input) {
    return Strings.isNullOrEmpty(input.replaceAll("\\*", ""));
  }

}
