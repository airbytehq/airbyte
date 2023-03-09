/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers.helpers;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class OAuthPathExtractor {

  private static final String PROPERTIES = "properties";
  private static final String PATH_IN_CONNECTOR_CONFIG = "path_in_connector_config";

  public static Map<String, List<String>> extractOauthConfigurationPaths(final JsonNode configuration) {

    if (configuration != null && configuration.has(PROPERTIES) && configuration.get(PROPERTIES).isObject()) {
      final Map<String, List<String>> result = new HashMap<>();

      configuration.get(PROPERTIES).fields().forEachRemaining(entry -> {
        final JsonNode value = entry.getValue();
        if (value.isObject() && value.has(PATH_IN_CONNECTOR_CONFIG) && value.get(PATH_IN_CONNECTOR_CONFIG).isArray()) {
          final List<String> path = new ArrayList<>();
          for (final JsonNode pathPart : value.get(PATH_IN_CONNECTOR_CONFIG)) {
            path.add(pathPart.textValue());
          }
          result.put(entry.getKey(), path);
        }
      });

      return result;
    } else {
      return new HashMap<>();
    }
  }

}
