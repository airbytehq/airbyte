/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import com.google.common.base.Preconditions;
import io.airbyte.api.model.generated.AttemptInfoRead;
import io.airbyte.api.model.generated.AttemptNormalizationStatusReadList;
import io.airbyte.api.model.generated.AttemptRead;
import io.airbyte.api.model.generated.AttemptStats;
import io.airbyte.api.model.generated.AttemptStreamStats;
import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.ConnectionRead;
import io.airbyte.api.model.generated.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.generated.DestinationDefinitionRead;
import io.airbyte.api.model.generated.DestinationIdRequestBody;
import io.airbyte.api.model.generated.DestinationRead;
import io.airbyte.api.model.generated.JobDebugInfoRead;
import io.airbyte.api.model.generated.JobDebugRead;
import io.airbyte.api.model.generated.JobIdRequestBody;
import io.airbyte.api.model.generated.JobInfoLightRead;
import io.airbyte.api.model.generated.JobInfoRead;
import io.airbyte.api.model.generated.JobListRequestBody;
import io.airbyte.api.model.generated.JobOptionalRead;
import io.airbyte.api.model.generated.JobRead;
import io.airbyte.api.model.generated.JobReadList;
import io.airbyte.api.model.generated.JobWithAttemptsRead;
import io.airbyte.api.model.generated.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.generated.SourceDefinitionRead;
import io.airbyte.api.model.generated.SourceIdRequestBody;
import io.airbyte.api.model.generated.SourceRead;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.server.converters.JobConverter;
import io.airbyte.commons.server.converters.WorkflowStateConverter;
import io.airbyte.commons.temporal.TemporalClient;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.JobPersistence.JobAttemptPair;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.persistence.job.models.JobStatus;
import io.airbyte.validation.json.JsonValidationException;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;

@Singleton
@Slf4j
public class JobHistoryHandler {

  private final ConnectionsHandler connectionsHandler;
  private final SourceHandler sourceHandler;
  private final DestinationHandler destinationHandler;
  private final SourceDefinitionsHandler sourceDefinitionsHandler;
  private final DestinationDefinitionsHandler destinationDefinitionsHandler;
  public static final int DEFAULT_PAGE_SIZE = 200;
  private final JobPersistence jobPersistence;
  private final JobConverter jobConverter;
  private final WorkflowStateConverter workflowStateConverter;
  private final AirbyteVersion airbyteVersion;
  private final TemporalClient temporalClient;

  public JobHistoryHandler(final JobPersistence jobPersistence,
                           final WorkerEnvironment workerEnvironment,
                           final LogConfigs logConfigs,
                           final ConnectionsHandler connectionsHandler,
                           final SourceHandler sourceHandler,
                           final SourceDefinitionsHandler sourceDefinitionsHandler,
                           final DestinationHandler destinationHandler,
                           final DestinationDefinitionsHandler destinationDefinitionsHandler,
                           final AirbyteVersion airbyteVersion,
                           final TemporalClient temporalClient) {
    jobConverter = new JobConverter(workerEnvironment, logConfigs);
    workflowStateConverter = new WorkflowStateConverter();
    this.jobPersistence = jobPersistence;
    this.connectionsHandler = connectionsHandler;
    this.sourceHandler = sourceHandler;
    this.sourceDefinitionsHandler = sourceDefinitionsHandler;
    this.destinationHandler = destinationHandler;
    this.destinationDefinitionsHandler = destinationDefinitionsHandler;
    this.airbyteVersion = airbyteVersion;
    this.temporalClient = temporalClient;
  }

  @Deprecated(forRemoval = true)
  public JobHistoryHandler(final JobPersistence jobPersistence,
                           final WorkerEnvironment workerEnvironment,
                           final LogConfigs logConfigs,
                           final ConnectionsHandler connectionsHandler,
                           final SourceHandler sourceHandler,
                           final SourceDefinitionsHandler sourceDefinitionsHandler,
                           final DestinationHandler destinationHandler,
                           final DestinationDefinitionsHandler destinationDefinitionsHandler,
                           final AirbyteVersion airbyteVersion) {
    this(jobPersistence, workerEnvironment, logConfigs, connectionsHandler, sourceHandler, sourceDefinitionsHandler, destinationHandler,
        destinationDefinitionsHandler, airbyteVersion, null);
  }

