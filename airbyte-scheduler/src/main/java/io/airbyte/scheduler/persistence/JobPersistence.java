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

package io.airbyte.scheduler.persistence;

import io.airbyte.config.JobConfig;
import io.airbyte.config.State;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.JobStatus;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface JobPersistence {

  Job getJob(long jobId) throws IOException;

  //
  // JOB LIFECYCLE
  //

  /**
   * Creates a new job. Its initial status will be pending.
   *
   * @param scope key that will be used to determine if two jobs should not be run at the same time.
   * @param jobConfig configuration for the job
   * @return job id
   * @throws IOException exception due to interaction with persistence
   */
  long createJob(String scope, JobConfig jobConfig) throws IOException;

  /**
   * Set job status from current status to PENDING. Throws {@link IllegalStateException} if the job is
   * in a terminal state.
   *
   * @param jobId job to reset
   * @throws IOException exception due to interaction with persistence
   */
  void resetJob(long jobId) throws IOException;

  /**
   * Set job status from current status to CANCELLED. If already in a terminal status, no op.
   *
   * @param jobId job to cancel
   * @param cancellationReason rest that the job is being cancelled.
   * @throws IOException exception due to interaction with persistence
   */
  void cancelJob(long jobId) throws IOException;

  /**
   * Set job status from current status to FAILED. If already in a terminal status, no op.
   *
   * @param jobId job to fail
   * @throws IOException exception due to interaction with persistence
   */
  void failJob(long jobId) throws IOException;

  //
  // ATTEMPT LIFECYCLE
  //

  /**
   * Create a new attempt for a job. Throws {@link IllegalStateException} if the job is already in a
   * terminal state.
   *
   * @param jobId job for which an attempt will be created
   * @param logPath path where logs should be written for the attempt
   * @return id of the attempt
   * @throws IOException exception due to interaction with persistence
   */
  int createAttempt(long jobId, Path logPath) throws IOException;

  /**
   * Sets an attempt to FAILED. Also attempts the parent job to FAILED. The job's status will not be
   * changed if it is already in a terminal state.
   *
   * @param jobId job id
   * @param attemptNumber attempt id
   * @throws IOException exception due to interaction with persistence
   */
  void failAttempt(long jobId, int attemptNumber) throws IOException;

  /**
   * Sets an attempt to SUCCEEDED. Also attempts the parent job to SUCCEEDED. The job's status is
   * changed regardless of what state it is in.
   *
   * @param jobId job id
   * @param attemptNumber attempt id
   * @throws IOException exception due to interaction with persistence
   */
  void succeedAttempt(long jobId, int attemptNumber) throws IOException;

  //
  // END OF LIFECYCLE
  //

  <T> void writeOutput(long jobId, int attemptNumber, T output) throws IOException;

  /**
   * @param configType - type of config, e.g. sync
   * @param configId - id of that config
   * @return lists job in descending order by created_at
   * @throws IOException - what you do when you IO
   */
  List<Job> listJobs(JobConfig.ConfigType configType, String configId) throws IOException;

  List<Job> listJobsWithStatus(JobConfig.ConfigType configType, JobStatus status) throws IOException;

  Optional<Job> getLastSyncJob(UUID connectionId) throws IOException;

  Optional<State> getCurrentState(UUID connectionId) throws IOException;

  Optional<Job> getOldestPendingJob() throws IOException;

}
