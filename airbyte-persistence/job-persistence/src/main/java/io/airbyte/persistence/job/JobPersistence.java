/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.version.Version;
import io.airbyte.config.AttemptFailureSummary;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobOutput;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.config.SyncStats;
import io.airbyte.db.instance.jobs.JobsDatabaseSchema;
import io.airbyte.persistence.job.models.AttemptNormalizationStatus;
import io.airbyte.persistence.job.models.AttemptWithJobInfo;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.persistence.job.models.JobStatus;
import io.airbyte.persistence.job.models.JobWithStatusAndTimestamp;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Stream;

/**
 * General interface methods for persistence to the Jobs database. This database is separate from
 * the config database as job-related tables has an order of magnitude higher load and scale
 * differently from the config tables.
 */
public interface JobPersistence {

  List<SyncStats> getSyncStats(long jobId, int attemptNumber) throws IOException;

  List<NormalizationSummary> getNormalizationSummary(long jobId, int attemptNumber) throws IOException;

  Job getJob(long jobId) throws IOException;

  //
  // JOB LIFECYCLE
  //

  /**
   * Enqueue a new job. Its initial status will be pending.
   *
   * @param scope key that will be used to determine if two jobs should not be run at the same time;
   *        it is the primary id of the standard sync (StandardSync#connectionId)
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
   * Create a new attempt for a job and return its attempt number. Throws
   * {@link IllegalStateException} if the job is already in a terminal state.
   *
   * @param jobId job for which an attempt will be created
   * @param logPath path where logs should be written for the attempt
   * @return The attempt number of the created attempt (see {@link DefaultJobPersistence})
   * @throws IOException exception due to interaction with persistence
   */
  int createAttempt(long jobId, Path logPath) throws IOException;

  /**
   * Sets an attempt to FAILED. Also attempts to set the parent job to INCOMPLETE. The job's status
   * will not be changed if it is already in a terminal state.
   *
   * @param jobId job id
   * @param attemptNumber attempt id
   * @throws IOException exception due to interaction with persistence
   */
  void failAttempt(long jobId, int attemptNumber) throws IOException;

  /**
   * Sets an attempt to SUCCEEDED. Also attempts to set the parent job to SUCCEEDED. The job's status
   * is changed regardless of what state it is in.
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
  void setAttemptTemporalWorkflowInfo(long jobId, int attemptNumber, String temporalWorkflowId, String processingTaskQueue) throws IOException;

  /**
   * Retrieves an attempt's temporal workflow id. Used to cancel the workflow.
   */
  Optional<String> getAttemptTemporalWorkflowId(long jobId, int attemptNumber) throws IOException;

  /**
   * When the output is a StandardSyncOutput, caller of this method should persiste
   * StandardSyncOutput#state in the configs database by calling
   * ConfigRepository#updateConnectionState, which takes care of persisting the connection state.
   */
  void writeOutput(long jobId, int attemptNumber, JobOutput output) throws IOException;

  /**
   * Writes a summary of all failures that occurred during the attempt.
   *
   * @param jobId job id
   * @param attemptNumber attempt number
   * @param failureSummary summary containing failure metadata and ordered list of failures
   * @throws IOException exception due to interaction with persistence
   */
  void writeAttemptFailureSummary(long jobId, int attemptNumber, AttemptFailureSummary failureSummary) throws IOException;

  /**
   * @param configTypes - the type of config, e.g. sync
   * @param connectionId - ID of the connection for which the job count should be retrieved
   * @return count of jobs belonging to the specified connection
   * @throws IOException
   */
  Long getJobCount(final Set<ConfigType> configTypes, final String connectionId) throws IOException;

  /**
   * @param configTypes - type of config, e.g. sync
   * @param configId - id of that config
   * @return lists job in descending order by created_at
   * @throws IOException - what you do when you IO
   */
  List<Job> listJobs(Set<JobConfig.ConfigType> configTypes, String configId, int limit, int offset) throws IOException;

