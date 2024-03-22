/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.base;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Singleton of destination config for easy lookup of values.
 */
public class DestinationConfig {

  private static final Logger LOGGER = LoggerFactory.getLogger(DestinationConfig.class);

  private static DestinationConfig config;

  // whether the destination fully supports Destinations V2
  private boolean isV2Destination;

  @VisibleForTesting
  protected JsonNode root;

  private DestinationConfig() {}

  @VisibleForTesting
  public static void initialize(final JsonNode root) {
    initialize(root, false);
  }

  public static void initialize(final JsonNode root, final boolean isV2Destination) {
    if (config == null) {
      if (root == null) {
        throw new IllegalArgumentException("Cannot create DestinationConfig from null.");
      }
      config = new DestinationConfig();
      config.root = root;
      config.isV2Destination = isV2Destination;
    } else {
      LOGGER.warn("Singleton was already initialized.");
    }
  }

  public static DestinationConfig getInstance() {
    if (config == null) {
      throw new IllegalStateException("Singleton not initialized.");
    }
    return config;
  }

  @VisibleForTesting
  public static void clearInstance() {
    config = null;
  }

  public JsonNode getNodeValue(final String key) {
    final JsonNode node = config.root.get(key);
    if (node == null) {
      LOGGER.debug("Cannot find node with key {} ", key);
    }
    return node;
  }

  // string value, otherwise empty string
  public String getTextValue(final String key) {
    final JsonNode node = getNodeValue(key);
    if (node == null || !node.isTextual()) {
      LOGGER.debug("Cannot retrieve text value for node with key {}", key);
      return "";
    }
    return node.asText();
  }

  // boolean value, otherwise false
  public boolean getBooleanValue(final String key) {
    final JsonNode node = getNodeValue(key);
    if (node == null || !node.isBoolean()) {
      LOGGER.debug("Cannot retrieve boolean value for node with key {}", key);
      return false;
    }
    return node.asBoolean();
  }

  public boolean getIsV2Destination() {
    return isV2Destination;
  }

}
