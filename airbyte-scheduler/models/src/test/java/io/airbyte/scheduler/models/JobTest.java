/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.models;

import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

class JobTest {

  @Test
  void testIsJobInTerminalState() {
    assertFalse(jobWithStatus(JobStatus.PENDING).isJobInTerminalState());
    assertFalse(jobWithStatus(JobStatus.RUNNING).isJobInTerminalState());
    assertFalse(jobWithStatus(JobStatus.INCOMPLETE).isJobInTerminalState());
    assertTrue(jobWithStatus(JobStatus.FAILED).isJobInTerminalState());
    assertTrue(jobWithStatus(JobStatus.SUCCEEDED).isJobInTerminalState());
    assertTrue(jobWithStatus(JobStatus.CANCELLED).isJobInTerminalState());

  }

  private static Job jobWithStatus(JobStatus jobStatus) {
    return new Job(1L, null, null, null, null, jobStatus, 0L, 0L, 0L);
  }

  @Test
  void testHasRunningAttempt() {
    assertTrue(jobWithAttemptWithStatus(AttemptStatus.RUNNING).hasRunningAttempt());
    assertFalse(jobWithAttemptWithStatus(AttemptStatus.FAILED).hasRunningAttempt());
    assertFalse(jobWithAttemptWithStatus(AttemptStatus.SUCCEEDED).hasRunningAttempt());
    assertFalse(jobWithAttemptWithStatus().hasRunningAttempt());
    assertTrue(jobWithAttemptWithStatus(AttemptStatus.SUCCEEDED, AttemptStatus.RUNNING).hasRunningAttempt());
  }

  private static Job jobWithAttemptWithStatus(AttemptStatus... attemptStatuses) {
    final List<Attempt> attempts = Arrays.stream(attemptStatuses)
        .map(attemptStatus -> new Attempt(1L, 1L, null, null, attemptStatus, 0L, 0L, null))
        .collect(Collectors.toList());
    return new Job(1L, null, null, null, attempts, null, 0L, 0L, 0L);
  }

  @Test
  void testGetSuccessfulAttempt() {
    assertTrue(jobWithAttemptWithStatus().getSuccessfulAttempt().isEmpty());
    assertTrue(jobWithAttemptWithStatus(AttemptStatus.FAILED).getSuccessfulAttempt().isEmpty());
    assertThrows(IllegalStateException.class,
        () -> jobWithAttemptWithStatus(AttemptStatus.SUCCEEDED, AttemptStatus.SUCCEEDED).getSuccessfulAttempt());

    final Job job = jobWithAttemptWithStatus(AttemptStatus.FAILED, AttemptStatus.SUCCEEDED);
    assertTrue(job.getSuccessfulAttempt().isPresent());
    assertEquals(job.getAttempts().get(1), job.getSuccessfulAttempt().get());
  }

}
