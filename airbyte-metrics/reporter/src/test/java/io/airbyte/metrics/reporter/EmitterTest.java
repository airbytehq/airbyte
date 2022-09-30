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

  @BeforeEach
  void setUp() {
    client = mock(MetricClient.class);
    repo = mock(MetricRepository.class);
  }

  @Test
  void TestNumPendingJobs() {
    final var value = 101;
    when(repo.numberOfPendingJobs()).thenReturn(value);

    final var emitter = new NumPendingJobs(client, repo);
    emitter.Emit();

    assertEquals(Duration.ofSeconds(15), emitter.getDuration());
    verify(repo).numberOfPendingJobs();
    verify(client).gauge(OssMetricsRegistry.NUM_PENDING_JOBS, value);
  }

  @Test
  void TestNumRunningJobs() {
    final var value = 101;
    when(repo.numberOfRunningJobs()).thenReturn(value);

    final var emitter = new NumRunningJobs(client, repo);
    emitter.Emit();

    assertEquals(Duration.ofSeconds(15), emitter.getDuration());
    verify(repo).numberOfRunningJobs();
    verify(client).gauge(OssMetricsRegistry.NUM_RUNNING_JOBS, value);
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
  }

  @Test
  void TestOldestRunningJob() {
    final var value = 101;
    when(repo.oldestRunningJobAgeSecs()).thenReturn((long) value);

    final var emitter = new OldestRunningJob(client, repo);
    emitter.Emit();

    assertEquals(Duration.ofSeconds(15), emitter.getDuration());
    verify(repo).oldestRunningJobAgeSecs();
    verify(client).gauge(OssMetricsRegistry.OLDEST_RUNNING_JOB_AGE_SECS, value);
  }

  @Test
  void TestOldestPendingJob() {
    final var value = 101;
    when(repo.oldestPendingJobAgeSecs()).thenReturn((long) value);

    final var emitter = new OldestPendingJob(client, repo);
    emitter.Emit();

    assertEquals(Duration.ofSeconds(15), emitter.getDuration());
    verify(repo).oldestPendingJobAgeSecs();
    verify(client).gauge(OssMetricsRegistry.OLDEST_PENDING_JOB_AGE_SECS, value);
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
  }

  @Test
  void TestTotalJobRuntimeByTerminalState() {
    final var values = Map.of(JobStatus.cancelled, 101.0, JobStatus.succeeded, 202.0, JobStatus.failed, 303.0);
    when(repo.overallJobRuntimeForTerminalJobsInLastHour()).thenReturn(values);

    final var emitter = new TotalJobRuntimeByTerminalState(client, repo);
    emitter.Emit();

    assertEquals(Duration.ofHours(1), emitter.getDuration());
    verify(repo).overallJobRuntimeForTerminalJobsInLastHour();
    values.forEach((jobStatus, time) -> {
      verify(client).distribution(OssMetricsRegistry.OVERALL_JOB_RUNTIME_IN_LAST_HOUR_BY_TERMINAL_STATE_SECS, time,
          new MetricAttribute(MetricTags.JOB_STATUS, jobStatus.getLiteral()));
    });
  }

}
