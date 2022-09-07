/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import com.google.common.base.Preconditions;
import io.airbyte.api.model.generated.ConnectionRead;
import io.airbyte.api.model.generated.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.generated.DestinationDefinitionRead;
import io.airbyte.api.model.generated.DestinationIdRequestBody;
import io.airbyte.api.model.generated.DestinationRead;
import io.airbyte.api.model.generated.JobDebugInfoRead;
import io.airbyte.api.model.generated.JobDebugRead;
import io.airbyte.api.model.generated.JobIdRequestBody;
import io.airbyte.api.model.generated.JobInfoRead;
import io.airbyte.api.model.generated.JobListRequestBody;
import io.airbyte.api.model.generated.JobReadList;
import io.airbyte.api.model.generated.JobWithAttemptsRead;
import io.airbyte.api.model.generated.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.generated.SourceDefinitionRead;
import io.airbyte.api.model.generated.SourceIdRequestBody;
import io.airbyte.api.model.generated.SourceRead;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.converters.JobConverter;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;

public class JobHistoryHandler {

  private final ConnectionsHandler connectionsHandler;
  private final SourceHandler sourceHandler;
  private final DestinationHandler destinationHandler;
  private final SourceDefinitionsHandler sourceDefinitionsHandler;
  private final DestinationDefinitionsHandler destinationDefinitionsHandler;
  public static final int DEFAULT_PAGE_SIZE = 200;
  private final JobPersistence jobPersistence;
  private final JobConverter jobConverter;
  private final AirbyteVersion airbyteVersion;

  public JobHistoryHandler(final JobPersistence jobPersistence,
                           final WorkerEnvironment workerEnvironment,
                           final LogConfigs logConfigs,
                           final ConnectionsHandler connectionsHandler,
                           final SourceHandler sourceHandler,
                           final SourceDefinitionsHandler sourceDefinitionsHandler,
                           final DestinationHandler destinationHandler,
                           final DestinationDefinitionsHandler destinationDefinitionsHandler,
                           final AirbyteVersion airbyteVersion) {
    jobConverter = new JobConverter(workerEnvironment, logConfigs);
    this.jobPersistence = jobPersistence;
    this.connectionsHandler = connectionsHandler;
    this.sourceHandler = sourceHandler;
    this.sourceDefinitionsHandler = sourceDefinitionsHandler;
    this.destinationHandler = destinationHandler;
    this.destinationDefinitionsHandler = destinationDefinitionsHandler;
    this.airbyteVersion = airbyteVersion;
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

    final List<JobWithAttemptsRead> jobReads = jobPersistence.listJobs(configTypes,
        configId,
        (request.getPagination() != null && request.getPagination().getPageSize() != null) ? request.getPagination().getPageSize()
            : DEFAULT_PAGE_SIZE,
        (request.getPagination() != null && request.getPagination().getRowOffset() != null) ? request.getPagination().getRowOffset() : 0)
        .stream()
        .map(attempt -> jobConverter.getJobWithAttemptsRead(attempt))
        .collect(Collectors.toList());
    return new JobReadList().jobs(jobReads);
  }

  public JobInfoRead getJobInfo(final JobIdRequestBody jobIdRequestBody) throws IOException {
    final Job job = jobPersistence.getJob(jobIdRequestBody.getId());
    return jobConverter.getJobInfoRead(job);
  }

  public JobDebugInfoRead getJobDebugInfo(final JobIdRequestBody jobIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final Job job = jobPersistence.getJob(jobIdRequestBody.getId());
    final JobInfoRead jobinfoRead = jobConverter.getJobInfoRead(job);

    return buildJobDebugInfoRead(jobinfoRead);
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
