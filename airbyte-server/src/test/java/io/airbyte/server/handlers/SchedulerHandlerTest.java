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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import io.airbyte.api.model.CheckConnectionRead;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.ConnectionState;
import io.airbyte.api.model.DestinationCoreConfig;
import io.airbyte.api.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationUpdate;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.SourceCoreConfig;
import io.airbyte.api.model.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.SourceDiscoverSchemaRead;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceUpdate;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.OperatorNormalization;
import io.airbyte.config.OperatorNormalization.Option;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOperation.OperatorType;
import io.airbyte.config.State;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.scheduler.client.SchedulerJobClient;
import io.airbyte.scheduler.client.SynchronousJobMetadata;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.converters.ConfigurationUpdate;
import io.airbyte.server.converters.SpecFetcher;
import io.airbyte.server.helpers.ConnectionHelpers;
import io.airbyte.server.helpers.DestinationHelpers;
import io.airbyte.server.helpers.SourceHelpers;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.io.IOException;
import java.net.URI;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

@SuppressWarnings("unchecked")
class SchedulerHandlerTest {

  private static final String SOURCE_DOCKER_REPO = "srcimage";
  private static final String SOURCE_DOCKER_TAG = "tag";
  private static final String SOURCE_DOCKER_IMAGE = DockerUtils.getTaggedImageName(SOURCE_DOCKER_REPO, SOURCE_DOCKER_TAG);

  private static final String DESTINATION_DOCKER_REPO = "dstimage";
  private static final String DESTINATION_DOCKER_TAG = "tag";
  private static final String DESTINATION_DOCKER_IMAGE = DockerUtils.getTaggedImageName(DESTINATION_DOCKER_REPO, DESTINATION_DOCKER_TAG);

  private static final String OPERATION_NAME = "transfo";

  private static final SourceConnection SOURCE = new SourceConnection()
      .withName("my postgres db")
      .withWorkspaceId(UUID.randomUUID())
      .withSourceDefinitionId(UUID.randomUUID())
      .withSourceId(UUID.randomUUID())
      .withConfiguration(Jsons.emptyObject())
      .withTombstone(false);

  private static final DestinationConnection DESTINATION = new DestinationConnection()
      .withName("my db2 instance")
      .withWorkspaceId(UUID.randomUUID())
      .withDestinationDefinitionId(UUID.randomUUID())
      .withDestinationId(UUID.randomUUID())
      .withConfiguration(Jsons.emptyObject())
      .withTombstone(false);

  private static final ConnectorSpecification CONNECTION_SPECIFICATION = new ConnectorSpecification()
      .withDocumentationUrl(Exceptions.toRuntime(() -> new URI("https://google.com")))
      .withChangelogUrl(Exceptions.toRuntime(() -> new URI("https://google.com")))
      .withConnectionSpecification(Jsons.jsonNode(new HashMap<>()));

  private SchedulerHandler schedulerHandler;
  private ConfigRepository configRepository;
  private Job completedJob;
  private SchedulerJobClient schedulerJobClient;
  private SynchronousSchedulerClient synchronousSchedulerClient;
  private SynchronousResponse<?> jobResponse;
  private ConfigurationUpdate configurationUpdate;
  private JsonSchemaValidator jsonSchemaValidator;
  private SpecFetcher specFetcher;
  private JobPersistence jobPersistence;

