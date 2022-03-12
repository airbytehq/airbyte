/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import io.airbyte.commons.lang.Exceptions;
import io.airbyte.db.instance.jobs.jooq.enums.JobStatus;
import io.airbyte.metrics.lib.DogStatsDMetricSingleton;
import io.airbyte.metrics.lib.MetricQueries;
import io.airbyte.metrics.lib.MetricTags;
import io.airbyte.metrics.lib.MetricsRegistry;
import java.util.concurrent.TimeUnit;
import lombok.AllArgsConstructor;
import org.apache.commons.lang3.tuple.Pair;

/**
 * This class contains all metrics emitted by the {@link ReporterApp}.
 */
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
  })),
  OLDEST_PENDING_JOB_AGE_SECS(Exceptions.toSwallowExceptionRunnable(() -> {
    final var age = ReporterApp.configDatabase.query(MetricQueries::oldestPendingJobAgeSecs);
    DogStatsDMetricSingleton.gauge(MetricsRegistry.OLDEST_PENDING_JOB_AGE_SECS, age);
  })),
  NUM_ACTIVE_CONN_PER_WORKSPACE(Exceptions.toSwallowExceptionRunnable(() -> {
    final var age = ReporterApp.configDatabase.query(MetricQueries::numberOfActiveConnPerWorkspace);
    for (long count : age) {
      DogStatsDMetricSingleton.percentile(MetricsRegistry.NUM_ACTIVE_CONN_PER_WORKSPACE, count);
    }
  })),
  OVERALL_JOB_RUNTIME_IN_LAST_HOUR_BY_TERMINAL_STATE_SECS(Exceptions.toSwallowExceptionRunnable(() -> {
    final var times = ReporterApp.configDatabase.query(MetricQueries::overallJobRuntimeForTerminalJobsInLastHour);
    for (Pair<JobStatus, Double> pair : times) {
      DogStatsDMetricSingleton.recordTimeGlobal(
          MetricsRegistry.OVERALL_JOB_RUNTIME_IN_LAST_HOUR_BY_TERMINAL_STATE_SECS, pair.getRight(), MetricTags.getJobStatus(pair.getLeft()));
    }
  }), 1, TimeUnit.HOURS);

  // default constructor
  final public Runnable emitRunnable;
  final public long period;
  final public TimeUnit timeUnit;

  ToEmit(Runnable toEmit) {
    this(toEmit, 15, TimeUnit.SECONDS);
  }

}
