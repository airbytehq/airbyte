/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.configoss;

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
   * Defines the bucket for caching specs. This immensely speeds up spec operations. This is updated
   * when new versions are published.
   */
  String getSpecCacheBucket();

  enum DeploymentMode {
    OSS,
    CLOUD
  }

}