  /**
   * @param configType The type of job
   * @param attemptEndedAtTimestamp The timestamp after which you want the jobs
   * @return List of jobs that have attempts after the provided timestamp
   * @throws IOException
   */
  List<Job> listJobs(ConfigType configType, Instant attemptEndedAtTimestamp) throws IOException;

  List<Job> listJobs(JobConfig.ConfigType configType, String configId, int limit, int offset) throws IOException;

  /**
   * @param configTypes - type of config, e.g. sync
   * @param connectionId - id of the connection for which jobs should be retrieved
   * @param includingJobId - id of the job that should be the included in the list, if it exists in
   *        the connection
   * @param pagesize - the pagesize that should be used when building the list (response may include
   *        multiple pages)
   * @return List of jobs in descending created_at order including the specified job. Will include
   *         multiple pages of jobs if required to include the specified job. If the specified job
   *         does not exist in the connection, the returned list will be empty.
   * @throws IOException
   */
  List<Job> listJobsIncludingId(Set<JobConfig.ConfigType> configTypes, String connectionId, long includingJobId, int pagesize) throws IOException;

  List<Job> listJobsWithStatus(JobStatus status) throws IOException;

  List<Job> listJobsWithStatus(Set<JobConfig.ConfigType> configTypes, JobStatus status) throws IOException;

  List<Job> listJobsWithStatus(JobConfig.ConfigType configType, JobStatus status) throws IOException;

  List<Job> listJobsForConnectionWithStatuses(UUID connectionId, Set<JobConfig.ConfigType> configTypes, Set<JobStatus> statuses) throws IOException;

  /**
   * @param connectionId The ID of the connection
   * @param configTypes The types of jobs
   * @param jobCreatedAtTimestamp The timestamp after which you want the jobs
   * @return List of jobs that only include information regarding id, status, timestamps from a
   *         specific connection that have attempts after the provided timestamp, sorted by jobs'
   *         createAt in descending order
   * @throws IOException
   */
  List<JobWithStatusAndTimestamp> listJobStatusAndTimestampWithConnection(UUID connectionId,
                                                                          Set<JobConfig.ConfigType> configTypes,
                                                                          Instant jobCreatedAtTimestamp)
      throws IOException;

  Optional<Job> getLastReplicationJob(UUID connectionId) throws IOException;

  Optional<Job> getLastSyncJob(UUID connectionId) throws IOException;

  List<Job> getLastSyncJobForConnections(final List<UUID> connectionIds) throws IOException;

  List<Job> getRunningSyncJobForConnections(final List<UUID> connectionIds) throws IOException;

  Optional<Job> getFirstReplicationJob(UUID connectionId) throws IOException;

  Optional<Job> getNextJob() throws IOException;

  /**
   * @param configType The type of job
   * @param attemptEndedAtTimestamp The timestamp after which you want the attempts
   * @return List of attempts (with job attached) that ended after the provided timestamp, sorted by
   *         attempts' endedAt in ascending order
   * @throws IOException
   */
  List<AttemptWithJobInfo> listAttemptsWithJobInfo(ConfigType configType, Instant attemptEndedAtTimestamp) throws IOException;

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
   * Get the max supported Airbyte Protocol Version
   */
  Optional<Version> getAirbyteProtocolVersionMax() throws IOException;

  /**
   * Set the max supported Airbyte Protocol Version
   */
  void setAirbyteProtocolVersionMax(Version version) throws IOException;

  /**
   * Get the min supported Airbyte Protocol Version
   */
  Optional<Version> getAirbyteProtocolVersionMin() throws IOException;

  /**
   * Set the min supported Airbyte Protocol Version
   */
  void setAirbyteProtocolVersionMin(Version version) throws IOException;

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
   */
  void purgeJobHistory();

  /**
   * Check if the secret has been migrated to a new secret store from a plain text values
   */
  boolean isSecretMigrated() throws IOException;

  /**
   * Set that the secret migration has been performed.
   */
  void setSecretMigrationDone() throws IOException;

  List<AttemptNormalizationStatus> getAttemptNormalizationStatusesForJob(final Long jobId) throws IOException;

}
