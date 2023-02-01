/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import io.airbyte.metrics.lib.MetricAttribute;
import io.airbyte.metrics.lib.MetricClient;
import io.airbyte.metrics.lib.MetricTags;
import io.airbyte.metrics.lib.OssMetricsRegistry;
import jakarta.inject.Singleton;
import java.lang.invoke.MethodHandles;
import java.time.Duration;
import java.util.concurrent.Callable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Singleton
final class NumPendingJobs extends Emitter {

  public NumPendingJobs(final MetricClient client, final MetricRepository db) {
    super(client, () -> {
      db.numberOfPendingJobsByGeography().forEach((geography, count) -> client.gauge(
          OssMetricsRegistry.NUM_PENDING_JOBS,
          count,
          new MetricAttribute(MetricTags.GEOGRAPHY, geography)));

      return null;
    });
  }

}

@Singleton
final class NumRunningJobs extends Emitter {

  public NumRunningJobs(final MetricClient client, final MetricRepository db) {
    super(client, () -> {
      db.numberOfRunningJobsByTaskQueue().forEach((attemptQueue, count) -> client.gauge(
          OssMetricsRegistry.NUM_RUNNING_JOBS,
          count,
          new MetricAttribute(MetricTags.ATTEMPT_QUEUE, attemptQueue)));
      return null;
    });
  }

}

@Singleton
final class NumOrphanRunningJobs extends Emitter {

  NumOrphanRunningJobs(final MetricClient client, final MetricRepository db) {
    super(client, () -> {
      final var orphaned = db.numberOfOrphanRunningJobs();
      client.gauge(OssMetricsRegistry.NUM_ORPHAN_RUNNING_JOBS, orphaned);
      return null;
    });
  }

}

@Singleton
final class OldestRunningJob extends Emitter {

  OldestRunningJob(final MetricClient client, final MetricRepository db) {
    super(client, () -> {
      db.oldestRunningJobAgeSecsByTaskQueue().forEach((attemptQueue, count) -> client.gauge(
          OssMetricsRegistry.OLDEST_RUNNING_JOB_AGE_SECS,
          count,
          new MetricAttribute(MetricTags.ATTEMPT_QUEUE, attemptQueue)));
      return null;
    });
  }

}

@Singleton
final class OldestPendingJob extends Emitter {

  OldestPendingJob(final MetricClient client, final MetricRepository db) {
    super(client, () -> {
      db.oldestPendingJobAgeSecsByGeography().forEach((geographyType, count) -> client.gauge(
          OssMetricsRegistry.OLDEST_PENDING_JOB_AGE_SECS,
          count,
          new MetricAttribute(MetricTags.GEOGRAPHY, geographyType)));
      return null;
    });
  }

}

@Singleton
final class NumActiveConnectionsPerWorkspace extends Emitter {

  NumActiveConnectionsPerWorkspace(final MetricClient client, final MetricRepository db) {
    super(client, () -> {
      final var workspaceConns = db.numberOfActiveConnPerWorkspace();
      for (final long numCons : workspaceConns) {
        client.distribution(OssMetricsRegistry.NUM_ACTIVE_CONN_PER_WORKSPACE, numCons);
      }
      return null;
    });
  }

}

@Singleton
final class NumAbnormalScheduledSyncs extends Emitter {

  NumAbnormalScheduledSyncs(final MetricClient client, final MetricRepository db) {
    super(client, () -> {
      final var count = db.numberOfJobsNotRunningOnScheduleInLastDay();
      client.gauge(OssMetricsRegistry.NUM_ABNORMAL_SCHEDULED_SYNCS_IN_LAST_DAY, count);
      return null;
    });
  }

  @Override
  public Duration getDuration() {
    return Duration.ofHours(1);
  }

}

@Singleton
final class NumUnusuallyLongSyncs extends Emitter {

  NumUnusuallyLongSyncs(final MetricClient client, final MetricRepository db) {
    super(client, () -> {
      final var count = db.numberOfJobsRunningUnusuallyLong();
      client.gauge(OssMetricsRegistry.NUM_UNUSUALLY_LONG_SYNCS, count);
      return null;
    });
  }

  @Override
  public Duration getDuration() {
    return Duration.ofMinutes(15);
  }

}

@Singleton
final class TotalScheduledSyncs extends Emitter {

  TotalScheduledSyncs(final MetricClient client, final MetricRepository db) {
    super(client, () -> {
      final var count = db.numScheduledActiveConnectionsInLastDay();
      client.gauge(OssMetricsRegistry.NUM_TOTAL_SCHEDULED_SYNCS_IN_LAST_DAY, count);
      return null;
    });
  }

  @Override
  public Duration getDuration() {
    return Duration.ofHours(1);
  }

}

@Singleton
final class TotalJobRuntimeByTerminalState extends Emitter {

  public TotalJobRuntimeByTerminalState(final MetricClient client, final MetricRepository db) {
    super(client, () -> {
      db.overallJobRuntimeForTerminalJobsInLastHour()
          .forEach((jobStatus, time) -> client.distribution(
              OssMetricsRegistry.OVERALL_JOB_RUNTIME_IN_LAST_HOUR_BY_TERMINAL_STATE_SECS,
              time,
              new MetricAttribute(MetricTags.JOB_STATUS, jobStatus.getLiteral())));
      return null;
    });
  }

  @Override
  public Duration getDuration() {
    return Duration.ofHours(1);
  }

}

/**
 * Abstract base class for all emitted metrics.
 * <p>
 * As this is a sealed class, all implementations of it are contained within this same file.
 */
sealed class Emitter {

  protected static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());
  protected final MetricClient client;
  protected final Callable<Void> callable;

  Emitter(final MetricClient client, final Callable<Void> callable) {
    this.client = client;
    this.callable = callable;
  }

  /**
   * Emit the metrics by calling the callable.
   * <p>
   * Any exception thrown by the callable will be logged.
   *
   * @TODO: replace log message with a published error-event of some kind.
   */
  public void Emit() {
    try {
      callable.call();
      client.count(OssMetricsRegistry.EST_NUM_METRICS_EMITTED_BY_REPORTER, 1);
    } catch (final Exception e) {
      log.error("Exception querying database for metric: ", e);
    }
  }

  /**
   * How often this metric should report, defaults to 15s if not overwritten.
   *
   * @return Duration of how often this metric should report.
   */
  public Duration getDuration() {
    return Duration.ofSeconds(15);
  }

}
