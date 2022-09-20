/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import io.airbyte.commons.lang.Exceptions.Procedure;
import io.airbyte.db.instance.jobs.jooq.generated.enums.JobStatus;
import io.airbyte.metrics.lib.MetricAttribute;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.airbyte.metrics.lib.MetricQueries;
import io.airbyte.metrics.lib.MetricTags;
import io.airbyte.metrics.lib.OssMetricsRegistry;
import java.util.concurrent.TimeUnit;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.tuple.Pair;

/**
 * This class contains all metrics emitted by the {@link ReporterApp}.
 */
@Slf4j
@AllArgsConstructor
public enum ToEmit {

  NUM_PENDING_JOBS(countMetricEmission(() -> {
    final var pendingJobs = ReporterApp.configDatabase.query(MetricQueries::numberOfPendingJobs);
    MetricClientFactory.getMetricClient().gauge(OssMetricsRegistry.NUM_PENDING_JOBS, pendingJobs);
  })),
  NUM_RUNNING_JOBS(countMetricEmission(() -> {
    final var runningJobs = ReporterApp.configDatabase.query(MetricQueries::numberOfRunningJobs);
    MetricClientFactory.getMetricClient().gauge(OssMetricsRegistry.NUM_RUNNING_JOBS, runningJobs);
  })),
  NUM_ORPHAN_RUNNING_JOB(countMetricEmission(() -> {
    final var orphanRunningJobs = ReporterApp.configDatabase.query(MetricQueries::numberOfOrphanRunningJobs);
    MetricClientFactory.getMetricClient().gauge(OssMetricsRegistry.NUM_ORPHAN_RUNNING_JOBS, orphanRunningJobs);
  })),
  OLDEST_RUNNING_JOB_AGE_SECS(countMetricEmission(() -> {
    final var age = ReporterApp.configDatabase.query(MetricQueries::oldestRunningJobAgeSecs);
    MetricClientFactory.getMetricClient().gauge(OssMetricsRegistry.OLDEST_RUNNING_JOB_AGE_SECS, age);
  })),
  OLDEST_PENDING_JOB_AGE_SECS(countMetricEmission(() -> {
    final var age = ReporterApp.configDatabase.query(MetricQueries::oldestPendingJobAgeSecs);
    MetricClientFactory.getMetricClient().gauge(OssMetricsRegistry.OLDEST_PENDING_JOB_AGE_SECS, age);
  })),
  NUM_ACTIVE_CONN_PER_WORKSPACE(countMetricEmission(() -> {
    final var age = ReporterApp.configDatabase.query(MetricQueries::numberOfActiveConnPerWorkspace);
    for (long count : age) {
      MetricClientFactory.getMetricClient().distribution(OssMetricsRegistry.NUM_ACTIVE_CONN_PER_WORKSPACE, count);
    }
  })),
  NUM_ABNORMAL_SCHEDULED_SYNCS_LAST_DAY(countMetricEmission(() -> {
    final var count = ReporterApp.configDatabase.query(MetricQueries::numberOfJobsNotRunningOnScheduleInLastDay);
    MetricClientFactory.getMetricClient().gauge(OssMetricsRegistry.NUM_ABNORMAL_SCHEDULED_SYNCS_IN_LAST_DAY, count);
  }), 1, TimeUnit.HOURS),
  NUM_TOTAL_SCHEDULED_SYNCS_LAST_DAY(countMetricEmission(() -> {
    final var count = ReporterApp.configDatabase.query(MetricQueries::numScheduledActiveConnectionsInLastDay);
    MetricClientFactory.getMetricClient().gauge(OssMetricsRegistry.NUM_TOTAL_SCHEDULED_SYNCS_IN_LAST_DAY, count);
  }), 1, TimeUnit.HOURS),
  OVERALL_JOB_RUNTIME_IN_LAST_HOUR_BY_TERMINAL_STATE_SECS(countMetricEmission(() -> {
    final var times = ReporterApp.configDatabase.query(MetricQueries::overallJobRuntimeForTerminalJobsInLastHour);
    for (Pair<JobStatus, Double> pair : times) {
      MetricClientFactory.getMetricClient().distribution(
          OssMetricsRegistry.OVERALL_JOB_RUNTIME_IN_LAST_HOUR_BY_TERMINAL_STATE_SECS, pair.getRight(),
          new MetricAttribute(MetricTags.JOB_STATUS, MetricTags.getJobStatus(pair.getLeft())));
    }
  }), 1, TimeUnit.HOURS);

  // default constructor
  final public Runnable emitRunnable;
  final public long period;
  final public TimeUnit timeUnit;

  ToEmit(final Runnable toEmit) {
    this(toEmit, 15, TimeUnit.SECONDS);
  }

  /**
   * Wrapper callable to handle 1) query exception logging and 2) counting metric emissions so
   * reporter app can be monitored too.
   *
   * @param metricQuery
   * @return
   */
  private static Runnable countMetricEmission(final Procedure metricQuery) {
    return () -> {
      try {
        metricQuery.call();
        MetricClientFactory.getMetricClient().count(OssMetricsRegistry.EST_NUM_METRICS_EMITTED_BY_REPORTER, 1);
      } catch (final Exception e) {
        log.error("Exception querying database for metric: ", e);
      }
    };
  }

}