  @BeforeEach
  void setup() {
    completedJob = mock(Job.class, RETURNS_DEEP_STUBS);
    jobResponse = mock(SynchronousResponse.class, RETURNS_DEEP_STUBS);
    configurationUpdate = mock(ConfigurationUpdate.class);
    jsonSchemaValidator = mock(JsonSchemaValidator.class);
    specFetcher = mock(SpecFetcher.class);
    when(completedJob.getStatus()).thenReturn(JobStatus.SUCCEEDED);
    when(completedJob.getConfig().getConfigType()).thenReturn(ConfigType.SYNC);
    when(completedJob.getScope()).thenReturn("sync:123");

    schedulerJobClient = spy(SchedulerJobClient.class);
    synchronousSchedulerClient = mock(SynchronousSchedulerClient.class);
    configRepository = mock(ConfigRepository.class);
    jobPersistence = mock(JobPersistence.class);
    final JobNotifier jobNotifier = mock(JobNotifier.class);

    schedulerHandler = new SchedulerHandler(
        configRepository,
        schedulerJobClient,
        synchronousSchedulerClient,
        configurationUpdate,
        jsonSchemaValidator,
        specFetcher,
        jobPersistence,
        jobNotifier,
        mock(WorkflowServiceStubs.class));
  }

  @Test
  void testCheckSourceConnectionFromSourceId() throws JsonValidationException, IOException, ConfigNotFoundException {
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    final SourceIdRequestBody request = new SourceIdRequestBody().sourceId(source.getSourceId());

    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceDefinitionId(source.getSourceDefinitionId()));
    when(configRepository.getSourceConnection(source.getSourceId())).thenReturn(source);
    when(synchronousSchedulerClient.createSourceCheckConnectionJob(source, SOURCE_DOCKER_IMAGE))
        .thenReturn((SynchronousResponse<StandardCheckConnectionOutput>) jobResponse);

    schedulerHandler.checkSourceConnectionFromSourceId(request);

