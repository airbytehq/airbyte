/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import lombok.AllArgsConstructor;

@AllArgsConstructor
public enum AirbyteApplications implements AirbyteApplication {

  AIRBYTE_METRICS_REPORTER("metrics-reporter"),
  AIRBYTE_SCHEDULER("scheduler"),
  AIRBYTE_WORKER("worker");

  private String applicationName;

  @Override
  public String getApplicationName() {
    return this.applicationName;
  }

}
