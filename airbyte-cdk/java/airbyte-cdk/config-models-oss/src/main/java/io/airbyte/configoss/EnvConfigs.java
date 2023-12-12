/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.configoss;

import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings({"PMD.LongVariable", "PMD.CyclomaticComplexity", "PMD.AvoidReassigningParameters", "PMD.ConstructorCallsOverridableMethod"})
public class EnvConfigs implements Configs {

  private static final Logger LOGGER = LoggerFactory.getLogger(EnvConfigs.class);

  // env variable names
  public static final String SPEC_CACHE_BUCKET = "SPEC_CACHE_BUCKET";
  public static final String LOCAL_CONNECTOR_CATALOG_PATH = "LOCAL_CONNECTOR_CATALOG_PATH";

  // defaults
  private static final String DEFAULT_SPEC_CACHE_BUCKET = "io-airbyte-cloud-spec-cache";

  private final Function<String, String> getEnv;

  /**
   * Constructs {@link EnvConfigs} from actual environment variables.
   */
  public EnvConfigs() {
    this(System.getenv());
  }

  /**
   * Constructs {@link EnvConfigs} from a provided map. This can be used for testing or getting
   * variables from a non-envvar source.
   */
  public EnvConfigs(final Map<String, String> envMap) {
    getEnv = envMap::get;
  }

  @Override
  public String getSpecCacheBucket() {
    return getEnvOrDefault(SPEC_CACHE_BUCKET, DEFAULT_SPEC_CACHE_BUCKET);
  }

  public Optional<String> getLocalCatalogPath() {
    return Optional.ofNullable(getEnv(LOCAL_CONNECTOR_CATALOG_PATH));
  }

  // Worker - Data plane

  // Helpers
  public String getEnvOrDefault(final String key, final String defaultValue) {
    return getEnvOrDefault(key, defaultValue, Function.identity(), false);
  }

  public <T> T getEnvOrDefault(final String key, final T defaultValue, final Function<String, T> parser, final boolean isSecret) {
    final String value = getEnv.apply(key);
    if (value != null && !value.isEmpty()) {
      return parser.apply(value);
    } else {
      LOGGER.info("Using default value for environment variable {}: '{}'", key, isSecret ? "*****" : defaultValue);
      return defaultValue;
    }
  }

  public String getEnv(final String name) {
    return getEnv.apply(name);
  }

}
