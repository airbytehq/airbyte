/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers.helpers;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.ArrayList;
import java.util.List;

public class OAuthPathExtractor {

  private static final String PROPERTIES = "properties";
  private static final String PATH_IN_CONNECTOR_CONFIG = "path_in_connector_config";

  public static List<List<String>> extractOauthConfigurationPaths(final JsonNode configuration) {

    if (configuration.has(PROPERTIES) && configuration.get(PROPERTIES).isObject()) {
      final List<List<String>> result = new ArrayList<>();

      configuration.get(PROPERTIES).fields().forEachRemaining(entry -> {
        final JsonNode value = entry.getValue();
        if (value.isObject() && value.has(PATH_IN_CONNECTOR_CONFIG) && value.get(PATH_IN_CONNECTOR_CONFIG).isArray()) {
          final List<String> path = new ArrayList<>();
          for (final JsonNode pathPart : value.get(PATH_IN_CONNECTOR_CONFIG)) {
            path.add(pathPart.textValue());
          }
          result.add(path);
        }
      });

      return result;
    } else {
      return new ArrayList<>();
    }
  }

}
