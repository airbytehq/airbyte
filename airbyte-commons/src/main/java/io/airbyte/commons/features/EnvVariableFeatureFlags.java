/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.features;

public class EnvVariableFeatureFlags implements FeatureFlags {

  @Override
  public boolean usesNewScheduler() {
    return Boolean.parseBoolean(System.getenv("NEW_SCHEDULER"));
  }

}
