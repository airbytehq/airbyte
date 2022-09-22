/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.features;

import java.util.function.Function;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class EnvVariableFeatureFlags implements FeatureFlags {

  public static final String USE_STREAM_CAPABLE_STATE = "USE_STREAM_CAPABLE_STATE";
  public static final String LOG_CONNECTOR_MESSAGES = "LOG_CONNECTOR_MESSAGES";

  @Override
  public boolean autoDisablesFailingConnections() {
    log.info("Auto Disable Failing Connections: " + Boolean.parseBoolean(System.getenv("AUTO_DISABLE_FAILING_CONNECTIONS")));

    return Boolean.parseBoolean(System.getenv("AUTO_DISABLE_FAILING_CONNECTIONS"));
  }

  @Override
  public boolean exposeSecretsInExport() {
    return Boolean.parseBoolean(System.getenv("EXPOSE_SECRETS_IN_EXPORT"));
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
  public boolean logConnectorMessages() {
    return getEnvOrDefault(LOG_CONNECTOR_MESSAGES, false, Boolean::parseBoolean);
  }

  // TODO: refactor in order to use the same method than the ones in EnvConfigs.java
  public <T> T getEnvOrDefault(final String key, final T defaultValue, final Function<String, T> parser) {
    final String value = System.getenv(key);
    if (value != null && !value.isEmpty()) {
      return parser.apply(value);
    } else {
      log.info("Using default value for environment variable {}: '{}'", key, defaultValue);
      return defaultValue;
    }
  }

}