  @SuppressWarnings("UnstableApiUsage")
  public JobReadList listJobsFor(final JobListRequestBody request) throws IOException {
    Preconditions.checkNotNull(request.getConfigTypes(), "configType cannot be null.");
    Preconditions.checkState(!request.getConfigTypes().isEmpty(), "Must include at least one configType.");

    final Set<ConfigType> configTypes = request.getConfigTypes()
        .stream()
        .map(type -> Enums.convertTo(type, JobConfig.ConfigType.class))
        .collect(Collectors.toSet());
    final String configId = request.getConfigId();

    final int pageSize = (request.getPagination() != null && request.getPagination().getPageSize() != null) ? request.getPagination().getPageSize()
        : DEFAULT_PAGE_SIZE;
    final List<Job> jobs;

    if (request.getIncludingJobId() != null) {
      jobs = jobPersistence.listJobsIncludingId(configTypes, configId, request.getIncludingJobId(), pageSize);
    } else {
      jobs = jobPersistence.listJobs(configTypes, configId, pageSize,
          (request.getPagination() != null && request.getPagination().getRowOffset() != null) ? request.getPagination().getRowOffset() : 0);
    }

    final List<JobWithAttemptsRead> jobReads = jobs.stream().map(JobConverter::getJobWithAttemptsRead).collect(Collectors.toList());
    final var jobIds = jobReads.stream().map(r -> r.getJob().getId()).toList();
    final Map<JobAttemptPair, JobPersistence.AttemptStats> stats = jobPersistence.getAttemptStats(jobIds);
    for (final JobWithAttemptsRead jwar : jobReads) {
      for (final AttemptRead a : jwar.getAttempts()) {
        final var stat = stats.get(new JobAttemptPair(jwar.getJob().getId(), a.getId().intValue()));
        if (stat == null) {
          log.error("Missing stats for job {} attempt {}", jwar.getJob().getId(), a.getId().intValue());
          continue;
        }

        hydrateWithStats(a, stat);
      }
    }

    final Long totalJobCount = jobPersistence.getJobCount(configTypes, configId);
    return new JobReadList().jobs(jobReads).totalJobCount(totalJobCount);
  }

  /**
   * Retrieve stats for a given job id and attempt number and hydrate the api model with the retrieved
   * information.
   *
   * @param jobId the job the attempt belongs to. Used as an index to retrieve stats.
   * @param a the attempt to hydrate stats for.
   */
  private void hydrateWithStats(final AttemptRead a, final JobPersistence.AttemptStats attemptStats) {
    a.setTotalStats(new AttemptStats());

    final var combinedStats = attemptStats.combinedStats();
    if (combinedStats == null) {
      // If overall stats are missing, assume stream stats are also missing, since overall stats are
      // easier to produce than stream stats. Exit early.
      return;
    }

    a.getTotalStats()
        .estimatedBytes(combinedStats.getEstimatedBytes())
        .estimatedRecords(combinedStats.getEstimatedRecords())
        .bytesEmitted(combinedStats.getBytesEmitted())
        .recordsEmitted(combinedStats.getRecordsEmitted())
        .recordsCommitted(combinedStats.getRecordsCommitted());

    final var streamStats = attemptStats.perStreamStats().stream().map(s -> new AttemptStreamStats()
        .streamName(s.getStreamName())
        .streamNamespace(s.getStreamNamespace())
        .stats(new AttemptStats()
            .bytesEmitted(s.getStats().getBytesEmitted())
            .recordsEmitted(s.getStats().getRecordsEmitted())
            .recordsCommitted(s.getStats().getRecordsCommitted())
            .estimatedBytes(s.getStats().getEstimatedBytes())
            .estimatedRecords(s.getStats().getEstimatedRecords())))
        .collect(Collectors.toList());
    a.setStreamStats(streamStats);
  }

  public JobInfoRead getJobInfo(final JobIdRequestBody jobIdRequestBody) throws IOException {
    final Job job = jobPersistence.getJob(jobIdRequestBody.getId());
    return jobConverter.getJobInfoRead(job);
  }

  public JobInfoLightRead getJobInfoLight(final JobIdRequestBody jobIdRequestBody) throws IOException {
    final Job job = jobPersistence.getJob(jobIdRequestBody.getId());
    return jobConverter.getJobInfoLightRead(job);
  }

  public JobOptionalRead getLastReplicationJob(final ConnectionIdRequestBody connectionIdRequestBody) throws IOException {
    Optional<Job> job = jobPersistence.getLastReplicationJob(connectionIdRequestBody.getConnectionId());
    if (job.isEmpty()) {
      return new JobOptionalRead();
    } else {
      return jobConverter.getJobOptionalRead(job.get());
    }

  }

