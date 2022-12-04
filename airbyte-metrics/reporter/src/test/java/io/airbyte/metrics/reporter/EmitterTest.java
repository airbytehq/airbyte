/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.reporter;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.db.instance.jobs.jooq.generated.enums.JobStatus;
import io.airbyte.metrics.lib.MetricAttribute;
import io.airbyte.metrics.lib.MetricClient;
import io.airbyte.metrics.lib.MetricTags;
import io.airbyte.metrics.lib.OssMetricsRegistry;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class EmitterTest {

  private MetricClient client;
  private MetricRepository repo;

  private static final String SYNC_QUEUE = "SYNC";
  private static final String AWS_QUEUE = "AWS";

  private static final String EU_REGION = "EU";
  private static final String AUTO_REGION = "AUTO";

  @BeforeEach
  void setUp() {
    client = mock(MetricClient.class);
    repo = mock(MetricRepository.class);
  }

  @Test
  void TestNumPendingJobs() {
    final var value = Map.of(AUTO_REGION, 101, EU_REGION, 20);
    when(repo.numberOfPendingJobsByGeography()).thenReturn(value);

    final var emitter = new NumPendingJobs(client, repo);
    emitter.Emit();

    assertEquals(Duration.ofSeconds(15), emitter.getDuration());
    verify(repo).numberOfPendingJobsByGeography();
    verify(client).gauge(OssMetricsRegistry.NUM_PENDING_JOBS, 101,
        new MetricAttribute(MetricTags.GEOGRAPHY, AUTO_REGION));
    verify(client).gauge(OssMetricsRegistry.NUM_PENDING_JOBS, 20,
        new MetricAttribute(MetricTags.GEOGRAPHY, EU_REGION));
    verify(client).count(OssMetricsRegistry.EST_NUM_METRICS_EMITTED_BY_REPORTER, 1);
  }

  @Test
  void TestNumRunningJobs() {
    final var value = Map.of(SYNC_QUEUE, 101, AWS_QUEUE, 20);
    when(repo.numberOfRunningJobsByTaskQueue()).thenReturn(value);

    final var emitter = new NumRunningJobs(client, repo);
    emitter.Emit();

    assertEquals(Duration.ofSeconds(15), emitter.getDuration());
    verify(repo).numberOfRunningJobsByTaskQueue();
    verify(client).gauge(OssMetricsRegistry.NUM_RUNNING_JOBS, 101,
        new MetricAttribute(MetricTags.ATTEMPT_QUEUE, SYNC_QUEUE));
    verify(client).gauge(OssMetricsRegistry.NUM_RUNNING_JOBS, 20,
        new MetricAttribute(MetricTags.ATTEMPT_QUEUE, AWS_QUEUE));
    verify(client).count(OssMetricsRegistry.EST_NUM_METRICS_EMITTED_BY_REPORTER, 1);
  }

  @Test
  void TestNumOrphanRunningJobs() {
    final var value = 101;
    when(repo.numberOfOrphanRunningJobs()).thenReturn(value);

    final var emitter = new NumOrphanRunningJobs(client, repo);
    emitter.Emit();

    assertEquals(Duration.ofSeconds(15), emitter.getDuration());
    verify(repo).numberOfOrphanRunningJobs();
    verify(client).gauge(OssMetricsRegistry.NUM_ORPHAN_RUNNING_JOBS, value);
    verify(client).count(OssMetricsRegistry.EST_NUM_METRICS_EMITTED_BY_REPORTER, 1);
  }

  @Test
  void TestOldestRunningJob() {
    final var value = Map.of(SYNC_QUEUE, 101.0, AWS_QUEUE, 20.0);
    when(repo.oldestRunningJobAgeSecsByTaskQueue()).thenReturn(value);

    final var emitter = new OldestRunningJob(client, repo);
    emitter.Emit();

    assertEquals(Duration.ofSeconds(15), emitter.getDuration());
    verify(repo).oldestRunningJobAgeSecsByTaskQueue();
    verify(client).gauge(OssMetricsRegistry.OLDEST_RUNNING_JOB_AGE_SECS, 101,
        new MetricAttribute(MetricTags.ATTEMPT_QUEUE, SYNC_QUEUE));
    verify(client).gauge(OssMetricsRegistry.OLDEST_RUNNING_JOB_AGE_SECS, 20,
        new MetricAttribute(MetricTags.ATTEMPT_QUEUE, AWS_QUEUE));
    verify(client).count(OssMetricsRegistry.EST_NUM_METRICS_EMITTED_BY_REPORTER, 1);
  }

  @Test
  void TestOldestPendingJob() {
    final var value = Map.of(AUTO_REGION, 101.0, EU_REGION, 20.0);
    when(repo.oldestPendingJobAgeSecsByGeography()).thenReturn(value);

    final var emitter = new OldestPendingJob(client, repo);
    emitter.Emit();

    assertEquals(Duration.ofSeconds(15), emitter.getDuration());
    verify(repo).oldestPendingJobAgeSecsByGeography();
    verify(client).gauge(OssMetricsRegistry.OLDEST_PENDING_JOB_AGE_SECS, 101,
        new MetricAttribute(MetricTags.GEOGRAPHY, AUTO_REGION));
    verify(client).gauge(OssMetricsRegistry.OLDEST_PENDING_JOB_AGE_SECS, 20,
        new MetricAttribute(MetricTags.GEOGRAPHY, EU_REGION));

    verify(client).count(OssMetricsRegistry.EST_NUM_METRICS_EMITTED_BY_REPORTER, 1);
  }

  @Test
  void TestNumActiveConnectionsPerWorkspace() {
    final var values = List.of(101L, 202L);
    when(repo.numberOfActiveConnPerWorkspace()).thenReturn(values);

    final var emitter = new NumActiveConnectionsPerWorkspace(client, repo);
    emitter.Emit();

    assertEquals(Duration.ofSeconds(15), emitter.getDuration());
    verify(repo).numberOfActiveConnPerWorkspace();
    for (final var value : values) {
      verify(client).distribution(OssMetricsRegistry.NUM_ACTIVE_CONN_PER_WORKSPACE, value);
    }
    verify(client).count(OssMetricsRegistry.EST_NUM_METRICS_EMITTED_BY_REPORTER, 1);
  }

  @Test
  void TestNumAbnormalScheduledSyncs() {
    final var value = 101;
    when(repo.numberOfJobsNotRunningOnScheduleInLastDay()).thenReturn((long) value);

    final var emitter = new NumAbnormalScheduledSyncs(client, repo);
    emitter.Emit();

    assertEquals(Duration.ofHours(1), emitter.getDuration());
    verify(repo).numberOfJobsNotRunningOnScheduleInLastDay();
    verify(client).gauge(OssMetricsRegistry.NUM_ABNORMAL_SCHEDULED_SYNCS_IN_LAST_DAY, value);
    verify(client).count(OssMetricsRegistry.EST_NUM_METRICS_EMITTED_BY_REPORTER, 1);
  }

  @Test
  void TestTotalScheduledSyncs() {
    final var value = 101;
    when(repo.numScheduledActiveConnectionsInLastDay()).thenReturn((long) value);

    final var emitter = new TotalScheduledSyncs(client, repo);
    emitter.Emit();

    assertEquals(Duration.ofHours(1), emitter.getDuration());
    verify(repo).numScheduledActiveConnectionsInLastDay();
    verify(client).gauge(OssMetricsRegistry.NUM_TOTAL_SCHEDULED_SYNCS_IN_LAST_DAY, value);
    verify(client).count(OssMetricsRegistry.EST_NUM_METRICS_EMITTED_BY_REPORTER, 1);
  }

  @Test
  void TestTotalJobRuntimeByTerminalState() {
    final var values = Map.of(JobStatus.cancelled, 101.0, JobStatus.succeeded, 202.0,
        JobStatus.failed, 303.0);
    when(repo.overallJobRuntimeForTerminalJobsInLastHour()).thenReturn(values);

    final var emitter = new TotalJobRuntimeByTerminalState(client, repo);
    emitter.Emit();

    assertEquals(Duration.ofHours(1), emitter.getDuration());
    verify(repo).overallJobRuntimeForTerminalJobsInLastHour();
    values.forEach((jobStatus, time) -> {
      verify(client).distribution(
          OssMetricsRegistry.OVERALL_JOB_RUNTIME_IN_LAST_HOUR_BY_TERMINAL_STATE_SECS, time,
          new MetricAttribute(MetricTags.JOB_STATUS, jobStatus.getLiteral()));
    });
    verify(client).count(OssMetricsRegistry.EST_NUM_METRICS_EMITTED_BY_REPORTER, 1);
  }

}
