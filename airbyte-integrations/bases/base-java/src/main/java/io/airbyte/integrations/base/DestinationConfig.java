package io.airbyte.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.inject.Singleton;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Singleton
public class DestinationConfig {
  private static final Logger LOGGER = LoggerFactory.getLogger(DestinationConfig.class);

  private static DestinationConfig config;
  private JsonNode root;

  private DestinationConfig() {}

  public static void initialize(final JsonNode root) {
    if (config == null) {
      if (root == null) {
        throw new IllegalArgumentException("Cannot create DestinationConfig from null.");
      }
      config = new DestinationConfig();
      config.root = root;
    }
  }

  public static DestinationConfig getInstance() {
    if (config == null) {
      throw new IllegalStateException("Singleton not initialized.");
    }
    return config;
  }

  public JsonNode getNodeValue(final String key) {
    final JsonNode node = config.root.get(key);
    if (node == null) {
      LOGGER.warn("Cannot find node with key {} ", key);
    }
    return node;
  }

  public String getTextValue(final String key) {
    final JsonNode node = getNodeValue(key);
    if (!node.isTextual()) {
      LOGGER.warn("Cannot get text value for node that is not text type: {}", key);
    }
    return node.asText("");
  }

  public Boolean getBooleanValue(final String key) {
    final JsonNode node = getNodeValue(key);
    if (!node.isBoolean()) {
      LOGGER.warn("Cannot get boolean value for node that is not boolean type: {}", key);
    }
    return node.asBoolean(false);
  }
}
