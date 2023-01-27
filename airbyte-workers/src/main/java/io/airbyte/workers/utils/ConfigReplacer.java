/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.utils;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonToken;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.AllowedHosts;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.apache.commons.text.StringSubstitutor;
import org.slf4j.Logger;

/**
 * This class takes values from a connector's configuration and uses it to fill in template-string
 * values. It substitutes strings with ${} access, e.g. "The ${animal} jumped over the ${target}"
 * with {animal: fox, target: fence}
 */
public class ConfigReplacer {

  private final Logger logger;

  public ConfigReplacer(Logger logger) {
    this.logger = logger;
  }

  /**
   * Note: This method does not interact with the secret manager. It is currently expected that all
   * replacement values are not secret (e.g. host vs password). This also assumed that the JSON config
   * for a connector has a single depth.
   */
  public AllowedHosts getAllowedHosts(AllowedHosts allowedHosts, JsonNode config) throws IOException {
    if (allowedHosts == null || allowedHosts.getHosts() == null) {
      return null;
    }

    final List<String> resolvedHosts = new ArrayList<>();
    final Map<String, String> valuesMap = new HashMap<>();
    final JsonParser jsonParser = config.traverse();
    while (!jsonParser.isClosed()) {
      if (jsonParser.nextToken() == JsonToken.FIELD_NAME) {
        final String key = jsonParser.getCurrentName();
        if (config.get(key) != null) {
          valuesMap.put(key, config.get(key).textValue());
        }
      }
    }

    final StringSubstitutor sub = new StringSubstitutor(valuesMap);
    final List<String> hosts = allowedHosts.getHosts();
    for (String host : hosts) {
      final String replacedString = sub.replace(host);
      if (replacedString.contains("${")) {
        this.logger.error(
            "The allowedHost value, '" + host + "', is expecting an interpolation value from the connector's configuration, but none is present");
      }
      resolvedHosts.add(replacedString);
    }

    final AllowedHosts resolvedAllowedHosts = new AllowedHosts();
    resolvedAllowedHosts.setHosts(resolvedHosts);
    return resolvedAllowedHosts;
  }

}
