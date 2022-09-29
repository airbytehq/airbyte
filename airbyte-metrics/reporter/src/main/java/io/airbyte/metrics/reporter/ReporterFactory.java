/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import io.airbyte.db.Database;
import io.airbyte.metrics.lib.MetricClient;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.micronaut.context.annotation.Factory;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import org.jooq.DSLContext;

/**
 * Micronaut factory for creating the appropriate singletons utilized by the metric reporter service.
 */
@Factory
public class ReporterFactory {

  @Singleton
  public MetricClient metricClient() {
    return MetricClientFactory.getMetricClient();
  }

  @Singleton
  public Database database(@Named("config") final DSLContext context) {
    return new Database(context);
  }
}
