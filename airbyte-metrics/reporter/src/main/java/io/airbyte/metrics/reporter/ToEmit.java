/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import io.airbyte.commons.lang.Exceptions;
import io.airbyte.metrics.lib.DogStatsDMetricSingleton;
import io.airbyte.metrics.lib.MetricQueries;
import io.airbyte.metrics.lib.MetricsRegistry;
import java.util.concurrent.TimeUnit;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public enum ToEmit {

  NUM_PENDING_JOBS(Exceptions.toSwallowExceptionRunnable(() -> {
    final var pendingJobs = ReporterApp.configDatabase.query(MetricQueries::numberOfPendingJobs);
    DogStatsDMetricSingleton.gauge(MetricsRegistry.NUM_PENDING_JOBS, pendingJobs);
  })),
  NUM_RUNNING_JOBS(Exceptions.toSwallowExceptionRunnable(() -> {
    final var runningJobs = ReporterApp.configDatabase.query(MetricQueries::numberOfRunningJobs);
    DogStatsDMetricSingleton.gauge(MetricsRegistry.NUM_RUNNING_JOBS, runningJobs);
  })),
  OLDEST_RUNNING_JOB_AGE_SECS(Exceptions.toSwallowExceptionRunnable(() -> {
    final var age = ReporterApp.configDatabase.query(MetricQueries::oldestRunningJobAgeSecs);
    DogStatsDMetricSingleton.gauge(MetricsRegistry.OLDEST_RUNNING_JOB_AGE_SECS, age);
  }));

  // default constructor
  final public Runnable emitRunnable;
  final public long period;
  final public TimeUnit timeUnit;

  ToEmit(Runnable toEmit) {
    this(toEmit, 15, TimeUnit.SECONDS);
  }

}
