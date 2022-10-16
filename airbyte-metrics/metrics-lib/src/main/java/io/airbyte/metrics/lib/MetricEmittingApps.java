/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import lombok.AllArgsConstructor;

/**
 * Enum containing all applications metrics are emitted for. Used to initialize
 * {@link MetricClientFactory.initialize(MetricEmittingApp)}.
 *
 * Application Name Conventions:
 * <p>
 * - Drop the airbyte prefix when naming applications, e.g airbyte-server -> server.
 * <p>
 * - Use dashes to delimit application names with multiple words.
 * <p>
 * - Use lowercase.
 */
@AllArgsConstructor
public enum MetricEmittingApps implements MetricEmittingApp {

  METRICS_REPORTER("metrics-reporter"),
  WORKER("worker");

  private String applicationName;

  @Override
  public String getApplicationName() {
    return this.applicationName;
  }

}
