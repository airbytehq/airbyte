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
    super(() -> {
      final var pending = db.numberOfPendingJobs();
      client.gauge(OssMetricsRegistry.NUM_PENDING_JOBS, pending);
      return null;
    });
  }

}

@Singleton
final class NumRunningJobs extends Emitter {

  public NumRunningJobs(final MetricClient client, final MetricRepository db) {
    super(() -> {
      final var running = db.numberOfRunningJobs();
      client.gauge(OssMetricsRegistry.NUM_RUNNING_JOBS, running);
      return null;
    });
  }

}

@Singleton
final class NumOrphanRunningJobs extends Emitter {

  NumOrphanRunningJobs(final MetricClient client, final MetricRepository db) {
    super(() -> {
      final var orphaned = db.numberOfOrphanRunningJobs();
      client.gauge(OssMetricsRegistry.NUM_ORPHAN_RUNNING_JOBS, orphaned);
      return null;
    });
  }

}

@Singleton
final class OldestRunningJob extends Emitter {

  OldestRunningJob(final MetricClient client, final MetricRepository db) {
    super(() -> {
      final var age = db.oldestRunningJobAgeSecs();
      client.gauge(OssMetricsRegistry.OLDEST_RUNNING_JOB_AGE_SECS, age);
      return null;
    });
  }

}

@Singleton
final class OldestPendingJob extends Emitter {

  OldestPendingJob(final MetricClient client, final MetricRepository db) {
    super(() -> {
      final var age = db.oldestPendingJobAgeSecs();
      client.gauge(OssMetricsRegistry.OLDEST_PENDING_JOB_AGE_SECS, age);
      return null;
    });
  }

}

@Singleton
final class NumActiveConnectionsPerWorkspace extends Emitter {

  NumActiveConnectionsPerWorkspace(final MetricClient client, final MetricRepository db) {
    super(() -> {
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
    super(() -> {
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
final class TotalScheduledSyncs extends Emitter {

  TotalScheduledSyncs(final MetricClient client, final MetricRepository db) {
    super(() -> {
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
    super(() -> {
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
  protected final Callable<Void> callable;

  Emitter(final Callable<Void> callable) {
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