    verify(configRepository).getSourceConnection(source.getSourceId());
    verify(synchronousSchedulerClient).createSourceCheckConnectionJob(source, SOURCE_DOCKER_IMAGE);
  }

  @Test
  void testCheckSourceConnectionFromSourceCreate() throws JsonValidationException, IOException, ConfigNotFoundException {
    final SourceConnection source = new SourceConnection()
        .withSourceDefinitionId(SOURCE.getSourceDefinitionId())
        .withConfiguration(SOURCE.getConfiguration());

    final SourceCoreConfig sourceCoreConfig = new SourceCoreConfig()
        .sourceDefinitionId(source.getSourceDefinitionId())
        .connectionConfiguration(source.getConfiguration());

    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceDefinitionId(source.getSourceDefinitionId()));
    when(synchronousSchedulerClient.createSourceCheckConnectionJob(source, SOURCE_DOCKER_IMAGE))
        .thenReturn((SynchronousResponse<StandardCheckConnectionOutput>) jobResponse);

    schedulerHandler.checkSourceConnectionFromSourceCreate(sourceCoreConfig);

    verify(synchronousSchedulerClient).createSourceCheckConnectionJob(source, SOURCE_DOCKER_IMAGE);
  }

  @Test
  void testCheckSourceConnectionFromUpdate() throws IOException, JsonValidationException, ConfigNotFoundException {
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    final SourceUpdate sourceUpdate = new SourceUpdate()
        .name(source.getName())
        .sourceId(source.getSourceId())
        .connectionConfiguration(source.getConfiguration());
    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(DESTINATION_DOCKER_REPO)
            .withDockerImageTag(DESTINATION_DOCKER_TAG)
            .withSourceDefinitionId(source.getSourceDefinitionId()));
    when(configRepository.getSourceConnection(source.getSourceId())).thenReturn(source);
    when(configurationUpdate.source(source.getSourceId(), source.getName(), sourceUpdate.getConnectionConfiguration())).thenReturn(source);
    when(specFetcher.execute(DESTINATION_DOCKER_IMAGE)).thenReturn(CONNECTION_SPECIFICATION);
    final SourceConnection submittedSource = new SourceConnection()
        .withSourceDefinitionId(source.getSourceDefinitionId())
        .withConfiguration(source.getConfiguration());
    when(synchronousSchedulerClient.createSourceCheckConnectionJob(submittedSource, DESTINATION_DOCKER_IMAGE))
        .thenReturn((SynchronousResponse<StandardCheckConnectionOutput>) jobResponse);

    schedulerHandler.checkSourceConnectionFromSourceIdForUpdate(sourceUpdate);

    verify(jsonSchemaValidator).ensure(CONNECTION_SPECIFICATION.getConnectionSpecification(), source.getConfiguration());
    verify(synchronousSchedulerClient).createSourceCheckConnectionJob(submittedSource, DESTINATION_DOCKER_IMAGE);
  }

  @Test
  void testGetSourceSpec() throws JsonValidationException, IOException, ConfigNotFoundException {
    final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody = new SourceDefinitionIdRequestBody().sourceDefinitionId(UUID.randomUUID());

    final SynchronousResponse<ConnectorSpecification> specResponse = (SynchronousResponse<ConnectorSpecification>) jobResponse;
    when(configRepository.getStandardSourceDefinition(sourceDefinitionIdRequestBody.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withName("name")
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceDefinitionId(sourceDefinitionIdRequestBody.getSourceDefinitionId()));
    when(synchronousSchedulerClient.createGetSpecJob(SOURCE_DOCKER_IMAGE))
        .thenReturn(specResponse);
    when(specResponse.getOutput()).thenReturn(CONNECTION_SPECIFICATION);

    schedulerHandler.getSourceDefinitionSpecification(sourceDefinitionIdRequestBody);

    verify(configRepository).getStandardSourceDefinition(sourceDefinitionIdRequestBody.getSourceDefinitionId());
  }

  @Test
  void testGetDestinationSpec() throws JsonValidationException, IOException, ConfigNotFoundException {
    final DestinationDefinitionIdRequestBody destinationDefinitionIdRequestBody =
        new DestinationDefinitionIdRequestBody().destinationDefinitionId(UUID.randomUUID());

    final SynchronousResponse<ConnectorSpecification> specResponse = (SynchronousResponse<ConnectorSpecification>) this.jobResponse;
    when(configRepository.getStandardDestinationDefinition(destinationDefinitionIdRequestBody.getDestinationDefinitionId()))
        .thenReturn(new StandardDestinationDefinition()
            .withName("name")
            .withDockerRepository(DESTINATION_DOCKER_REPO)
            .withDockerImageTag(DESTINATION_DOCKER_TAG)
            .withDestinationDefinitionId(destinationDefinitionIdRequestBody.getDestinationDefinitionId()));
    when(synchronousSchedulerClient.createGetSpecJob(DESTINATION_DOCKER_IMAGE))
        .thenReturn(specResponse);
    when(specResponse.getOutput()).thenReturn(CONNECTION_SPECIFICATION);

    schedulerHandler.getDestinationSpecification(destinationDefinitionIdRequestBody);

    verify(configRepository).getStandardDestinationDefinition(destinationDefinitionIdRequestBody.getDestinationDefinitionId());
  }

  @Test
  public void testGetConnectorSpec() throws IOException {
    final SynchronousResponse<ConnectorSpecification> specResponse = (SynchronousResponse<ConnectorSpecification>) jobResponse;
    when(specResponse.getOutput()).thenReturn(CONNECTION_SPECIFICATION);
    when(synchronousSchedulerClient.createGetSpecJob(SOURCE_DOCKER_IMAGE))
        .thenReturn(specResponse);

    assertEquals(CONNECTION_SPECIFICATION, schedulerHandler.getConnectorSpecification(SOURCE_DOCKER_IMAGE).getOutput());
  }

  @Test
  void testCheckDestinationConnectionFromDestinationId() throws IOException, JsonValidationException, ConfigNotFoundException {
    final DestinationConnection destination = DestinationHelpers.generateDestination(UUID.randomUUID());
    final DestinationIdRequestBody request = new DestinationIdRequestBody().destinationId(destination.getDestinationId());

    when(configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId()))
        .thenReturn(new StandardDestinationDefinition()
            .withDockerRepository(DESTINATION_DOCKER_REPO)
            .withDockerImageTag(DESTINATION_DOCKER_TAG)
            .withDestinationDefinitionId(destination.getDestinationDefinitionId()));
    when(configRepository.getDestinationConnection(destination.getDestinationId())).thenReturn(destination);
    when(synchronousSchedulerClient.createDestinationCheckConnectionJob(destination, DESTINATION_DOCKER_IMAGE))
        .thenReturn((SynchronousResponse<StandardCheckConnectionOutput>) jobResponse);

    schedulerHandler.checkDestinationConnectionFromDestinationId(request);

    verify(configRepository).getDestinationConnection(destination.getDestinationId());
    verify(synchronousSchedulerClient).createDestinationCheckConnectionJob(destination, DESTINATION_DOCKER_IMAGE);
  }

  @Test
  void testCheckDestinationConnectionFromDestinationCreate() throws JsonValidationException, IOException, ConfigNotFoundException {
    final DestinationConnection destination = new DestinationConnection()
        .withDestinationDefinitionId(DESTINATION.getDestinationDefinitionId())
        .withConfiguration(DESTINATION.getConfiguration());

    final DestinationCoreConfig destinationCoreConfig = new DestinationCoreConfig()
        .destinationDefinitionId(destination.getDestinationDefinitionId())
        .connectionConfiguration(destination.getConfiguration());

    when(configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId()))
        .thenReturn(new StandardDestinationDefinition()
            .withDockerRepository(DESTINATION_DOCKER_REPO)
            .withDockerImageTag(DESTINATION_DOCKER_TAG)
            .withDestinationDefinitionId(destination.getDestinationDefinitionId()));

    when(synchronousSchedulerClient.createDestinationCheckConnectionJob(destination, DESTINATION_DOCKER_IMAGE))
        .thenReturn((SynchronousResponse<StandardCheckConnectionOutput>) jobResponse);

    schedulerHandler.checkDestinationConnectionFromDestinationCreate(destinationCoreConfig);

    verify(synchronousSchedulerClient).createDestinationCheckConnectionJob(destination, DESTINATION_DOCKER_IMAGE);
  }

  @Test
  void testCheckDestinationConnectionFromUpdate() throws IOException, JsonValidationException, ConfigNotFoundException {
    final DestinationConnection destination = DestinationHelpers.generateDestination(UUID.randomUUID());
    final DestinationUpdate destinationUpdate = new DestinationUpdate()
        .name(destination.getName())
        .destinationId(destination.getDestinationId())
        .connectionConfiguration(destination.getConfiguration());
    when(configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId()))
        .thenReturn(new StandardDestinationDefinition()
            .withDockerRepository(DESTINATION_DOCKER_REPO)
            .withDockerImageTag(DESTINATION_DOCKER_TAG)
            .withDestinationDefinitionId(destination.getDestinationDefinitionId()));
    when(configRepository.getDestinationConnection(destination.getDestinationId())).thenReturn(destination);
    when(configurationUpdate.destination(destination.getDestinationId(), destination.getName(), destinationUpdate.getConnectionConfiguration()))
        .thenReturn(destination);
    when(specFetcher.execute(DESTINATION_DOCKER_IMAGE)).thenReturn(CONNECTION_SPECIFICATION);
    final DestinationConnection submittedDestination = new DestinationConnection()
        .withDestinationDefinitionId(destination.getDestinationDefinitionId())
        .withConfiguration(destination.getConfiguration());
    when(synchronousSchedulerClient.createDestinationCheckConnectionJob(submittedDestination, DESTINATION_DOCKER_IMAGE))
        .thenReturn((SynchronousResponse<StandardCheckConnectionOutput>) jobResponse);

    schedulerHandler.checkDestinationConnectionFromDestinationIdForUpdate(destinationUpdate);

    verify(jsonSchemaValidator).ensure(CONNECTION_SPECIFICATION.getConnectionSpecification(), destination.getConfiguration());
    verify(synchronousSchedulerClient).createDestinationCheckConnectionJob(submittedDestination, DESTINATION_DOCKER_IMAGE);
  }

  @Test
  void testDiscoverSchemaForSourceFromSourceId() throws IOException, JsonValidationException, ConfigNotFoundException {
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    final SourceIdRequestBody request = new SourceIdRequestBody().sourceId(source.getSourceId());

    final SynchronousResponse<AirbyteCatalog> discoverResponse = (SynchronousResponse<AirbyteCatalog>) jobResponse;
    final SynchronousJobMetadata metadata = mock(SynchronousJobMetadata.class);
    when(discoverResponse.isSuccess()).thenReturn(true);
    when(discoverResponse.getOutput()).thenReturn(CatalogHelpers.createAirbyteCatalog("shoes", Field.of("sku", JsonSchemaPrimitive.STRING)));
    when(discoverResponse.getMetadata()).thenReturn(metadata);
    when(metadata.isSucceeded()).thenReturn(true);

    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceDefinitionId(source.getSourceDefinitionId()));
    when(configRepository.getSourceConnection(source.getSourceId())).thenReturn(source);
    when(synchronousSchedulerClient.createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE))
        .thenReturn(discoverResponse);

    final SourceDiscoverSchemaRead actual = schedulerHandler.discoverSchemaForSourceFromSourceId(request);

    assertNotNull(actual.getCatalog());
    assertNotNull(actual.getJobInfo());
    assertTrue(actual.getJobInfo().getSucceeded());
    verify(configRepository).getSourceConnection(source.getSourceId());
    verify(synchronousSchedulerClient).createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE);
  }

  @Test
  void testDiscoverSchemaForSourceFromSourceIdFailed() throws IOException, JsonValidationException, ConfigNotFoundException {
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    final SourceIdRequestBody request = new SourceIdRequestBody().sourceId(source.getSourceId());

    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceDefinitionId(source.getSourceDefinitionId()));
    when(configRepository.getSourceConnection(source.getSourceId())).thenReturn(source);
    when(synchronousSchedulerClient.createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE))
        .thenReturn((SynchronousResponse<AirbyteCatalog>) jobResponse);
    when(completedJob.getSuccessOutput()).thenReturn(Optional.empty());
    when(completedJob.getStatus()).thenReturn(JobStatus.FAILED);

    final SourceDiscoverSchemaRead actual = schedulerHandler.discoverSchemaForSourceFromSourceId(request);

    assertNull(actual.getCatalog());
    assertNotNull(actual.getJobInfo());
    assertFalse(actual.getJobInfo().getSucceeded());
    verify(configRepository).getSourceConnection(source.getSourceId());
    verify(synchronousSchedulerClient).createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE);
  }

  @Test
  void testDiscoverSchemaForSourceFromSourceCreate() throws JsonValidationException, IOException, ConfigNotFoundException {
    final SourceConnection source = new SourceConnection()
        .withSourceDefinitionId(SOURCE.getSourceDefinitionId())
        .withConfiguration(SOURCE.getConfiguration());

    final SynchronousResponse<AirbyteCatalog> discoverResponse = (SynchronousResponse<AirbyteCatalog>) jobResponse;
    final SynchronousJobMetadata metadata = mock(SynchronousJobMetadata.class);
    when(discoverResponse.isSuccess()).thenReturn(true);
    when(discoverResponse.getOutput()).thenReturn(new AirbyteCatalog());
    when(discoverResponse.getMetadata()).thenReturn(metadata);
    when(metadata.isSucceeded()).thenReturn(true);

    final SourceCoreConfig sourceCoreConfig = new SourceCoreConfig()
        .sourceDefinitionId(source.getSourceDefinitionId())
        .connectionConfiguration(source.getConfiguration());

    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceDefinitionId(source.getSourceDefinitionId()));
    when(synchronousSchedulerClient.createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE))
        .thenReturn(discoverResponse);

    final SourceDiscoverSchemaRead actual = schedulerHandler.discoverSchemaForSourceFromSourceCreate(sourceCoreConfig);

    assertNotNull(actual.getCatalog());
    assertNotNull(actual.getJobInfo());
    assertTrue(actual.getJobInfo().getSucceeded());
    verify(synchronousSchedulerClient).createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE);
  }

  @Test
  void testDiscoverSchemaForSourceFromSourceCreateFailed() throws JsonValidationException, IOException, ConfigNotFoundException {
    final SourceConnection source = new SourceConnection()
        .withSourceDefinitionId(SOURCE.getSourceDefinitionId())
        .withConfiguration(SOURCE.getConfiguration());

    final SourceCoreConfig sourceCoreConfig = new SourceCoreConfig()
        .sourceDefinitionId(source.getSourceDefinitionId())
        .connectionConfiguration(source.getConfiguration());

    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceDefinitionId(source.getSourceDefinitionId()));
    when(synchronousSchedulerClient.createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE))
        .thenReturn((SynchronousResponse<AirbyteCatalog>) jobResponse);
    when(completedJob.getSuccessOutput()).thenReturn(Optional.empty());
    when(completedJob.getStatus()).thenReturn(JobStatus.FAILED);

    final SourceDiscoverSchemaRead actual = schedulerHandler.discoverSchemaForSourceFromSourceCreate(sourceCoreConfig);

    assertNull(actual.getCatalog());
    assertNotNull(actual.getJobInfo());
    assertFalse(actual.getJobInfo().getSucceeded());
    verify(synchronousSchedulerClient).createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE);
  }

  @Test
  void testSyncConnection() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardSync standardSync = ConnectionHelpers.generateSyncWithSourceId(UUID.randomUUID());
    final ConnectionIdRequestBody request = new ConnectionIdRequestBody().connectionId(standardSync.getConnectionId());
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID()).withSourceId(standardSync.getSourceId());
    final DestinationConnection destination = DestinationHelpers.generateDestination(UUID.randomUUID())
        .withDestinationId(standardSync.getDestinationId());
    final UUID operationId = standardSync.getOperationIds().get(0);
    final List<StandardSyncOperation> operations = getOperations(standardSync);

    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceDefinitionId(source.getSourceDefinitionId()));
    when(configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId()))
        .thenReturn(new StandardDestinationDefinition()
            .withDockerRepository(DESTINATION_DOCKER_REPO)
            .withDockerImageTag(DESTINATION_DOCKER_TAG)
            .withDestinationDefinitionId(destination.getDestinationDefinitionId()));
    when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);
    when(configRepository.getSourceConnection(source.getSourceId())).thenReturn(source);
    when(configRepository.getDestinationConnection(destination.getDestinationId())).thenReturn(destination);
    when(configRepository.getStandardSyncOperation(operationId)).thenReturn(getOperation(operationId));
    when(schedulerJobClient.createOrGetActiveSyncJob(source, destination, standardSync, SOURCE_DOCKER_IMAGE, DESTINATION_DOCKER_IMAGE, operations))
        .thenReturn(completedJob);
    when(completedJob.getScope()).thenReturn("cat:12");
    final JobConfig jobConfig = mock(JobConfig.class);
    when(completedJob.getConfig()).thenReturn(jobConfig);
    when(jobConfig.getConfigType()).thenReturn(ConfigType.SYNC);

    final JobInfoRead jobStatusRead = schedulerHandler.syncConnection(request);

    assertEquals(io.airbyte.api.model.JobStatus.SUCCEEDED, jobStatusRead.getJob().getStatus());
    verify(configRepository).getStandardSync(standardSync.getConnectionId());
    verify(configRepository).getSourceConnection(standardSync.getSourceId());
    verify(configRepository).getDestinationConnection(standardSync.getDestinationId());
    verify(schedulerJobClient).createOrGetActiveSyncJob(source, destination, standardSync, SOURCE_DOCKER_IMAGE, DESTINATION_DOCKER_IMAGE, operations);
  }

  @Test
  void testResetConnection() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardSync standardSync = ConnectionHelpers.generateSyncWithSourceId(UUID.randomUUID());
    final ConnectionIdRequestBody request = new ConnectionIdRequestBody().connectionId(standardSync.getConnectionId());
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID()).withSourceId(standardSync.getSourceId());
    final DestinationConnection destination = DestinationHelpers.generateDestination(UUID.randomUUID())
        .withDestinationId(standardSync.getDestinationId());
    final UUID operationId = standardSync.getOperationIds().get(0);
    final List<StandardSyncOperation> operations = getOperations(standardSync);

    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceDefinitionId(source.getSourceDefinitionId()));
    when(configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId()))
        .thenReturn(new StandardDestinationDefinition()
            .withDockerRepository(DESTINATION_DOCKER_REPO)
            .withDockerImageTag(DESTINATION_DOCKER_TAG)
            .withDestinationDefinitionId(destination.getDestinationDefinitionId()));
    when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);
    when(configRepository.getSourceConnection(source.getSourceId())).thenReturn(source);
    when(configRepository.getDestinationConnection(destination.getDestinationId())).thenReturn(destination);
    when(configRepository.getStandardSyncOperation(operationId)).thenReturn(getOperation(operationId));
    when(schedulerJobClient.createOrGetActiveResetConnectionJob(destination, standardSync, DESTINATION_DOCKER_IMAGE, operations))
        .thenReturn(completedJob);
    when(completedJob.getScope()).thenReturn("cat:12");
    final JobConfig jobConfig = mock(JobConfig.class);
    when(completedJob.getConfig()).thenReturn(jobConfig);
    when(jobConfig.getConfigType()).thenReturn(ConfigType.SYNC);

    final JobInfoRead jobStatusRead = schedulerHandler.resetConnection(request);

    assertEquals(io.airbyte.api.model.JobStatus.SUCCEEDED, jobStatusRead.getJob().getStatus());
    verify(configRepository).getStandardSync(standardSync.getConnectionId());
    verify(configRepository).getDestinationConnection(standardSync.getDestinationId());
    verify(schedulerJobClient).createOrGetActiveResetConnectionJob(destination, standardSync, DESTINATION_DOCKER_IMAGE, operations);
  }

  @Test
  void testGetCurrentState() throws IOException {
    final UUID connectionId = UUID.randomUUID();
    final State state = new State().withState(Jsons.jsonNode(ImmutableMap.of("checkpoint", 1)));
    when(jobPersistence.getCurrentState(connectionId)).thenReturn(Optional.of(state));

    final ConnectionState connectionState = schedulerHandler.getState(new ConnectionIdRequestBody().connectionId(connectionId));
    assertEquals(new ConnectionState().connectionId(connectionId).state(state.getState()), connectionState);
  }

  @Test
  void testGetCurrentStateEmpty() throws IOException {
    final UUID connectionId = UUID.randomUUID();
    when(jobPersistence.getCurrentState(connectionId)).thenReturn(Optional.empty());

    final ConnectionState connectionState = schedulerHandler.getState(new ConnectionIdRequestBody().connectionId(connectionId));
    assertEquals(new ConnectionState().connectionId(connectionId), connectionState);
  }

  @Test
  void testEnumConversion() {
    assertTrue(Enums.isCompatible(StandardCheckConnectionOutput.Status.class, CheckConnectionRead.StatusEnum.class));
    assertTrue(Enums.isCompatible(JobStatus.class, io.airbyte.api.model.JobStatus.class));
  }

  private static List<StandardSyncOperation> getOperations(StandardSync standardSync) {
    if (standardSync.getOperationIds() != null && !standardSync.getOperationIds().isEmpty()) {
      return List.of(getOperation(standardSync.getOperationIds().get(0)));
    } else {
      return List.of();
    }
  }

  private static StandardSyncOperation getOperation(UUID operationId) {
    return new StandardSyncOperation()
        .withOperationId(operationId)
        .withName(OPERATION_NAME)
        .withOperatorType(OperatorType.NORMALIZATION)
        .withOperatorNormalization(new OperatorNormalization().withOption(Option.BASIC));
  }

}
