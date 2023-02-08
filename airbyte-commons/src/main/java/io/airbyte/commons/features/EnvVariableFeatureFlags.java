/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.features;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;
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

  private static final String ROUTE_TO_WORKSPACE_GEOGRAPHY_ENABLED = "ROUTE_TO_WORKSPACE_GEOGRAPHY_ENABLED";
  private static final String ROUTE_TASK_QUEUE_FOR_WORKSPACE_ALLOWLIST = "ROUTE_TASK_QUEUE_FOR_WORKSPACE_ALLOWLIST";

  public static final String STRICT_COMPARISON_NORMALIZATION_WORKSPACES = "STRICT_COMPARISON_NORMALIZATION_WORKSPACES";
  public static final String STRICT_COMPARISON_NORMALIZATION_TAG = "STRICT_COMPARISON_NORMALIZATION_TAG";

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

  @Override
  public boolean routeTaskQueueForWorkspaceEnabled() {
    return getEnvOrDefault(ROUTE_TO_WORKSPACE_GEOGRAPHY_ENABLED, false, Boolean::parseBoolean);
  }

  @Override
  public Set<String> routeTaskQueueForWorkspaceAllowList() {
    return getEnvOrDefault(ROUTE_TASK_QUEUE_FOR_WORKSPACE_ALLOWLIST, new HashSet<>(),
        (arg) -> Arrays.stream(arg.split(",")).collect(Collectors.toSet()));
  }

  @Override
  public String strictComparisonNormalizationWorkspaces() {
    return getEnvOrDefault(STRICT_COMPARISON_NORMALIZATION_WORKSPACES, "", (arg) -> arg);
  }

  @Override
  public String strictComparisonNormalizationTag() {
    return getEnvOrDefault(STRICT_COMPARISON_NORMALIZATION_TAG, "strict_comparison", (arg) -> arg);
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
