/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
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

package io.airbyte.scheduler;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.config.Schedule;
import io.airbyte.config.StandardSyncSchedule;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.EnumSource;

class ScheduleJobPredicateTest {

  private static final StandardSyncSchedule SCHEDULE = new StandardSyncSchedule()
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
    final StandardSyncSchedule standardSyncSchedule = new StandardSyncSchedule().withManual(true);
    assertFalse(scheduleJobPredicate.test(Optional.empty(), standardSyncSchedule));
  }

  @Test
  public void testNoPreviousJob() {
    assertTrue(scheduleJobPredicate.test(Optional.empty(), SCHEDULE));
  }

  @Test
  public void testScheduleNotReady() {
    when(job.getStatus()).thenReturn(JobStatus.SUCCEEDED);
    when(job.getUpdatedAtInSecond()).thenReturn(now.minus(Duration.ofDays(1)).getEpochSecond());

    assertFalse(scheduleJobPredicate.test(Optional.of(job), SCHEDULE));
  }

  @ParameterizedTest
  @EnumSource(value = JobStatus.class,
              names = {"SUCCEEDED", "CANCELLED"})
  public void testShouldScheduleBasedOnPreviousJobStatus(JobStatus status) {
    when(job.getStatus()).thenReturn(status);
    when(job.getUpdatedAtInSecond()).thenReturn(now.minus(Duration.ofDays(2)).getEpochSecond());

    assertTrue(scheduleJobPredicate.test(Optional.of(job), SCHEDULE));
  }

  @ParameterizedTest
  @EnumSource(value = JobStatus.class,
              names = {"FAILED", "PENDING", "RUNNING"})
  public void testScheduleShouldNotScheduleBasedOnPreviousJobStatus(JobStatus status) {
    when(job.getStatus()).thenReturn(status);
    when(job.getUpdatedAtInSecond()).thenReturn(now.minus(Duration.ofDays(1)).getEpochSecond());

    assertFalse(scheduleJobPredicate.test(Optional.of(job), SCHEDULE));
  }

}
