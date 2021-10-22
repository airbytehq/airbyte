/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import io.airbyte.api.model.AuthSpecification;
import io.airbyte.api.model.CheckConnectionRead;
import io.airbyte.api.model.CheckConnectionRead.StatusEnum;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.ConnectionState;
import io.airbyte.api.model.DestinationCoreConfig;
import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationDefinitionSpecificationRead;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationSyncMode;
import io.airbyte.api.model.DestinationUpdate;
import io.airbyte.api.model.JobIdRequestBody;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.SourceCoreConfig;
import io.airbyte.api.model.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.SourceDefinitionSpecificationRead;
import io.airbyte.api.model.SourceDiscoverSchemaRead;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceUpdate;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.State;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.SchedulerJobClient;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.server.converters.CatalogConverter;
import io.airbyte.server.converters.ConfigurationUpdate;
import io.airbyte.server.converters.JobConverter;
import io.airbyte.server.converters.OauthModelConverter;
import io.airbyte.server.converters.SpecFetcher;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.temporal.TemporalUtils;
import io.temporal.api.common.v1.WorkflowExecution;
import io.temporal.api.workflowservice.v1.RequestCancelWorkflowExecutionRequest;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SchedulerHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(SchedulerHandler.class);
  private static final UUID NO_WORKSPACE = UUID.fromString("00000000-0000-0000-0000-000000000000");

  private final ConfigRepository configRepository;
  private final SchedulerJobClient schedulerJobClient;
  private final SynchronousSchedulerClient synchronousSchedulerClient;
  private final SpecFetcher specFetcher;
  private final ConfigurationUpdate configurationUpdate;
  private final JsonSchemaValidator jsonSchemaValidator;
  private final JobPersistence jobPersistence;
  private final JobNotifier jobNotifier;
  private final WorkflowServiceStubs temporalService;
  private final OAuthConfigSupplier oAuthConfigSupplier;

  public SchedulerHandler(final ConfigRepository configRepository,
                          final SchedulerJobClient schedulerJobClient,
                          final SynchronousSchedulerClient synchronousSchedulerClient,
                          final JobPersistence jobPersistence,
                          final JobNotifier jobNotifier,
                          final WorkflowServiceStubs temporalService,
                          final OAuthConfigSupplier oAuthConfigSupplier) {
    this(
        configRepository,
        schedulerJobClient,
        synchronousSchedulerClient,
        new ConfigurationUpdate(configRepository, new SpecFetcher(synchronousSchedulerClient)),
        new JsonSchemaValidator(),
        new SpecFetcher(synchronousSchedulerClient),
        jobPersistence,
        jobNotifier,
        temporalService,
        oAuthConfigSupplier);
  }

  @VisibleForTesting
  SchedulerHandler(final ConfigRepository configRepository,
                   final SchedulerJobClient schedulerJobClient,
                   final SynchronousSchedulerClient synchronousSchedulerClient,
                   final ConfigurationUpdate configurationUpdate,
                   final JsonSchemaValidator jsonSchemaValidator,
                   final SpecFetcher specFetcher,
                   final JobPersistence jobPersistence,
                   final JobNotifier jobNotifier,
                   final WorkflowServiceStubs temporalService,
                   final OAuthConfigSupplier oAuthConfigSupplier) {
    this.configRepository = configRepository;
    this.schedulerJobClient = schedulerJobClient;
    this.synchronousSchedulerClient = synchronousSchedulerClient;
    this.configurationUpdate = configurationUpdate;
    this.jsonSchemaValidator = jsonSchemaValidator;
    this.specFetcher = specFetcher;
    this.jobPersistence = jobPersistence;
    this.jobNotifier = jobNotifier;
    this.temporalService = temporalService;
    this.oAuthConfigSupplier = oAuthConfigSupplier;
  }

  public CheckConnectionRead checkSourceConnectionFromSourceId(final SourceIdRequestBody sourceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final SourceConnection source = configRepository.getSourceConnection(sourceIdRequestBody.getSourceId());
    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(source.getSourceDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());

    return reportConnectionStatus(synchronousSchedulerClient.createSourceCheckConnectionJob(source, imageName));
  }

  public CheckConnectionRead checkSourceConnectionFromSourceCreate(final SourceCoreConfig sourceConfig)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(sourceConfig.getSourceDefinitionId());
    final var partialConfig = configRepository.statefulSplitEphemeralSecrets(
        sourceConfig.getConnectionConfiguration(),
        specFetcher.getSpec(sourceDef));

    // todo (cgardens) - narrow the struct passed to the client. we are not setting fields that are
    // technically declared as required.
    final SourceConnection source = new SourceConnection()
        .withSourceDefinitionId(sourceConfig.getSourceDefinitionId())
        .withConfiguration(partialConfig);

    final String imageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());
    return reportConnectionStatus(synchronousSchedulerClient.createSourceCheckConnectionJob(source, imageName));
  }

  public CheckConnectionRead checkSourceConnectionFromSourceIdForUpdate(final SourceUpdate sourceUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final SourceConnection updatedSource =
        configurationUpdate.source(sourceUpdate.getSourceId(), sourceUpdate.getName(), sourceUpdate.getConnectionConfiguration());

    final ConnectorSpecification spec = getSpecFromSourceDefinitionId(updatedSource.getSourceDefinitionId());
    jsonSchemaValidator.ensure(spec.getConnectionSpecification(), updatedSource.getConfiguration());

    final SourceCoreConfig sourceCoreConfig = new SourceCoreConfig()
        .connectionConfiguration(updatedSource.getConfiguration())
        .sourceDefinitionId(updatedSource.getSourceDefinitionId());

    return checkSourceConnectionFromSourceCreate(sourceCoreConfig);
  }

  public CheckConnectionRead checkDestinationConnectionFromDestinationId(final DestinationIdRequestBody destinationIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final DestinationConnection destination = configRepository.getDestinationConnection(destinationIdRequestBody.getDestinationId());
    final StandardDestinationDefinition destinationDef = configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(destinationDef.getDockerRepository(), destinationDef.getDockerImageTag());
    return reportConnectionStatus(synchronousSchedulerClient.createDestinationCheckConnectionJob(destination, imageName));
  }

  public CheckConnectionRead checkDestinationConnectionFromDestinationCreate(final DestinationCoreConfig destinationConfig)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardDestinationDefinition destDef = configRepository.getStandardDestinationDefinition(destinationConfig.getDestinationDefinitionId());
    final var partialConfig = configRepository.statefulSplitEphemeralSecrets(
        destinationConfig.getConnectionConfiguration(),
        specFetcher.getSpec(destDef));

    // todo (cgardens) - narrow the struct passed to the client. we are not setting fields that are
    // technically declared as required.
    final DestinationConnection destination = new DestinationConnection()
        .withDestinationDefinitionId(destinationConfig.getDestinationDefinitionId())
        .withConfiguration(partialConfig);

    final String imageName = DockerUtils.getTaggedImageName(destDef.getDockerRepository(), destDef.getDockerImageTag());
    return reportConnectionStatus(synchronousSchedulerClient.createDestinationCheckConnectionJob(destination, imageName));
  }

  public CheckConnectionRead checkDestinationConnectionFromDestinationIdForUpdate(final DestinationUpdate destinationUpdate)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final DestinationConnection updatedDestination = configurationUpdate
        .destination(destinationUpdate.getDestinationId(), destinationUpdate.getName(), destinationUpdate.getConnectionConfiguration());

    final ConnectorSpecification spec = getSpecFromDestinationDefinitionId(updatedDestination.getDestinationDefinitionId());
    jsonSchemaValidator.ensure(spec.getConnectionSpecification(), updatedDestination.getConfiguration());

    final DestinationCoreConfig destinationCoreConfig = new DestinationCoreConfig()
        .connectionConfiguration(updatedDestination.getConfiguration())
        .destinationDefinitionId(updatedDestination.getDestinationDefinitionId());

    return checkDestinationConnectionFromDestinationCreate(destinationCoreConfig);
  }

  public SourceDiscoverSchemaRead discoverSchemaForSourceFromSourceId(final SourceIdRequestBody sourceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final SourceConnection source = configRepository.getSourceConnection(sourceIdRequestBody.getSourceId());
    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(source.getSourceDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());
    final SynchronousResponse<AirbyteCatalog> response = synchronousSchedulerClient.createDiscoverSchemaJob(source, imageName);
    return discoverJobToOutput(response);
  }

  public SourceDiscoverSchemaRead discoverSchemaForSourceFromSourceCreate(final SourceCoreConfig sourceCreate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(sourceCreate.getSourceDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());
    // todo (cgardens) - narrow the struct passed to the client. we are not setting fields that are
    // technically declared as required.
    final SourceConnection source = new SourceConnection()
        .withSourceDefinitionId(sourceCreate.getSourceDefinitionId())
        .withConfiguration(sourceCreate.getConnectionConfiguration());
    final SynchronousResponse<AirbyteCatalog> response = synchronousSchedulerClient.createDiscoverSchemaJob(source, imageName);
    return discoverJobToOutput(response);
  }

  private static SourceDiscoverSchemaRead discoverJobToOutput(final SynchronousResponse<AirbyteCatalog> response) {
    final SourceDiscoverSchemaRead sourceDiscoverSchemaRead = new SourceDiscoverSchemaRead()
        .jobInfo(JobConverter.getSynchronousJobRead(response));

    if (response.isSuccess()) {
      sourceDiscoverSchemaRead.catalog(CatalogConverter.toApi(response.getOutput()));
    }

    return sourceDiscoverSchemaRead;
  }

  public SourceDefinitionSpecificationRead getSourceDefinitionSpecification(final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID sourceDefinitionId = sourceDefinitionIdRequestBody.getSourceDefinitionId();
    final StandardSourceDefinition source = configRepository.getStandardSourceDefinition(sourceDefinitionId);
    final SynchronousResponse<ConnectorSpecification> response = specFetcher.getSpecJobResponse(source);
    final ConnectorSpecification spec = response.getOutput();
    final SourceDefinitionSpecificationRead specRead = new SourceDefinitionSpecificationRead()
        .jobInfo(JobConverter.getSynchronousJobRead(response))
        .connectionSpecification(spec.getConnectionSpecification())
        .documentationUrl(spec.getDocumentationUrl().toString())
        .sourceDefinitionId(sourceDefinitionId);

    final Optional<AuthSpecification> authSpec = OauthModelConverter.getAuthSpec(spec);
    if (authSpec.isPresent()) {
      specRead.setAuthSpecification(authSpec.get());
    }

    return specRead;
  }

  public DestinationDefinitionSpecificationRead getDestinationSpecification(final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID destinationDefinitionId = destinationDefinitionIdRequestBody.getDestinationDefinitionId();
    final StandardDestinationDefinition destination = configRepository.getStandardDestinationDefinition(destinationDefinitionId);
    final SynchronousResponse<ConnectorSpecification> response = specFetcher.getSpecJobResponse(destination);
    final ConnectorSpecification spec = response.getOutput();

    final DestinationDefinitionSpecificationRead specRead = new DestinationDefinitionSpecificationRead()
        .jobInfo(JobConverter.getSynchronousJobRead(response))
        .supportedDestinationSyncModes(Enums.convertListTo(spec.getSupportedDestinationSyncModes(), DestinationSyncMode.class))
        .connectionSpecification(spec.getConnectionSpecification())
        .documentationUrl(spec.getDocumentationUrl().toString())
        .supportsNormalization(spec.getSupportsNormalization())
        .supportsDbt(spec.getSupportsDBT())
        .destinationDefinitionId(destinationDefinitionId);

    final Optional<AuthSpecification> authSpec = OauthModelConverter.getAuthSpec(spec);
    if (authSpec.isPresent()) {
      specRead.setAuthSpecification(authSpec.get());
    }

    return specRead;
  }

  public JobInfoRead syncConnection(final ConnectionIdRequestBody connectionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID connectionId = connectionIdRequestBody.getConnectionId();
    final StandardSync standardSync = configRepository.getStandardSync(connectionId);

    final SourceConnection sourceConnection = configRepository.getSourceConnection(standardSync.getSourceId());
    final DestinationConnection destinationConnection = configRepository.getDestinationConnection(standardSync.getDestinationId());
    final JsonNode sourceConfiguration = oAuthConfigSupplier.injectSourceOAuthParameters(
        sourceConnection.getSourceDefinitionId(),
        sourceConnection.getWorkspaceId(),
        sourceConnection.getConfiguration());
    sourceConnection.withConfiguration(sourceConfiguration);
    final JsonNode destinationConfiguration = oAuthConfigSupplier.injectDestinationOAuthParameters(
        destinationConnection.getDestinationDefinitionId(),
        destinationConnection.getWorkspaceId(),
        destinationConnection.getConfiguration());
    destinationConnection.withConfiguration(destinationConfiguration);

    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(sourceConnection.getSourceDefinitionId());
    final String sourceImageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());

    final StandardDestinationDefinition destinationDef =
        configRepository.getStandardDestinationDefinition(destinationConnection.getDestinationDefinitionId());
    final String destinationImageName = DockerUtils.getTaggedImageName(destinationDef.getDockerRepository(), destinationDef.getDockerImageTag());

    final List<StandardSyncOperation> standardSyncOperations = Lists.newArrayList();
    for (final var operationId : standardSync.getOperationIds()) {
      final StandardSyncOperation standardSyncOperation = configRepository.getStandardSyncOperation(operationId);
      standardSyncOperations.add(standardSyncOperation);
    }

    final Job job = schedulerJobClient.createOrGetActiveSyncJob(
        sourceConnection,
        destinationConnection,
        standardSync,
        sourceImageName,
        destinationImageName,
        standardSyncOperations);

    return JobConverter.getJobInfoRead(job);
  }

  public JobInfoRead resetConnection(final ConnectionIdRequestBody connectionIdRequestBody)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    final UUID connectionId = connectionIdRequestBody.getConnectionId();
    final StandardSync standardSync = configRepository.getStandardSync(connectionId);

    final DestinationConnection destination = configRepository.getDestinationConnection(standardSync.getDestinationId());

    final StandardDestinationDefinition destinationDef = configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId());
    final String destinationImageName = DockerUtils.getTaggedImageName(destinationDef.getDockerRepository(), destinationDef.getDockerImageTag());

    final List<StandardSyncOperation> standardSyncOperations = Lists.newArrayList();
    for (final var operationId : standardSync.getOperationIds()) {
      final StandardSyncOperation standardSyncOperation = configRepository.getStandardSyncOperation(operationId);
      standardSyncOperations.add(standardSyncOperation);
    }

    final Job job = schedulerJobClient.createOrGetActiveResetConnectionJob(destination, standardSync, destinationImageName, standardSyncOperations);

    return JobConverter.getJobInfoRead(job);
  }

  public ConnectionState getState(final ConnectionIdRequestBody connectionIdRequestBody) throws IOException {
    final Optional<State> currentState = jobPersistence.getCurrentState(connectionIdRequestBody.getConnectionId());
    LOGGER.info("currentState server: {}", currentState);

    final ConnectionState connectionState = new ConnectionState()
        .connectionId(connectionIdRequestBody.getConnectionId());

    currentState.ifPresent(state -> connectionState.state(state.getState()));

    return connectionState;
  }

  public JobInfoRead cancelJob(final JobIdRequestBody jobIdRequestBody) throws IOException {
    final long jobId = jobIdRequestBody.getId();

    // prevent this job from being scheduled again
    jobPersistence.cancelJob(jobId);
    cancelTemporalWorkflowIfPresent(jobId);

    final Job job = jobPersistence.getJob(jobId);
    jobNotifier.failJob("job was cancelled", job);
    return JobConverter.getJobInfoRead(job);
  }

  private void cancelTemporalWorkflowIfPresent(final long jobId) throws IOException {
    final var latestAttemptId = jobPersistence.getJob(jobId).getAttempts().size() - 1; // attempts ids are monotonically increasing starting from 0
    // and
    // specific to a job id, allowing us to do this.
    final var workflowId = jobPersistence.getAttemptTemporalWorkflowId(jobId, latestAttemptId);

    if (workflowId.isPresent()) {
      LOGGER.info("Cancelling workflow: {}", workflowId);
      final WorkflowExecution workflowExecution = WorkflowExecution.newBuilder()
          .setWorkflowId(workflowId.get())
          .build();
      final RequestCancelWorkflowExecutionRequest cancelRequest = RequestCancelWorkflowExecutionRequest.newBuilder()
          .setWorkflowExecution(workflowExecution)
          .setNamespace(TemporalUtils.DEFAULT_NAMESPACE)
          .build();
      temporalService.blockingStub().requestCancelWorkflowExecution(cancelRequest);
    }
  }

  private CheckConnectionRead reportConnectionStatus(final SynchronousResponse<StandardCheckConnectionOutput> response) {
    final CheckConnectionRead checkConnectionRead = new CheckConnectionRead()
        .jobInfo(JobConverter.getSynchronousJobRead(response));

    if (response.isSuccess()) {
      checkConnectionRead
          .status(Enums.convertTo(response.getOutput().getStatus(), StatusEnum.class))
          .message(response.getOutput().getMessage());
    } else {
      checkConnectionRead
          .status(StatusEnum.FAILED)
          .message("Check Connection Failed!");
    }

    return checkConnectionRead;
  }

  private ConnectorSpecification getSpecFromSourceDefinitionId(final UUID sourceDefId)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(sourceDefId);
    return specFetcher.getSpec(sourceDef);
  }

  private ConnectorSpecification getSpecFromDestinationDefinitionId(final UUID destDefId)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    final StandardDestinationDefinition destinationDef = configRepository.getStandardDestinationDefinition(destDefId);
    return specFetcher.getSpec(destinationDef);
  }

}
