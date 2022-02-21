/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import com.google.api.client.util.Preconditions;

/**
 * Wrapper class representing an emitted metric.
 *
 * Although {@link #metricDescription} isn't used, it's presence is enforced as metadata to
 * understand a metric.
 */
public class AirbyteMetric {

  public final String metricName;
  public final String metricDescription;

  public AirbyteMetric(final String metricName, final String metricDescription) {
    Preconditions.checkNotNull(metricDescription);

    this.metricName = metricName;
    this.metricDescription = metricDescription;
  }

}
