/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.app;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.config.Schedule;
import io.airbyte.config.StandardSync;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;
import org.junit.jupiter.params.provider.EnumSource.Mode;

class ScheduleJobPredicateTest {

  private static final StandardSync STANDARD_SYNC = new StandardSync()
      .withManual(false)
      .withSchedule(new Schedule()
          .withTimeUnit(Schedule.TimeUnit.DAYS)
          .withUnits(1L));

  private ScheduleJobPredicate scheduleJobPredicate;
  private Instant now;
  private Job job;

  @SuppressWarnings("unchecked")
  @BeforeEach
  public void setup() {
    Supplier<Instant> timeSupplier = mock(Supplier.class);
    scheduleJobPredicate = new ScheduleJobPredicate(timeSupplier);
    job = mock(Job.class);
    when(job.getId()).thenReturn(10L);
    now = Instant.now();
    when(timeSupplier.get()).thenReturn(now);
  }

  @Test
  public void testManualSchedule() {
    final StandardSync standardSync = new StandardSync().withManual(true);
    assertFalse(scheduleJobPredicate.test(Optional.empty(), standardSync));
  }

  @Test
  public void testNoPreviousJob() {
    assertTrue(scheduleJobPredicate.test(Optional.empty(), STANDARD_SYNC));
  }

  @Test
  public void testScheduleNotReady() {
    when(job.getStatus()).thenReturn(JobStatus.SUCCEEDED);
    when(job.getStartedAtInSecond()).thenReturn(Optional.of(now.minus(Duration.ofDays(1)).getEpochSecond()));

    assertFalse(scheduleJobPredicate.test(Optional.of(job), STANDARD_SYNC));
  }

  // use Mode.EXCLUDE so that when new values are added to the enum, these tests will fail if that
  // value has not also been added to the switch statement.
  @ParameterizedTest
  @EnumSource(value = JobStatus.class,
              mode = Mode.EXCLUDE,
              names = {"PENDING", "RUNNING", "INCOMPLETE"})
  public void testShouldScheduleBasedOnPreviousJobStatus(JobStatus status) {
    when(job.getStatus()).thenReturn(status);
    when(job.getStartedAtInSecond()).thenReturn(Optional.of(now.minus(Duration.ofDays(2)).getEpochSecond()));

    assertTrue(scheduleJobPredicate.test(Optional.of(job), STANDARD_SYNC), "job status: " + status.toString());
  }

  @ParameterizedTest
  @EnumSource(value = JobStatus.class,
              mode = Mode.EXCLUDE,
              names = {"FAILED", "SUCCEEDED", "CANCELLED"})
  public void testScheduleShouldNotScheduleBasedOnPreviousJobStatus(JobStatus status) {
    when(job.getStatus()).thenReturn(status);
    when(job.getStartedAtInSecond()).thenReturn(Optional.of(now.minus(Duration.ofDays(2)).getEpochSecond()));

    assertFalse(scheduleJobPredicate.test(Optional.of(job), STANDARD_SYNC), "job status: " + status.toString());
  }

}
