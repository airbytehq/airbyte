/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.dataline.scheduler;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.dataline.config.Schedule;
import io.dataline.config.StandardSyncSchedule;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ScheduleJobPredicateTest {

  private static final StandardSyncSchedule SCHEDULE;

  private ScheduleJobPredicate scheduleJobPredicate;
  private Instant now;

  static {
    final Schedule schedule = new Schedule();
    schedule.setTimeUnit(Schedule.TimeUnit.DAYS);
    schedule.setUnits(1L);

    SCHEDULE = new StandardSyncSchedule();
    SCHEDULE.setManual(false);
    SCHEDULE.setSchedule(schedule);
  }

  @SuppressWarnings("unchecked")
  @BeforeEach
  public void setup() {
    Supplier<Instant> timeSupplier = mock(Supplier.class);
    scheduleJobPredicate = new ScheduleJobPredicate(timeSupplier);

    now = Instant.now();
    when(timeSupplier.get()).thenReturn(now);
  }

  private static Optional<Job> generateJobWithStatusAndUpdatedAt(JobStatus status, Instant createdAt) {
    return Optional.of(new Job(
        10L,
        "",
        status,
        null,
        null,
        null,
        null,
        createdAt.toEpochMilli(),
        null,
        createdAt.toEpochMilli()));
  }

  @Test
  public void testManualSchedule() {
    final StandardSyncSchedule standardSyncSchedule = new StandardSyncSchedule();
    standardSyncSchedule.setManual(true);
    assertFalse(scheduleJobPredicate.test(Optional.empty(), standardSyncSchedule));
  }

  @Test
  public void testNoPreviousJob() {
    assertTrue(scheduleJobPredicate.test(Optional.empty(), SCHEDULE));
  }

  @Test
  public void testScheduleReady() {
    final Optional<Job> jobOptionalCompleted = generateJobWithStatusAndUpdatedAt(JobStatus.COMPLETED, now.minus(Duration.ofDays(2)));
    assertTrue(scheduleJobPredicate.test(jobOptionalCompleted, SCHEDULE));

    final Optional<Job> jobOptionalCancelled = generateJobWithStatusAndUpdatedAt(JobStatus.COMPLETED, now.minus(Duration.ofDays(2)));
    assertTrue(scheduleJobPredicate.test(jobOptionalCancelled, SCHEDULE));
  }

  @Test
  public void testScheduleNotReady() {
    final Optional<Job> jobOptional = generateJobWithStatusAndUpdatedAt(JobStatus.COMPLETED, now.minus(Duration.ofDays(1)));
    assertFalse(scheduleJobPredicate.test(jobOptional, SCHEDULE));
  }

  @Test
  public void testScheduleNotReadyPreviousFailed() {
    final Optional<Job> jobOptional = generateJobWithStatusAndUpdatedAt(JobStatus.FAILED, now.minus(Duration.ofDays(1)));
    assertTrue(scheduleJobPredicate.test(jobOptional, SCHEDULE));
  }

  @Test
  public void testScheduleReadyPreviousNotCompleted() {
    final Optional<Job> jobOptionalPending = generateJobWithStatusAndUpdatedAt(JobStatus.PENDING, now.minus(Duration.ofDays(2)));
    assertFalse(scheduleJobPredicate.test(jobOptionalPending, SCHEDULE));

    final Optional<Job> jobOptionalRunning = generateJobWithStatusAndUpdatedAt(JobStatus.RUNNING, now.minus(Duration.ofDays(2)));
    assertFalse(scheduleJobPredicate.test(jobOptionalRunning, SCHEDULE));
  }

}
