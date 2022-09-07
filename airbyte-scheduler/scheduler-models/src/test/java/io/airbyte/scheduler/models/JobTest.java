/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.models;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
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

  private static Job jobWithStatus(final JobStatus jobStatus) {
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

  private static Job jobWithAttemptWithStatus(final AttemptStatus... attemptStatuses) {
    final List<Attempt> attempts = IntStream.range(0, attemptStatuses.length)
        .mapToObj(idx -> new Attempt(idx + 1, 1L, null, null, attemptStatuses[idx], null, idx, 0L, null))
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

  @Test
  void testGetLastFailedAttempt() {
    assertTrue(jobWithAttemptWithStatus().getLastFailedAttempt().isEmpty());
    assertTrue(jobWithAttemptWithStatus(AttemptStatus.SUCCEEDED).getLastFailedAttempt().isEmpty());
    assertTrue(jobWithAttemptWithStatus(AttemptStatus.FAILED).getLastFailedAttempt().isPresent());

    final Job job = jobWithAttemptWithStatus(AttemptStatus.FAILED, AttemptStatus.FAILED);
    assertTrue(job.getLastFailedAttempt().isPresent());
    assertEquals(2, job.getLastFailedAttempt().get().getId());
  }

  @Test
  void testValidateStatusTransitionFromPending() {
    final Job pendingJob = jobWithStatus(JobStatus.PENDING);
    assertDoesNotThrow(() -> pendingJob.validateStatusTransition(JobStatus.RUNNING));
    assertDoesNotThrow(() -> pendingJob.validateStatusTransition(JobStatus.FAILED));
    assertDoesNotThrow(() -> pendingJob.validateStatusTransition(JobStatus.CANCELLED));
    assertThrows(IllegalStateException.class, () -> pendingJob.validateStatusTransition(JobStatus.INCOMPLETE));
    assertThrows(IllegalStateException.class, () -> pendingJob.validateStatusTransition(JobStatus.SUCCEEDED));
  }

  @Test
  void testValidateStatusTransitionFromRunning() {
    final Job runningJob = jobWithStatus(JobStatus.RUNNING);
    assertDoesNotThrow(() -> runningJob.validateStatusTransition(JobStatus.INCOMPLETE));
    assertDoesNotThrow(() -> runningJob.validateStatusTransition(JobStatus.SUCCEEDED));
    assertDoesNotThrow(() -> runningJob.validateStatusTransition(JobStatus.FAILED));
    assertDoesNotThrow(() -> runningJob.validateStatusTransition(JobStatus.CANCELLED));
    assertThrows(IllegalStateException.class, () -> runningJob.validateStatusTransition(JobStatus.PENDING));
  }

  @Test
  void testValidateStatusTransitionFromIncomplete() {
    final Job incompleteJob = jobWithStatus(JobStatus.INCOMPLETE);
    assertDoesNotThrow(() -> incompleteJob.validateStatusTransition(JobStatus.PENDING));
    assertDoesNotThrow(() -> incompleteJob.validateStatusTransition(JobStatus.RUNNING));
    assertDoesNotThrow(() -> incompleteJob.validateStatusTransition(JobStatus.FAILED));
    assertDoesNotThrow(() -> incompleteJob.validateStatusTransition(JobStatus.CANCELLED));
    assertThrows(IllegalStateException.class, () -> incompleteJob.validateStatusTransition(JobStatus.SUCCEEDED));
  }

  @Test
  void testValidateStatusTransitionFromSucceeded() {
    final Job suceededJob = jobWithStatus(JobStatus.SUCCEEDED);
    assertThrows(IllegalStateException.class, () -> suceededJob.validateStatusTransition(JobStatus.PENDING));
    assertThrows(IllegalStateException.class, () -> suceededJob.validateStatusTransition(JobStatus.RUNNING));
    assertThrows(IllegalStateException.class, () -> suceededJob.validateStatusTransition(JobStatus.INCOMPLETE));
    assertThrows(IllegalStateException.class, () -> suceededJob.validateStatusTransition(JobStatus.FAILED));
    assertThrows(IllegalStateException.class, () -> suceededJob.validateStatusTransition(JobStatus.CANCELLED));
  }

  @Test
  void testValidateStatusTransitionFromFailed() {
    final Job failedJob = jobWithStatus(JobStatus.FAILED);
    assertThrows(IllegalStateException.class, () -> failedJob.validateStatusTransition(JobStatus.SUCCEEDED));
    assertThrows(IllegalStateException.class, () -> failedJob.validateStatusTransition(JobStatus.PENDING));
    assertThrows(IllegalStateException.class, () -> failedJob.validateStatusTransition(JobStatus.RUNNING));
    assertThrows(IllegalStateException.class, () -> failedJob.validateStatusTransition(JobStatus.INCOMPLETE));
    assertThrows(IllegalStateException.class, () -> failedJob.validateStatusTransition(JobStatus.CANCELLED));
  }

  @Test
  void testValidateStatusTransitionFromCancelled() {
    final Job cancelledJob = jobWithStatus(JobStatus.CANCELLED);
    assertThrows(IllegalStateException.class, () -> cancelledJob.validateStatusTransition(JobStatus.SUCCEEDED));
    assertThrows(IllegalStateException.class, () -> cancelledJob.validateStatusTransition(JobStatus.PENDING));
    assertThrows(IllegalStateException.class, () -> cancelledJob.validateStatusTransition(JobStatus.RUNNING));
    assertThrows(IllegalStateException.class, () -> cancelledJob.validateStatusTransition(JobStatus.INCOMPLETE));
    assertThrows(IllegalStateException.class, () -> cancelledJob.validateStatusTransition(JobStatus.CANCELLED));
  }

}
