/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.features;

import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EnvVariableFeatureFlags implements FeatureFlags {

  private static final Logger log = LoggerFactory.getLogger(EnvVariableFeatureFlags.class);

  public static final String AUTO_DETECT_SCHEMA = "AUTO_DETECT_SCHEMA";
  // Set this value to true to see all messages from the source to destination, set to one second
  // emission
  public static final String LOG_CONNECTOR_MESSAGES = "LOG_CONNECTOR_MESSAGES";
  public static final String APPLY_FIELD_SELECTION = "APPLY_FIELD_SELECTION";
  public static final String FIELD_SELECTION_WORKSPACES = "FIELD_SELECTION_WORKSPACES";
  public static final String CONCURRENT_SOURCE_STREAM_READ = "CONCURRENT_SOURCE_STREAM_READ";
  public static final String STRICT_COMPARISON_NORMALIZATION_WORKSPACES = "STRICT_COMPARISON_NORMALIZATION_WORKSPACES";
  public static final String STRICT_COMPARISON_NORMALIZATION_TAG = "STRICT_COMPARISON_NORMALIZATION_TAG";
  public static final String DEPLOYMENT_MODE = "DEPLOYMENT_MODE";

  @Override
  public boolean autoDetectSchema() {
    return getEnvOrDefault(AUTO_DETECT_SCHEMA, true, Boolean::parseBoolean);
  }

  @Override
  public boolean logConnectorMessages() {
    return getEnvOrDefault(LOG_CONNECTOR_MESSAGES, false, Boolean::parseBoolean);
  }

  @Override
  public boolean concurrentSourceStreamRead() {
    return getEnvOrDefault(CONCURRENT_SOURCE_STREAM_READ, false, Boolean::parseBoolean);
  }

  @Override
  public boolean applyFieldSelection() {
    return getEnvOrDefault(APPLY_FIELD_SELECTION, false, Boolean::parseBoolean);
  }

  @Override
  public String fieldSelectionWorkspaces() {
    return getEnvOrDefault(FIELD_SELECTION_WORKSPACES, "", (arg) -> arg);
  }

  @Override
  public String strictComparisonNormalizationWorkspaces() {
    return getEnvOrDefault(STRICT_COMPARISON_NORMALIZATION_WORKSPACES, "", (arg) -> arg);
  }

  @Override
  public String strictComparisonNormalizationTag() {
    return getEnvOrDefault(STRICT_COMPARISON_NORMALIZATION_TAG, "strict_comparison2", (arg) -> arg);
  }

  @Override
  public String deploymentMode() {
    return getEnvOrDefault(DEPLOYMENT_MODE, "", (arg) -> arg);
  }

  // TODO: refactor in order to use the same method than the ones in EnvConfigs.java
  public <T> T getEnvOrDefault(final String key, final T defaultValue, final Function<String, T> parser) {
    final String value = System.getenv(key);
    if (value != null && !value.isEmpty()) {
      return parser.apply(value);
    } else {
      log.debug("Using default value for environment variable {}: '{}'", key, defaultValue);
      return defaultValue;
    }
  }

}
