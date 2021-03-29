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

package io.airbyte.server.handlers;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.api.model.CheckConnectionRead;
import io.airbyte.api.model.CheckConnectionRead.StatusEnum;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.DestinationCoreConfig;
import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationDefinitionSpecificationRead;
import io.airbyte.api.model.DestinationIdRequestBody;
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
import io.airbyte.commons.io.IOs;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.SchedulerJobClient;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.converters.CatalogConverter;
import io.airbyte.server.converters.ConfigurationUpdate;
import io.airbyte.server.converters.JobConverter;
import io.airbyte.server.converters.SpecFetcher;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import io.airbyte.workers.temporal.TemporalUtils;
import io.temporal.api.common.v1.WorkflowExecution;
import io.temporal.api.workflowservice.v1.RequestCancelWorkflowExecutionRequest;
import java.io.IOException;
import java.nio.file.Path;
import java.util.UUID;

public class SchedulerHandler {

  private final ConfigRepository configRepository;
  private final SchedulerJobClient schedulerJobClient;
  private final SynchronousSchedulerClient synchronousSchedulerClient;
  private final SpecFetcher specFetcher;
  private final ConfigurationUpdate configurationUpdate;
  private final JsonSchemaValidator jsonSchemaValidator;
  private final JobPersistence jobPersistence;
  private final Path workspaceRoot;

  public SchedulerHandler(ConfigRepository configRepository,
                          SchedulerJobClient schedulerJobClient,
                          SynchronousSchedulerClient synchronousSchedulerClient,
                          JobPersistence jobPersistence,
                          Path workspaceRoot) {
    this(
        configRepository,
        schedulerJobClient,
        synchronousSchedulerClient,
        new ConfigurationUpdate(configRepository, new SpecFetcher(synchronousSchedulerClient)),
        new JsonSchemaValidator(),
        new SpecFetcher(synchronousSchedulerClient),
        jobPersistence,
        workspaceRoot);
  }

  @VisibleForTesting
  SchedulerHandler(ConfigRepository configRepository,
                   SchedulerJobClient schedulerJobClient,
                   SynchronousSchedulerClient synchronousSchedulerClient,
                   ConfigurationUpdate configurationUpdate,
                   JsonSchemaValidator jsonSchemaValidator,
                   SpecFetcher specFetcher,
                   JobPersistence jobPersistence,
                   Path workspaceRoot) {
    this.configRepository = configRepository;
    this.schedulerJobClient = schedulerJobClient;
    this.synchronousSchedulerClient = synchronousSchedulerClient;
    this.configurationUpdate = configurationUpdate;
    this.jsonSchemaValidator = jsonSchemaValidator;
    this.specFetcher = specFetcher;
    this.jobPersistence = jobPersistence;
    this.workspaceRoot = workspaceRoot;
  }

  public CheckConnectionRead checkSourceConnectionFromSourceId(SourceIdRequestBody sourceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final SourceConnection source = configRepository.getSourceConnection(sourceIdRequestBody.getSourceId());
    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(source.getSourceDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());

    return reportConnectionStatus(synchronousSchedulerClient.createSourceCheckConnectionJob(source, imageName));
  }

  public CheckConnectionRead checkSourceConnectionFromSourceCreate(SourceCoreConfig sourceConfig)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(sourceConfig.getSourceDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());
    // todo (cgardens) - narrow the struct passed to the client. we are not setting fields that are
    // technically declared as required.
    final SourceConnection source = new SourceConnection()
        .withSourceDefinitionId(sourceConfig.getSourceDefinitionId())
        .withConfiguration(sourceConfig.getConnectionConfiguration());

