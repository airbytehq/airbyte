/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.features;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class EnvVariableFeatureFlags implements FeatureFlags {

  @Override
  public boolean usesNewScheduler() {
    log.info("New Scheduler: " + Boolean.parseBoolean(System.getenv("NEW_SCHEDULER")));

    return Boolean.parseBoolean(System.getenv("NEW_SCHEDULER"));
  }

}
