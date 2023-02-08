/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.utils;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonToken;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.AllowedHosts;
import io.airbyte.config.constants.AlwaysAllowedHosts;
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
  private final AlwaysAllowedHosts alwaysAllowedHosts = new AlwaysAllowedHosts();

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

    List<String> prefixes = new ArrayList<>();
    while (!jsonParser.isClosed()) {
      final JsonToken type = jsonParser.nextToken();
      if (type == JsonToken.FIELD_NAME) {
        final String key = jsonParser.getCurrentName();
        // the interface for allowedHosts is dot notation, e.g. `"${tunnel_method.tunnel_host}"`
        final String fullKey = (prefixes.isEmpty() ? "" : String.join(".", prefixes) + ".") + key;
        // the search path for JSON nodes is slash notation, e.g. `"/tunnel_method/tunnel_host"`
        final String lookupKey = "/" + (prefixes.isEmpty() ? "" : String.join("/", prefixes) + "/") + key;

        String value = config.at(lookupKey).textValue();
        if (value == null) {
          final Number numberValue = config.at(lookupKey).numberValue();
          if (numberValue != null) {
            value = numberValue.toString();
          }
        }

        if (value != null) {
          valuesMap.put(fullKey, value);
        }
      } else if (type == JsonToken.START_OBJECT) {
        if (jsonParser.getCurrentName() != null) {
          prefixes.add(jsonParser.getCurrentName());
        }
      } else if (type == JsonToken.END_OBJECT) {
        if (!prefixes.isEmpty()) {
          prefixes.remove(prefixes.size() - 1);
        }
      }
    }

    final StringSubstitutor sub = new StringSubstitutor(valuesMap);
    final List<String> hosts = allowedHosts.getHosts();
    for (String host : hosts) {
      final String replacedString = sub.replace(host);
      if (!replacedString.contains("${")) {
        resolvedHosts.add(replacedString);
      }
    }

    if (resolvedHosts.isEmpty() && !hosts.isEmpty()) {
      this.logger.error(
          "All allowedHosts values are un-replaced.  Check this connector's configuration or actor definition - " + allowedHosts.getHosts());
    }

    resolvedHosts.addAll(alwaysAllowedHosts.getHosts());

    final AllowedHosts resolvedAllowedHosts = new AllowedHosts();
    resolvedAllowedHosts.setHosts(resolvedHosts);
    return resolvedAllowedHosts;
  }

}