    return reportConnectionStatus(synchronousSchedulerClient.createSourceCheckConnectionJob(source, imageName));
  }

  public CheckConnectionRead checkSourceConnectionFromSourceIdForUpdate(SourceUpdate sourceUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final SourceConnection updatedSource = configurationUpdate.source(sourceUpdate.getSourceId(), sourceUpdate.getConnectionConfiguration());

    final ConnectorSpecification spec = getSpecFromSourceDefinitionId(updatedSource.getSourceDefinitionId());
    jsonSchemaValidator.validate(spec.getConnectionSpecification(), updatedSource.getConfiguration());

    final SourceCoreConfig sourceCoreConfig = new SourceCoreConfig()
        .connectionConfiguration(updatedSource.getConfiguration())
        .sourceDefinitionId(updatedSource.getSourceDefinitionId());

    return checkSourceConnectionFromSourceCreate(sourceCoreConfig);
  }

  public CheckConnectionRead checkDestinationConnectionFromDestinationId(DestinationIdRequestBody destinationIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final DestinationConnection destination = configRepository.getDestinationConnection(destinationIdRequestBody.getDestinationId());
    final StandardDestinationDefinition destinationDef = configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(destinationDef.getDockerRepository(), destinationDef.getDockerImageTag());
    return reportConnectionStatus(synchronousSchedulerClient.createDestinationCheckConnectionJob(destination, imageName));
  }

  public CheckConnectionRead checkDestinationConnectionFromDestinationCreate(DestinationCoreConfig destinationConfig)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardDestinationDefinition destDef = configRepository.getStandardDestinationDefinition(destinationConfig.getDestinationDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(destDef.getDockerRepository(), destDef.getDockerImageTag());
    // todo (cgardens) - narrow the struct passed to the client. we are not setting fields that are
    // technically declared as required.
    final DestinationConnection destination = new DestinationConnection()
        .withDestinationDefinitionId(destinationConfig.getDestinationDefinitionId())
        .withConfiguration(destinationConfig.getConnectionConfiguration());
    return reportConnectionStatus(synchronousSchedulerClient.createDestinationCheckConnectionJob(destination, imageName));
  }

  public CheckConnectionRead checkDestinationConnectionFromDestinationIdForUpdate(DestinationUpdate destinationUpdate)
      throws JsonValidationException, IOException, ConfigNotFoundException {
    final DestinationConnection updatedDestination = configurationUpdate
        .destination(destinationUpdate.getDestinationId(), destinationUpdate.getConnectionConfiguration());

    final ConnectorSpecification spec = getSpecFromDestinationDefinitionId(updatedDestination.getDestinationDefinitionId());
    jsonSchemaValidator.validate(spec.getConnectionSpecification(), updatedDestination.getConfiguration());

    final DestinationCoreConfig destinationCoreConfig = new DestinationCoreConfig()
        .connectionConfiguration(updatedDestination.getConfiguration())
        .destinationDefinitionId(updatedDestination.getDestinationDefinitionId());

    return checkDestinationConnectionFromDestinationCreate(destinationCoreConfig);
  }

  public SourceDiscoverSchemaRead discoverSchemaForSourceFromSourceId(SourceIdRequestBody sourceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final SourceConnection source = configRepository.getSourceConnection(sourceIdRequestBody.getSourceId());
    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(source.getSourceDefinitionId());
    final String imageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());
    final SynchronousResponse<AirbyteCatalog> response = synchronousSchedulerClient.createDiscoverSchemaJob(source, imageName);
    return discoverJobToOutput(response);
  }

  public SourceDiscoverSchemaRead discoverSchemaForSourceFromSourceCreate(SourceCoreConfig sourceCreate)
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

  private static SourceDiscoverSchemaRead discoverJobToOutput(SynchronousResponse<AirbyteCatalog> response) {
    final SourceDiscoverSchemaRead sourceDiscoverSchemaRead = new SourceDiscoverSchemaRead()
        .jobInfo(JobConverter.getSynchronousJobRead(response));

    if (response.isSuccess()) {
      sourceDiscoverSchemaRead.catalog(CatalogConverter.toApi(response.getOutput()));
    }

    return sourceDiscoverSchemaRead;
  }

  public SourceDefinitionSpecificationRead getSourceDefinitionSpecification(SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID sourceDefinitionId = sourceDefinitionIdRequestBody.getSourceDefinitionId();
    final StandardSourceDefinition source = configRepository.getStandardSourceDefinition(sourceDefinitionId);
    final String imageName = DockerUtils.getTaggedImageName(source.getDockerRepository(), source.getDockerImageTag());
    final SynchronousResponse<ConnectorSpecification> response = getConnectorSpecification(imageName);
    final ConnectorSpecification spec = response.getOutput();
    return new SourceDefinitionSpecificationRead()
        .jobInfo(JobConverter.getSynchronousJobRead(response))
        .connectionSpecification(spec.getConnectionSpecification())
        .documentationUrl(spec.getDocumentationUrl().toString())
        .sourceDefinitionId(sourceDefinitionId);
  }

  public DestinationDefinitionSpecificationRead getDestinationSpecification(DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID destinationDefinitionId = destinationDefinitionIdRequestBody.getDestinationDefinitionId();
    final StandardDestinationDefinition destination = configRepository.getStandardDestinationDefinition(destinationDefinitionId);
    final String imageName = DockerUtils.getTaggedImageName(destination.getDockerRepository(), destination.getDockerImageTag());
    final SynchronousResponse<ConnectorSpecification> response = getConnectorSpecification(imageName);
    final ConnectorSpecification spec = response.getOutput();
    return new DestinationDefinitionSpecificationRead()
        .jobInfo(JobConverter.getSynchronousJobRead(response))
        .connectionSpecification(spec.getConnectionSpecification())
        .documentationUrl(spec.getDocumentationUrl().toString())
        .destinationDefinitionId(destinationDefinitionId);
  }

  public SynchronousResponse<ConnectorSpecification> getConnectorSpecification(String dockerImage) throws IOException {
    return synchronousSchedulerClient.createGetSpecJob(dockerImage);
  }

  public JobInfoRead syncConnection(final ConnectionIdRequestBody connectionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID connectionId = connectionIdRequestBody.getConnectionId();
    final StandardSync standardSync = configRepository.getStandardSync(connectionId);

    final SourceConnection source = configRepository.getSourceConnection(standardSync.getSourceId());
    final DestinationConnection destination = configRepository.getDestinationConnection(standardSync.getDestinationId());

    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(source.getSourceDefinitionId());
    final String sourceImageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());

    final StandardDestinationDefinition destinationDef = configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId());
    final String destinationImageName = DockerUtils.getTaggedImageName(destinationDef.getDockerRepository(), destinationDef.getDockerImageTag());

    final Job job = schedulerJobClient.createOrGetActiveSyncJob(
        source,
        destination,
        standardSync,
        sourceImageName,
        destinationImageName);

    return JobConverter.getJobInfoRead(job);
  }

  public JobInfoRead resetConnection(final ConnectionIdRequestBody connectionIdRequestBody)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    final UUID connectionId = connectionIdRequestBody.getConnectionId();
    final StandardSync standardSync = configRepository.getStandardSync(connectionId);

    final DestinationConnection destination = configRepository.getDestinationConnection(standardSync.getDestinationId());

    final StandardDestinationDefinition destinationDef = configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId());
    final String destinationImageName = DockerUtils.getTaggedImageName(destinationDef.getDockerRepository(), destinationDef.getDockerImageTag());

    final Job job = schedulerJobClient.createOrGetActiveResetConnectionJob(destination, standardSync, destinationImageName);

    return JobConverter.getJobInfoRead(job);
  }

  public JobInfoRead cancelJob(JobIdRequestBody jobIdRequestBody) throws IOException {
    final long jobId = jobIdRequestBody.getId();

    // first prevent this job from being scheduled again
    jobPersistence.cancelJob(jobId);

    // second cancel the temporal execution
    // TODO: this is hacky, resolve https://github.com/airbytehq/airbyte/issues/2564 to avoid this
    // behavior
    final Path attemptParentDir = WorkerUtils.getJobRoot(workspaceRoot, String.valueOf(jobId), 0L).getParent();
    final String workflowId = IOs.readFile(attemptParentDir, TemporalAttemptExecution.WORKFLOW_ID_FILENAME);
    final WorkflowExecution workflowExecution = WorkflowExecution.newBuilder()
        .setWorkflowId(workflowId)
        .build();
    final RequestCancelWorkflowExecutionRequest cancelRequest = RequestCancelWorkflowExecutionRequest.newBuilder()
        .setWorkflowExecution(workflowExecution)
        .setNamespace(TemporalUtils.DEFAULT_NAMESPACE)
        .build();

    TemporalUtils.TEMPORAL_SERVICE.blockingStub().requestCancelWorkflowExecution(cancelRequest);

    return JobConverter.getJobInfoRead(jobPersistence.getJob(jobId));
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

  private ConnectorSpecification getSpecFromSourceDefinitionId(UUID sourceDefId)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    final StandardSourceDefinition sourceDef = configRepository.getStandardSourceDefinition(sourceDefId);
    final String imageName = DockerUtils.getTaggedImageName(sourceDef.getDockerRepository(), sourceDef.getDockerImageTag());
    return specFetcher.execute(imageName);
  }

  private ConnectorSpecification getSpecFromDestinationDefinitionId(UUID destDefId)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    final StandardDestinationDefinition destinationDef = configRepository.getStandardDestinationDefinition(destDefId);
    final String imageName = DockerUtils.getTaggedImageName(destinationDef.getDockerRepository(), destinationDef.getDockerImageTag());
    return specFetcher.execute(imageName);
  }

}
