/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import io.airbyte.commons.version.AirbyteVersion;

/**
 * This interface defines the general variables for configuring Airbyte.
 * <p>
 * Please update the configuring-airbyte.md document when modifying this file.
 * <p>
 * Please also add one of the following tags to the env var accordingly:
 * <p>
 * 1. 'Internal-use only' if a var is mainly for Airbyte-only configuration. e.g. tracking, test or
 * Cloud related etc.
 * <p>
 * 2. 'Alpha support' if a var does not have proper support and should be used with care.
 */

@SuppressWarnings("PMD.BooleanGetMethodName")
public interface Configs {


  /**
   * Defines the Airbyte deployment version.
   */
  AirbyteVersion getAirbyteVersion();

  /**
   * Defines the bucket for caching specs. This immensely speeds up spec operations. This is updated
   * when new versions are published.
   */
  String getSpecCacheBucket();

  // Database

  /**
   * If using a LaunchDarkly feature flag client, this API key will be used.
   *
   * @return LaunchDarkly API key as a string.
   */
  String getLaunchDarklyKey();

  /**
   * Get the type of feature flag client to use.
   */
  String getFeatureFlagClient();

  // Jobs - Kube only

  enum JobErrorReportingStrategy {
    SENTRY,
    LOGGING
  }

  enum WorkerEnvironment {
    DOCKER,
    KUBERNETES
  }

  enum DeploymentMode {
    OSS,
    CLOUD
  }

}
