/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import io.airbyte.db.instance.jobs.jooq.generated.enums.JobStatus;
import io.airbyte.metrics.lib.MetricAttribute;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.airbyte.metrics.lib.MetricQueries;
import io.airbyte.metrics.lib.MetricTags;
import io.airbyte.metrics.lib.OssMetricsRegistry;
import java.lang.invoke.MethodHandles;
import java.time.Duration;
import java.util.concurrent.Callable;
import org.apache.commons.lang3.tuple.Pair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class contains all metrics emitted by the {@link ReporterApp}.
 */
public enum ToEmit {

  NUM_PENDING_JOBS(countMetricEmission(() -> {
    final var pendingJobs = ReporterApp.configDatabase.query(MetricQueries::numberOfPendingJobs);
    MetricClientFactory.getMetricClient().gauge(OssMetricsRegistry.NUM_PENDING_JOBS, pendingJobs);
    return null;
  })),
  NUM_RUNNING_JOBS(countMetricEmission(() -> {
    final var runningJobs = ReporterApp.configDatabase.query(MetricQueries::numberOfRunningJobs);
    MetricClientFactory.getMetricClient().gauge(OssMetricsRegistry.NUM_RUNNING_JOBS, runningJobs);
    return null;
  })),
  NUM_ORPHAN_RUNNING_JOB(countMetricEmission(() -> {
    final var orphanRunningJobs = ReporterApp.configDatabase.query(MetricQueries::numberOfOrphanRunningJobs);
    MetricClientFactory.getMetricClient().gauge(OssMetricsRegistry.NUM_ORPHAN_RUNNING_JOBS, orphanRunningJobs);
    return null;
  })),
  OLDEST_RUNNING_JOB_AGE_SECS(countMetricEmission(() -> {
    final var age = ReporterApp.configDatabase.query(MetricQueries::oldestRunningJobAgeSecs);
    MetricClientFactory.getMetricClient().gauge(OssMetricsRegistry.OLDEST_RUNNING_JOB_AGE_SECS, age);
    return null;
  })),
  OLDEST_PENDING_JOB_AGE_SECS(countMetricEmission(() -> {
    final var age = ReporterApp.configDatabase.query(MetricQueries::oldestPendingJobAgeSecs);
    MetricClientFactory.getMetricClient().gauge(OssMetricsRegistry.OLDEST_PENDING_JOB_AGE_SECS, age);
    return null;
  })),
  NUM_ACTIVE_CONN_PER_WORKSPACE(countMetricEmission(() -> {
    final var age = ReporterApp.configDatabase.query(MetricQueries::numberOfActiveConnPerWorkspace);
    for (final long count : age) {
      MetricClientFactory.getMetricClient().distribution(OssMetricsRegistry.NUM_ACTIVE_CONN_PER_WORKSPACE, count);
    }
    return null;
  })),
  NUM_ABNORMAL_SCHEDULED_SYNCS_LAST_DAY(Duration.ofHours(1), countMetricEmission(() -> {
    final var count = ReporterApp.configDatabase.query(MetricQueries::numberOfJobsNotRunningOnScheduleInLastDay);
    MetricClientFactory.getMetricClient().gauge(OssMetricsRegistry.NUM_ABNORMAL_SCHEDULED_SYNCS_IN_LAST_DAY, count);
    return null;
  })),
  NUM_TOTAL_SCHEDULED_SYNCS_LAST_DAY(Duration.ofHours(1), countMetricEmission(() -> {
    final var count = ReporterApp.configDatabase.query(MetricQueries::numScheduledActiveConnectionsInLastDay);
    MetricClientFactory.getMetricClient().gauge(OssMetricsRegistry.NUM_TOTAL_SCHEDULED_SYNCS_IN_LAST_DAY, count);
    return null;
  })),
  OVERALL_JOB_RUNTIME_IN_LAST_HOUR_BY_TERMINAL_STATE_SECS(Duration.ofHours(1), countMetricEmission(() -> {
    final var times = ReporterApp.configDatabase.query(MetricQueries::overallJobRuntimeForTerminalJobsInLastHour);
    for (final Pair<JobStatus, Double> pair : times) {
      MetricClientFactory.getMetricClient().distribution(
          OssMetricsRegistry.OVERALL_JOB_RUNTIME_IN_LAST_HOUR_BY_TERMINAL_STATE_SECS, pair.getRight(),
          new MetricAttribute(MetricTags.JOB_STATUS, MetricTags.getJobStatus(pair.getLeft())));
    }
    return null;
  }));

  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());

  // default constructor
  /** A runnable that emits a metric. */
  final public Runnable emit;
  /** How often this metric would emit data. */
  final public Duration duration;

  ToEmit(final Runnable emit) {
    this(Duration.ofSeconds(15), emit);
  }

  ToEmit(final Duration duration, final Runnable emit) {
    this.duration = duration;
    this.emit = emit;
  }

  /**
   * Wrapper callable to handle 1) query exception logging and 2) counting metric emissions so
   * reporter app can be monitored too.
   *
   * @param metricQuery
   * @return
   */
  private static Runnable countMetricEmission(final Callable<Void> metricQuery) {
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