  public JobDebugInfoRead getJobDebugInfo(final JobIdRequestBody jobIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final Job job = jobPersistence.getJob(jobIdRequestBody.getId());
    final JobInfoRead jobinfoRead = jobConverter.getJobInfoRead(job);

    for (final AttemptInfoRead a : jobinfoRead.getAttempts()) {
      final int attemptNumber = a.getAttempt().getId().intValue();
      final var attemptStats = jobPersistence.getAttemptStats(job.getId(), attemptNumber);
      hydrateWithStats(a.getAttempt(), attemptStats);
    }

    final JobDebugInfoRead jobDebugInfoRead = buildJobDebugInfoRead(jobinfoRead);
    if (temporalClient != null) {
      final UUID connectionId = UUID.fromString(job.getScope());
      temporalClient.getWorkflowState(connectionId)
          .map(workflowStateConverter::getWorkflowStateRead)
          .ifPresent(jobDebugInfoRead::setWorkflowState);
    }

    return jobDebugInfoRead;
  }

  public Optional<JobRead> getLatestRunningSyncJob(final UUID connectionId) throws IOException {
    final List<Job> nonTerminalSyncJobsForConnection = jobPersistence.listJobsForConnectionWithStatuses(
        connectionId,
        Collections.singleton(ConfigType.SYNC),
        JobStatus.NON_TERMINAL_STATUSES);

    // there *should* only be a single running sync job for a connection, but
    // jobPersistence.listJobsForConnectionWithStatuses orders by created_at desc so
    // .findFirst will always return what we want.
    return nonTerminalSyncJobsForConnection.stream().map(JobConverter::getJobRead).findFirst();
  }

  public Optional<JobRead> getLatestSyncJob(final UUID connectionId) throws IOException {
    return jobPersistence.getLastSyncJob(connectionId).map(JobConverter::getJobRead);
  }

  public List<JobRead> getLatestSyncJobsForConnections(final List<UUID> connectionIds) throws IOException {
    return jobPersistence.getLastSyncJobForConnections(connectionIds).stream()
        .map(JobConverter::getJobRead)
        .collect(Collectors.toList());
  }

  public AttemptNormalizationStatusReadList getAttemptNormalizationStatuses(final JobIdRequestBody jobIdRequestBody) throws IOException {
    return new AttemptNormalizationStatusReadList()
        .attemptNormalizationStatuses(jobPersistence.getAttemptNormalizationStatusesForJob(jobIdRequestBody.getId()).stream()
            .map(JobConverter::convertAttemptNormalizationStatus).collect(Collectors.toList()));
  }

  public List<JobRead> getRunningSyncJobForConnections(final List<UUID> connectionIds) throws IOException {
    return jobPersistence.getRunningSyncJobForConnections(connectionIds).stream()
        .map(JobConverter::getJobRead)
        .collect(Collectors.toList());
  }

  private SourceRead getSourceRead(final ConnectionRead connectionRead) throws JsonValidationException, IOException, ConfigNotFoundException {
    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody().sourceId(connectionRead.getSourceId());
    return sourceHandler.getSource(sourceIdRequestBody);
  }

  private DestinationRead getDestinationRead(final ConnectionRead connectionRead)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final DestinationIdRequestBody destinationIdRequestBody = new DestinationIdRequestBody().destinationId(connectionRead.getDestinationId());
    return destinationHandler.getDestination(destinationIdRequestBody);
  }

  private SourceDefinitionRead getSourceDefinitionRead(final SourceRead sourceRead)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody =
        new SourceDefinitionIdRequestBody().sourceDefinitionId(sourceRead.getSourceDefinitionId());
    return sourceDefinitionsHandler.getSourceDefinition(sourceDefinitionIdRequestBody);
  }

  private DestinationDefinitionRead getDestinationDefinitionRead(final DestinationRead destinationRead)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody =
        new DestinationDefinitionIdRequestBody().destinationDefinitionId(destinationRead.getDestinationDefinitionId());
    return destinationDefinitionsHandler.getDestinationDefinition(destinationDefinitionIdRequestBody);
  }

  private JobDebugInfoRead buildJobDebugInfoRead(final JobInfoRead jobInfoRead)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final String configId = jobInfoRead.getJob().getConfigId();
    final ConnectionRead connection = connectionsHandler.getConnection(UUID.fromString(configId));
    final SourceRead source = getSourceRead(connection);
    final DestinationRead destination = getDestinationRead(connection);
    final SourceDefinitionRead sourceDefinitionRead = getSourceDefinitionRead(source);
    final DestinationDefinitionRead destinationDefinitionRead = getDestinationDefinitionRead(destination);
    final JobDebugRead jobDebugRead = JobConverter.getDebugJobInfoRead(jobInfoRead, sourceDefinitionRead, destinationDefinitionRead, airbyteVersion);

    return new JobDebugInfoRead()
        .attempts(jobInfoRead.getAttempts())
        .job(jobDebugRead);
  }

}
