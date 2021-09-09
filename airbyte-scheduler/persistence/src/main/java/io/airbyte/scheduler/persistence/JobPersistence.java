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

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.JobConfig;
import io.airbyte.config.State;
import io.airbyte.db.instance.jobs.JobsDatabaseSchema;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Stream;

/**
 * TODO Introduce a locking mechanism so that no DB operation is allowed when automatic migration is
 * running
 */
public interface JobPersistence {

  Job getJob(long jobId) throws IOException;

  //
  // JOB LIFECYCLE
  //

  /**
   * Enqueue a new job. Its initial status will be pending.
   *
   * @param scope key that will be used to determine if two jobs should not be run at the same time.
   * @param jobConfig configuration for the job
   * @return job id
   * @throws IOException exception due to interaction with persistence
   */
  Optional<Long> enqueueJob(String scope, JobConfig jobConfig) throws IOException;

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

  /**
   * Sets an attempt's temporal workflow id. Later used to cancel the workflow.
   */
  void setAttemptTemporalWorkflowId(long jobId, int attemptNumber, String temporalWorkflowId) throws IOException;

  /**
   * Retrieves an attempt's temporal workflow id. Used to cancel the workflow.
   */
  Optional<String> getAttemptTemporalWorkflowId(long jobId, int attemptNumber) throws IOException;

  <T> void writeOutput(long jobId, int attemptNumber, T output) throws IOException;

  /**
   * @param configType - type of config, e.g. sync
   * @param configId - id of that config
   * @return lists job in descending order by created_at
   * @throws IOException - what you do when you IO
   */
  List<Job> listJobs(Set<JobConfig.ConfigType> configTypes, String configId, int limit, int offset) throws IOException;

  List<Job> listJobs(JobConfig.ConfigType configType, String configId, int limit, int offset) throws IOException;

  List<Job> listJobsWithStatus(JobStatus status) throws IOException;

  List<Job> listJobsWithStatus(Set<JobConfig.ConfigType> configTypes, JobStatus status) throws IOException;

  List<Job> listJobsWithStatus(JobConfig.ConfigType configType, JobStatus status) throws IOException;

  Optional<Job> getLastReplicationJob(UUID connectionId) throws IOException;

  /**
   * if a job does not succeed, we assume that it synced nothing. that is the most conservative
   * assumption we can make. as long as all destinations write the final data output in a
   * transactional way, this will be true. if this changes, then we may end up writing duplicate data
   * with our incremental append only. this is preferable to failing to send data at all. our
   * incremental append only most closely resembles a deliver at least once strategy anyway.
   *
   * @param connectionId - id of the connection whose state we want to fetch.
   * @return the current state, if any of, the connection
   * @throws IOException exception due to interaction with persistence
   */
  Optional<State> getCurrentState(UUID connectionId) throws IOException;

  Optional<Job> getNextJob() throws IOException;

  /// ARCHIVE

  /**
   * Returns the AirbyteVersion.
   */
  Optional<String> getVersion() throws IOException;

  /**
   * Set the airbyte version
   */
  void setVersion(String airbyteVersion) throws IOException;

  /**
   * Returns a deployment UUID.
   */
  Optional<UUID> getDeployment() throws IOException;
  // a deployment references a setup of airbyte. it is created the first time the docker compose or
  // K8s is ready.

  /**
   * Set deployment id. If one is already set, the new value is ignored.
   */
  void setDeployment(UUID uuid) throws IOException;

  /**
   * Export all SQL tables from @param schema into streams of JsonNode objects. This returns a Map of
   * table schemas to the associated streams of records that is being exported.
   */
  Map<JobsDatabaseSchema, Stream<JsonNode>> exportDatabase() throws IOException;

  Map<String, Stream<JsonNode>> dump() throws IOException;

  /**
   * Import all SQL tables from streams of JsonNode objects.
   *
   * @param data is a Map of table schemas to the associated streams of records to import.
   * @param airbyteVersion is the version of the files to be imported and should match the Airbyte
   *        version in the Database.
   */
  void importDatabase(String airbyteVersion, Map<JobsDatabaseSchema, Stream<JsonNode>> data) throws IOException;

  /**
   * Purges job history while ensuring that the latest saved-state information is maintained.
   *
   * @throws IOException
   */
  void purgeJobHistory();

}
