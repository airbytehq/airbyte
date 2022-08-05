/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.features;

public class EnvVariableFeatureFlags implements FeatureFlags {

  @Override
  public boolean usesNewScheduler() {
    return System.getenv().containsKey("NEW_SCHEDULER");
  }

}
