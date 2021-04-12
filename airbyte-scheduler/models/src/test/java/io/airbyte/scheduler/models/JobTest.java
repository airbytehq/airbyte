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
