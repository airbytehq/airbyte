/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Charsets;
import com.google.common.collect.Lists;
import com.google.common.hash.HashFunction;
import com.google.common.hash.Hashing;
import io.airbyte.api.model.AdvancedAuth;
import io.airbyte.api.model.AuthSpecification;
import io.airbyte.api.model.CheckConnectionRead;
import io.airbyte.api.model.CheckConnectionRead.StatusEnum;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.ConnectionState;
import io.airbyte.api.model.DestinationCoreConfig;
import io.airbyte.api.model.DestinationDefinitionIdWithWorkspaceId;
import io.airbyte.api.model.DestinationDefinitionSpecificationRead;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationSyncMode;
import io.airbyte.api.model.DestinationUpdate;
import io.airbyte.api.model.JobConfigType;
import io.airbyte.api.model.JobIdRequestBody;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.LogRead;
import io.airbyte.api.model.SourceCoreConfig;
import io.airbyte.api.model.SourceDefinitionIdWithWorkspaceId;
import io.airbyte.api.model.SourceDefinitionSpecificationRead;
import io.airbyte.api.model.SourceDiscoverSchemaRead;
import io.airbyte.api.model.SourceDiscoverSchemaRequestBody;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceUpdate;
import io.airbyte.api.model.SynchronousJobRead;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ActorCatalog;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.State;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.EventRunner;
import io.airbyte.scheduler.client.SchedulerJobClient;
import io.airbyte.scheduler.client.SynchronousJobMetadata;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.server.converters.ConfigurationUpdate;
import io.airbyte.server.converters.JobConverter;
import io.airbyte.server.converters.OauthModelConverter;
import io.airbyte.server.handlers.helpers.CatalogConverter;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.temporal.TemporalClient.ManualSyncSubmissionResult;
import io.airbyte.workers.temporal.TemporalUtils;
import io.temporal.api.common.v1.WorkflowExecution;
import io.temporal.api.workflowservice.v1.RequestCancelWorkflowExecutionRequest;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SchedulerHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(SchedulerHandler.class);
  private static final HashFunction HASH_FUNCTION = Hashing.md5();

  private final ConfigRepository configRepository;
  private final SecretsRepositoryWriter secretsRepositoryWriter;
  private final SchedulerJobClient schedulerJobClient;
  private final SynchronousSchedulerClient synchronousSchedulerClient;
  private final ConfigurationUpdate configurationUpdate;
  private final JsonSchemaValidator jsonSchemaValidator;
  private final JobPersistence jobPersistence;
  private final JobNotifier jobNotifier;
  private final WorkflowServiceStubs temporalService;
  private final OAuthConfigSupplier oAuthConfigSupplier;
  private final JobConverter jobConverter;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;
  private final EventRunner eventRunner;
  private final FeatureFlags featureFlags;

  public SchedulerHandler(final ConfigRepository configRepository,
                          final SecretsRepositoryReader secretsRepositoryReader,
                          final SecretsRepositoryWriter secretsRepositoryWriter,
                          final SchedulerJobClient schedulerJobClient,
                          final SynchronousSchedulerClient synchronousSchedulerClient,
                          final JobPersistence jobPersistence,
                          final JobNotifier jobNotifier,
                          final WorkflowServiceStubs temporalService,
                          final OAuthConfigSupplier oAuthConfigSupplier,
                          final WorkerEnvironment workerEnvironment,
                          final LogConfigs logConfigs,
                          final EventRunner eventRunner,
                          final FeatureFlags featureFlags) {
    this(
        configRepository,
        secretsRepositoryWriter,
        secretsRepositoryReader,
        schedulerJobClient,
        synchronousSchedulerClient,
        new ConfigurationUpdate(configRepository, secretsRepositoryReader),
        new JsonSchemaValidator(),
        jobPersistence,
        jobNotifier,
        temporalService,
        oAuthConfigSupplier,
        workerEnvironment,
        logConfigs,
        eventRunner,
        featureFlags,
        new JobConverter(workerEnvironment, logConfigs));
  }

  @VisibleForTesting
  SchedulerHandler(final ConfigRepository configRepository,
                   final SecretsRepositoryWriter secretsRepositoryWriter,
                   final SecretsRepositoryReader secretsRepositoryReader,
                   final SchedulerJobClient schedulerJobClient,
                   final SynchronousSchedulerClient synchronousSchedulerClient,
                   final ConfigurationUpdate configurationUpdate,
                   final JsonSchemaValidator jsonSchemaValidator,
                   final JobPersistence jobPersistence,
                   final JobNotifier jobNotifier,
                   final WorkflowServiceStubs temporalService,
                   final OAuthConfigSupplier oAuthConfigSupplier,
                   final WorkerEnvironment workerEnvironment,
                   final LogConfigs logConfigs,
                   final EventRunner eventRunner,
                   final FeatureFlags featureFlags,
                   final JobConverter jobConverter) {
    this.configRepository = configRepository;
    this.secretsRepositoryWriter = secretsRepositoryWriter;
    this.schedulerJobClient = schedulerJobClient;
    this.synchronousSchedulerClient = synchronousSchedulerClient;
    this.configurationUpdate = configurationUpdate;
    this.jsonSchemaValidator = jsonSchemaValidator;
    this.jobPersistence = jobPersistence;
    this.jobNotifier = jobNotifier;
    this.temporalService = temporalService;
    this.oAuthConfigSupplier = oAuthConfigSupplier;
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
    this.eventRunner = eventRunner;
    this.featureFlags = featureFlags;
    this.jobConverter = jobConverter;
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
    final var partialConfig = secretsRepositoryWriter.statefulSplitEphemeralSecrets(
        sourceConfig.getConnectionConfiguration(),
        sourceDef.getSpec());

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
    final var partialConfig = secretsRepositoryWriter.statefulSplitEphemeralSecrets(
        destinationConfig.getConnectionConfiguration(),
        destDef.getSpec());

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

  public SourceDiscoverSchemaRead discoverSchemaForSourceFromSourceId(final SourceDiscoverSchemaRequestBody discoverSchemaRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final SourceConnection source = configRepository.getSourceConnection(discoverSchemaRequestBody.getSourceId());
    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(source.getSourceDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());

    final String configHash = HASH_FUNCTION.hashBytes(Jsons.serialize(source.getConfiguration()).getBytes(
        Charsets.UTF_8)).toString();
    final String connectorVersion = sourceDef.getDockerImageTag();
    final Optional<ActorCatalog> currentCatalog =
        configRepository.getActorCatalog(discoverSchemaRequestBody.getSourceId(), connectorVersion, configHash);
    final boolean bustActorCatalogCache = discoverSchemaRequestBody.getDisableCache() != null && discoverSchemaRequestBody.getDisableCache();
    if (currentCatalog.isEmpty() || bustActorCatalogCache) {
      final SynchronousResponse<AirbyteCatalog> response = synchronousSchedulerClient.createDiscoverSchemaJob(source, imageName);
      final SourceDiscoverSchemaRead returnValue = discoverJobToOutput(response);
      if (response.isSuccess()) {
        final UUID catalogId = configRepository.writeActorCatalogFetchEvent(response.getOutput(), source.getSourceId(), connectorVersion, configHash);
        returnValue.catalogId(catalogId);
      }
      return returnValue;
    }
    final AirbyteCatalog airbyteCatalog = Jsons.object(currentCatalog.get().getCatalog(), AirbyteCatalog.class);
    final SynchronousJobRead emptyJob = new SynchronousJobRead()
        .configId("NoConfiguration")
        .configType(JobConfigType.DISCOVER_SCHEMA)
        .id(UUID.randomUUID())
        .createdAt(0L)
        .endedAt(0L)
        .logs(new LogRead().logLines(new ArrayList<>()))
        .succeeded(true);
    return new SourceDiscoverSchemaRead()
        .catalog(CatalogConverter.toApi(airbyteCatalog))
        .jobInfo(emptyJob)
        .catalogId(currentCatalog.get().getId());
  }

  public SourceDiscoverSchemaRead discoverSchemaForSourceFromSourceCreate(final SourceCoreConfig sourceCreate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(sourceCreate.getSourceDefinitionId());
    final var partialConfig = secretsRepositoryWriter.statefulSplitEphemeralSecrets(
        sourceCreate.getConnectionConfiguration(),
        sourceDef.getSpec());

    final String imageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());
    // todo (cgardens) - narrow the struct passed to the client. we are not setting fields that are
    // technically declared as required.
    final SourceConnection source = new SourceConnection()
        .withSourceDefinitionId(sourceCreate.getSourceDefinitionId())
        .withConfiguration(partialConfig);
    final SynchronousResponse<AirbyteCatalog> response = synchronousSchedulerClient.createDiscoverSchemaJob(source, imageName);
    return discoverJobToOutput(response);
  }

  private SourceDiscoverSchemaRead discoverJobToOutput(final SynchronousResponse<AirbyteCatalog> response) {
    final SourceDiscoverSchemaRead sourceDiscoverSchemaRead = new SourceDiscoverSchemaRead()
        .jobInfo(jobConverter.getSynchronousJobRead(response));

    if (response.isSuccess()) {
      sourceDiscoverSchemaRead.catalog(CatalogConverter.toApi(response.getOutput()));
    }

    return sourceDiscoverSchemaRead;
  }

  public SourceDefinitionSpecificationRead getSourceDefinitionSpecification(final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID sourceDefinitionId = sourceDefinitionIdWithWorkspaceId.getSourceDefinitionId();
    final StandardSourceDefinition source = configRepository.getStandardSourceDefinition(sourceDefinitionId);
    final ConnectorSpecification spec = source.getSpec();
    final SourceDefinitionSpecificationRead specRead = new SourceDefinitionSpecificationRead()
        .jobInfo(jobConverter.getSynchronousJobRead(SynchronousJobMetadata.mock(ConfigType.GET_SPEC)))
        .connectionSpecification(spec.getConnectionSpecification())
        .documentationUrl(spec.getDocumentationUrl().toString())
        .sourceDefinitionId(sourceDefinitionId);

    final Optional<AuthSpecification> authSpec = OauthModelConverter.getAuthSpec(spec);
    authSpec.ifPresent(specRead::setAuthSpecification);

    final Optional<AdvancedAuth> advancedAuth = OauthModelConverter.getAdvancedAuth(spec);
    advancedAuth.ifPresent(specRead::setAdvancedAuth);

    return specRead;
  }

  public DestinationDefinitionSpecificationRead getDestinationSpecification(
                                                                            final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID destinationDefinitionId = destinationDefinitionIdWithWorkspaceId.getDestinationDefinitionId();
    final StandardDestinationDefinition destination = configRepository.getStandardDestinationDefinition(destinationDefinitionId);
    final ConnectorSpecification spec = destination.getSpec();

    final DestinationDefinitionSpecificationRead specRead = new DestinationDefinitionSpecificationRead()
        .jobInfo(jobConverter.getSynchronousJobRead(SynchronousJobMetadata.mock(ConfigType.GET_SPEC)))
        .supportedDestinationSyncModes(Enums.convertListTo(spec.getSupportedDestinationSyncModes(), DestinationSyncMode.class))
        .connectionSpecification(spec.getConnectionSpecification())
        .documentationUrl(spec.getDocumentationUrl().toString())
        .supportsNormalization(spec.getSupportsNormalization())
        .supportsDbt(spec.getSupportsDBT())
        .destinationDefinitionId(destinationDefinitionId);

    final Optional<AuthSpecification> authSpec = OauthModelConverter.getAuthSpec(spec);
    authSpec.ifPresent(specRead::setAuthSpecification);

    final Optional<AdvancedAuth> advancedAuth = OauthModelConverter.getAdvancedAuth(spec);
    advancedAuth.ifPresent(specRead::setAdvancedAuth);

    return specRead;
  }

  public JobInfoRead syncConnection(final ConnectionIdRequestBody connectionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    if (featureFlags.usesNewScheduler()) {
      return createManualRun(connectionIdRequestBody.getConnectionId());
    }
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
        standardSyncOperations,
        sourceDef.getResourceRequirements(),
        destinationDef.getResourceRequirements());

    return jobConverter.getJobInfoRead(job);
  }

  public JobInfoRead resetConnection(final ConnectionIdRequestBody connectionIdRequestBody)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    if (featureFlags.usesNewScheduler()) {
      return resetConnectionWithNewScheduler(connectionIdRequestBody.getConnectionId());
    }
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

    return jobConverter.getJobInfoRead(job);
  }

  public ConnectionState getState(final ConnectionIdRequestBody connectionIdRequestBody) throws IOException {
    final Optional<State> currentState = configRepository.getConnectionState(connectionIdRequestBody.getConnectionId());
    LOGGER.info("currentState server: {}", currentState);

    final ConnectionState connectionState = new ConnectionState()
        .connectionId(connectionIdRequestBody.getConnectionId());

    currentState.ifPresent(state -> connectionState.state(state.getState()));

    return connectionState;
  }

  // todo (cgardens) - this method needs a test.
  public JobInfoRead cancelJob(final JobIdRequestBody jobIdRequestBody) throws IOException {
    if (featureFlags.usesNewScheduler()) {
      return createNewSchedulerCancellation(jobIdRequestBody.getId());
    }

    final long jobId = jobIdRequestBody.getId();

    // prevent this job from being scheduled again
    jobPersistence.cancelJob(jobId);
    cancelTemporalWorkflowIfPresent(jobId);

    final Job job = jobPersistence.getJob(jobId);
    jobNotifier.failJob("job was cancelled", job);
    return jobConverter.getJobInfoRead(job);
  }

  private void cancelTemporalWorkflowIfPresent(final long jobId) throws IOException {
    // attempts ids are monotonically increasing starting from 0 and specific to a job id, allowing us
    // to do this.
    final var latestAttemptId = jobPersistence.getJob(jobId).getAttempts().size() - 1;
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
        .jobInfo(jobConverter.getSynchronousJobRead(response));

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
    return sourceDef.getSpec();
  }

  private ConnectorSpecification getSpecFromDestinationDefinitionId(final UUID destDefId)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    final StandardDestinationDefinition destinationDef = configRepository.getStandardDestinationDefinition(destDefId);
    return destinationDef.getSpec();
  }

  private JobInfoRead createNewSchedulerCancellation(final Long id) throws IOException {
    final Job job = jobPersistence.getJob(id);

    final ManualSyncSubmissionResult cancellationSubmissionResult = eventRunner.startNewCancelation(UUID.fromString(job.getScope()));

    if (cancellationSubmissionResult.getFailingReason().isPresent()) {
      throw new IllegalStateException(cancellationSubmissionResult.getFailingReason().get());
    }

    final Job cancelledJob = jobPersistence.getJob(id);
    return jobConverter.getJobInfoRead(cancelledJob);
  }

  private JobInfoRead createManualRun(final UUID connectionId) throws IOException {
    final ManualSyncSubmissionResult manualSyncSubmissionResult = eventRunner.startNewManualSync(connectionId);

    if (manualSyncSubmissionResult.getFailingReason().isPresent()) {
      throw new IllegalStateException(manualSyncSubmissionResult.getFailingReason().get());
    }

    final Job job = jobPersistence.getJob(manualSyncSubmissionResult.getJobId().get());

    return jobConverter.getJobInfoRead(job);
  }

  private JobInfoRead resetConnectionWithNewScheduler(final UUID connectionId) throws IOException {
    final ManualSyncSubmissionResult manualSyncSubmissionResult = eventRunner.resetConnection(connectionId);

    if (manualSyncSubmissionResult.getFailingReason().isPresent()) {
      throw new IllegalStateException(manualSyncSubmissionResult.getFailingReason().get());
    }

    final Job job = jobPersistence.getJob(manualSyncSubmissionResult.getJobId().get());

    return jobConverter.getJobInfoRead(job);
  }

}
