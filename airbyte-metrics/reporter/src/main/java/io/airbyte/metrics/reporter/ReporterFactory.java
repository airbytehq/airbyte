/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import io.airbyte.metrics.lib.MetricClient;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.micronaut.context.annotation.Factory;
import jakarta.inject.Singleton;

/**
 * Micronaut factory for creating the appropriate singletons utilized by the metric reporter
 * service.
 */
@Factory
class ReporterFactory {

  @Singleton
  public MetricClient metricClient() {
    return MetricClientFactory.getMetricClient();
  }

}
