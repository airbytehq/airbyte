/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.features;

import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EnvVariableFeatureFlags implements FeatureFlags {

  private static final Logger log = LoggerFactory.getLogger(EnvVariableFeatureFlags.class);

  public static final String USE_STREAM_CAPABLE_STATE = "USE_STREAM_CAPABLE_STATE";
  public static final String AUTO_DETECT_SCHEMA = "AUTO_DETECT_SCHEMA";
  // Set this value to true to see all messages from the source to destination, set to one second
  // emission
  public static final String LOG_CONNECTOR_MESSAGES = "LOG_CONNECTOR_MESSAGES";
  public static final String NEED_STATE_VALIDATION = "NEED_STATE_VALIDATION";
  public static final String APPLY_FIELD_SELECTION = "APPLY_FIELD_SELECTION";

  public static final String FIELD_SELECTION_WORKSPACES = "FIELD_SELECTION_WORKSPACES";

  @Override
  public boolean autoDisablesFailingConnections() {
    log.info("Auto Disable Failing Connections: " + Boolean.parseBoolean(System.getenv("AUTO_DISABLE_FAILING_CONNECTIONS")));

    return Boolean.parseBoolean(System.getenv("AUTO_DISABLE_FAILING_CONNECTIONS"));
  }

  @Override
  public boolean forceSecretMigration() {
    return Boolean.parseBoolean(System.getenv("FORCE_MIGRATE_SECRET_STORE"));
  }

  @Override
  public boolean useStreamCapableState() {
    return getEnvOrDefault(USE_STREAM_CAPABLE_STATE, false, Boolean::parseBoolean);
  }

  @Override
  public boolean autoDetectSchema() {
    return getEnvOrDefault(AUTO_DETECT_SCHEMA, true, Boolean::parseBoolean);
  }

  @Override
  public boolean logConnectorMessages() {
    return getEnvOrDefault(LOG_CONNECTOR_MESSAGES, false, Boolean::parseBoolean);
  }

  @Override
  public boolean needStateValidation() {
    return getEnvOrDefault(NEED_STATE_VALIDATION, true, Boolean::parseBoolean);
  }

  @Override
  public boolean applyFieldSelection() {
    return getEnvOrDefault(APPLY_FIELD_SELECTION, false, Boolean::parseBoolean);
  }

  @Override
  public String fieldSelectionWorkspaces() {
    return getEnvOrDefault(FIELD_SELECTION_WORKSPACES, "", (arg) -> arg);
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
