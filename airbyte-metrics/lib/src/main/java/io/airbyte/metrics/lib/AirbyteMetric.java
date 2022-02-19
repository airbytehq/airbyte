/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import lombok.AllArgsConstructor;

@AllArgsConstructor
public class AirbyteMetric {

  private final AirbyteApplications airbyteApplication;
  public final String metricName;
  public final String metricDescription;

}
