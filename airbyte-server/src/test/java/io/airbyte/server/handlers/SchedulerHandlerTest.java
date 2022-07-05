/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.api.model.generated.CheckConnectionRead;
import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.DestinationCoreConfig;
import io.airbyte.api.model.generated.DestinationDefinitionIdWithWorkspaceId;
import io.airbyte.api.model.generated.DestinationDefinitionSpecificationRead;
import io.airbyte.api.model.generated.DestinationIdRequestBody;
import io.airbyte.api.model.generated.DestinationUpdate;
import io.airbyte.api.model.generated.JobIdRequestBody;
import io.airbyte.api.model.generated.JobInfoRead;
import io.airbyte.api.model.generated.SourceCoreConfig;
import io.airbyte.api.model.generated.SourceDefinitionIdWithWorkspaceId;
import io.airbyte.api.model.generated.SourceDefinitionSpecificationRead;
import io.airbyte.api.model.generated.SourceDiscoverSchemaRead;
import io.airbyte.api.model.generated.SourceDiscoverSchemaRequestBody;
import io.airbyte.api.model.generated.SourceIdRequestBody;
import io.airbyte.api.model.generated.SourceUpdate;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.ActorCatalog;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.scheduler.client.EventRunner;
import io.airbyte.scheduler.client.SynchronousJobMetadata;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.converters.ConfigurationUpdate;
import io.airbyte.server.converters.JobConverter;
import io.airbyte.server.helpers.DestinationHelpers;
import io.airbyte.server.helpers.SourceHelpers;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.temporal.TemporalClient.ManualOperationResult;
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

  private static final ConnectorSpecification CONNECTOR_SPECIFICATION = new ConnectorSpecification()
      .withDocumentationUrl(Exceptions.toRuntime(() -> new URI("https://google.com")))
      .withChangelogUrl(Exceptions.toRuntime(() -> new URI("https://google.com")))
      .withConnectionSpecification(Jsons.jsonNode(new HashMap<>()));

  private static final StreamDescriptor STREAM_DESCRIPTOR = new StreamDescriptor().withName("1");

  private SchedulerHandler schedulerHandler;
  private ConfigRepository configRepository;
  private SecretsRepositoryWriter secretsRepositoryWriter;
  private Job completedJob;
  private SynchronousSchedulerClient synchronousSchedulerClient;
  private SynchronousResponse<?> jobResponse;
  private ConfigurationUpdate configurationUpdate;
  private JsonSchemaValidator jsonSchemaValidator;
  private JobPersistence jobPersistence;
  private EventRunner eventRunner;
  private JobConverter jobConverter;
  private StatePersistence statePersistence;

  @BeforeEach
  void setup() {
    completedJob = mock(Job.class, RETURNS_DEEP_STUBS);
    jobResponse = mock(SynchronousResponse.class, RETURNS_DEEP_STUBS);
    configurationUpdate = mock(ConfigurationUpdate.class);
    jsonSchemaValidator = mock(JsonSchemaValidator.class);
    when(completedJob.getStatus()).thenReturn(JobStatus.SUCCEEDED);
    when(completedJob.getConfig().getConfigType()).thenReturn(ConfigType.SYNC);
    when(completedJob.getScope()).thenReturn("sync:123");

    synchronousSchedulerClient = mock(SynchronousSchedulerClient.class);
    configRepository = mock(ConfigRepository.class);
    secretsRepositoryWriter = mock(SecretsRepositoryWriter.class);
    jobPersistence = mock(JobPersistence.class);
    statePersistence = mock(StatePersistence.class);
    eventRunner = mock(EventRunner.class);

    jobConverter = spy(new JobConverter(WorkerEnvironment.DOCKER, LogConfigs.EMPTY));

    schedulerHandler = new SchedulerHandler(
        configRepository,
        secretsRepositoryWriter,
        synchronousSchedulerClient,
        configurationUpdate,
        jsonSchemaValidator,
        jobPersistence,
        eventRunner,
        jobConverter);
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
    when(secretsRepositoryWriter.statefulSplitEphemeralSecrets(
        eq(source.getConfiguration()),
        any())).thenReturn(source.getConfiguration());
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
    final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
        .withDockerRepository(DESTINATION_DOCKER_REPO)
        .withDockerImageTag(DESTINATION_DOCKER_TAG)
        .withSourceDefinitionId(source.getSourceDefinitionId())
        .withSpec(CONNECTOR_SPECIFICATION);
    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(sourceDefinition);
    when(configRepository.getSourceConnection(source.getSourceId())).thenReturn(source);
    when(configurationUpdate.source(source.getSourceId(), source.getName(), sourceUpdate.getConnectionConfiguration())).thenReturn(source);
    final SourceConnection submittedSource = new SourceConnection()
        .withSourceDefinitionId(source.getSourceDefinitionId())
        .withConfiguration(source.getConfiguration());
    when(synchronousSchedulerClient.createSourceCheckConnectionJob(submittedSource, DESTINATION_DOCKER_IMAGE))
        .thenReturn((SynchronousResponse<StandardCheckConnectionOutput>) jobResponse);
    when(secretsRepositoryWriter.statefulSplitEphemeralSecrets(
        eq(source.getConfiguration()),
        any())).thenReturn(source.getConfiguration());
    schedulerHandler.checkSourceConnectionFromSourceIdForUpdate(sourceUpdate);

    verify(jsonSchemaValidator).ensure(CONNECTOR_SPECIFICATION.getConnectionSpecification(), source.getConfiguration());
    verify(synchronousSchedulerClient).createSourceCheckConnectionJob(submittedSource, DESTINATION_DOCKER_IMAGE);
  }

  @Test
  void testGetSourceSpec() throws JsonValidationException, IOException, ConfigNotFoundException {
    final SourceDefinitionIdWithWorkspaceId sourceDefinitionIdWithWorkspaceId =
        new SourceDefinitionIdWithWorkspaceId().sourceDefinitionId(UUID.randomUUID()).workspaceId(UUID.randomUUID());

    final SynchronousResponse<ConnectorSpecification> specResponse = (SynchronousResponse<ConnectorSpecification>) jobResponse;
    final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
        .withName("name")
        .withDockerRepository(SOURCE_DOCKER_REPO)
        .withDockerImageTag(SOURCE_DOCKER_TAG)
        .withSourceDefinitionId(sourceDefinitionIdWithWorkspaceId.getSourceDefinitionId())
        .withSpec(CONNECTOR_SPECIFICATION);
    when(configRepository.getStandardSourceDefinition(sourceDefinitionIdWithWorkspaceId.getSourceDefinitionId()))
        .thenReturn(sourceDefinition);

    final SourceDefinitionSpecificationRead response = schedulerHandler.getSourceDefinitionSpecification(sourceDefinitionIdWithWorkspaceId);

    verify(configRepository).getStandardSourceDefinition(sourceDefinitionIdWithWorkspaceId.getSourceDefinitionId());
    assertEquals(CONNECTOR_SPECIFICATION.getConnectionSpecification(), response.getConnectionSpecification());
  }

  @Test
  void testGetDestinationSpec() throws JsonValidationException, IOException, ConfigNotFoundException {
    final DestinationDefinitionIdWithWorkspaceId destinationDefinitionIdWithWorkspaceId =
        new DestinationDefinitionIdWithWorkspaceId().destinationDefinitionId(UUID.randomUUID()).workspaceId(UUID.randomUUID());

    final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
        .withName("name")
        .withDockerRepository(DESTINATION_DOCKER_REPO)
        .withDockerImageTag(DESTINATION_DOCKER_TAG)
        .withDestinationDefinitionId(destinationDefinitionIdWithWorkspaceId.getDestinationDefinitionId())
        .withSpec(CONNECTOR_SPECIFICATION);
    when(configRepository.getStandardDestinationDefinition(destinationDefinitionIdWithWorkspaceId.getDestinationDefinitionId()))
        .thenReturn(destinationDefinition);

    final DestinationDefinitionSpecificationRead response = schedulerHandler.getDestinationSpecification(destinationDefinitionIdWithWorkspaceId);

    verify(configRepository).getStandardDestinationDefinition(destinationDefinitionIdWithWorkspaceId.getDestinationDefinitionId());
    assertEquals(CONNECTOR_SPECIFICATION.getConnectionSpecification(), response.getConnectionSpecification());
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
    when(secretsRepositoryWriter.statefulSplitEphemeralSecrets(
        eq(destination.getConfiguration()),
        any())).thenReturn(destination.getConfiguration());
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
    final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
        .withDockerRepository(DESTINATION_DOCKER_REPO)
        .withDockerImageTag(DESTINATION_DOCKER_TAG)
        .withDestinationDefinitionId(destination.getDestinationDefinitionId())
        .withSpec(CONNECTOR_SPECIFICATION);
    when(configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId()))
        .thenReturn(destinationDefinition);
    when(configRepository.getDestinationConnection(destination.getDestinationId())).thenReturn(destination);
    when(configurationUpdate.destination(destination.getDestinationId(), destination.getName(), destinationUpdate.getConnectionConfiguration()))
        .thenReturn(destination);
    final DestinationConnection submittedDestination = new DestinationConnection()
        .withDestinationDefinitionId(destination.getDestinationDefinitionId())
        .withConfiguration(destination.getConfiguration());
    when(synchronousSchedulerClient.createDestinationCheckConnectionJob(submittedDestination, DESTINATION_DOCKER_IMAGE))
        .thenReturn((SynchronousResponse<StandardCheckConnectionOutput>) jobResponse);
    when(secretsRepositoryWriter.statefulSplitEphemeralSecrets(
        eq(destination.getConfiguration()),
        any())).thenReturn(destination.getConfiguration());
    schedulerHandler.checkDestinationConnectionFromDestinationIdForUpdate(destinationUpdate);

    verify(jsonSchemaValidator).ensure(CONNECTOR_SPECIFICATION.getConnectionSpecification(), destination.getConfiguration());
    verify(synchronousSchedulerClient).createDestinationCheckConnectionJob(submittedDestination, DESTINATION_DOCKER_IMAGE);
  }

  @Test
  void testDiscoverSchemaForSourceFromSourceId() throws IOException, JsonValidationException, ConfigNotFoundException {
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    final SourceDiscoverSchemaRequestBody request = new SourceDiscoverSchemaRequestBody().sourceId(source.getSourceId());

    final SynchronousResponse<AirbyteCatalog> discoverResponse = (SynchronousResponse<AirbyteCatalog>) jobResponse;
    final SynchronousJobMetadata metadata = mock(SynchronousJobMetadata.class);
    when(discoverResponse.isSuccess()).thenReturn(true);
    final AirbyteCatalog airbyteCatalog = CatalogHelpers.createAirbyteCatalog("shoes",
        Field.of("sku", JsonSchemaType.STRING));
    when(discoverResponse.getOutput()).thenReturn(airbyteCatalog);
    when(discoverResponse.getMetadata()).thenReturn(metadata);
    when(metadata.isSucceeded()).thenReturn(true);

    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceDefinitionId(source.getSourceDefinitionId()));
    when(configRepository.getSourceConnection(source.getSourceId())).thenReturn(source);
    when(configRepository.getActorCatalog(any(), any(), any())).thenReturn(Optional.empty());
    when(synchronousSchedulerClient.createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE))
        .thenReturn(discoverResponse);

    final SourceDiscoverSchemaRead actual = schedulerHandler.discoverSchemaForSourceFromSourceId(request);

    assertNotNull(actual.getCatalog());
    assertNotNull(actual.getJobInfo());
    assertTrue(actual.getJobInfo().getSucceeded());
    verify(configRepository).getSourceConnection(source.getSourceId());
    verify(configRepository).getActorCatalog(eq(request.getSourceId()), eq(SOURCE_DOCKER_TAG), any());
    verify(configRepository).writeActorCatalogFetchEvent(eq(airbyteCatalog), eq(source.getSourceId()), eq(SOURCE_DOCKER_TAG), any());
    verify(synchronousSchedulerClient).createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE);
  }

  @Test
  void testDiscoverSchemaForSourceFromSourceIdCachedCatalog() throws IOException, JsonValidationException, ConfigNotFoundException {
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    final SourceDiscoverSchemaRequestBody request = new SourceDiscoverSchemaRequestBody().sourceId(source.getSourceId());

    final SynchronousResponse<AirbyteCatalog> discoverResponse = (SynchronousResponse<AirbyteCatalog>) jobResponse;
    final SynchronousJobMetadata metadata = mock(SynchronousJobMetadata.class);
    when(discoverResponse.isSuccess()).thenReturn(true);
    final AirbyteCatalog airbyteCatalog = CatalogHelpers.createAirbyteCatalog("shoes",
        Field.of("sku", JsonSchemaType.STRING));
    when(discoverResponse.getOutput()).thenReturn(airbyteCatalog);
    when(discoverResponse.getMetadata()).thenReturn(metadata);
    when(metadata.isSucceeded()).thenReturn(true);

    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceDefinitionId(source.getSourceDefinitionId()));
    when(configRepository.getSourceConnection(source.getSourceId())).thenReturn(source);
    final ActorCatalog actorCatalog = new ActorCatalog()
        .withCatalog(Jsons.jsonNode(airbyteCatalog))
        .withCatalogHash("")
        .withId(UUID.randomUUID());
    when(configRepository.getActorCatalog(any(), any(), any())).thenReturn(Optional.of(actorCatalog));
    when(synchronousSchedulerClient.createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE))
        .thenReturn(discoverResponse);

    final SourceDiscoverSchemaRead actual = schedulerHandler.discoverSchemaForSourceFromSourceId(request);

    assertNotNull(actual.getCatalog());
    assertNotNull(actual.getJobInfo());
    assertTrue(actual.getJobInfo().getSucceeded());
    verify(configRepository).getSourceConnection(source.getSourceId());
    verify(configRepository).getActorCatalog(eq(request.getSourceId()), any(), any());
    verify(configRepository, never()).writeActorCatalogFetchEvent(any(), any(), any(), any());
    verify(synchronousSchedulerClient, never()).createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE);
  }

  @Test
  void testDiscoverSchemaForSourceFromSourceIdDisableCache() throws IOException, JsonValidationException, ConfigNotFoundException {
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    final SourceDiscoverSchemaRequestBody request = new SourceDiscoverSchemaRequestBody().sourceId(source.getSourceId()).disableCache(true);

    final SynchronousResponse<AirbyteCatalog> discoverResponse = (SynchronousResponse<AirbyteCatalog>) jobResponse;
    final SynchronousJobMetadata metadata = mock(SynchronousJobMetadata.class);
    when(discoverResponse.isSuccess()).thenReturn(true);
    final AirbyteCatalog airbyteCatalog = CatalogHelpers.createAirbyteCatalog("shoes",
        Field.of("sku", JsonSchemaType.STRING));
    when(discoverResponse.getOutput()).thenReturn(airbyteCatalog);
    when(discoverResponse.getMetadata()).thenReturn(metadata);
    when(metadata.isSucceeded()).thenReturn(true);

    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withSourceDefinitionId(source.getSourceDefinitionId()));
    when(configRepository.getSourceConnection(source.getSourceId())).thenReturn(source);
    final ActorCatalog actorCatalog = new ActorCatalog()
        .withCatalog(Jsons.jsonNode(airbyteCatalog))
        .withCatalogHash("")
        .withId(UUID.randomUUID());
    when(configRepository.getActorCatalog(any(), any(), any())).thenReturn(Optional.of(actorCatalog));
    when(synchronousSchedulerClient.createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE))
        .thenReturn(discoverResponse);

    final SourceDiscoverSchemaRead actual = schedulerHandler.discoverSchemaForSourceFromSourceId(request);

    assertNotNull(actual.getCatalog());
    assertNotNull(actual.getJobInfo());
    assertTrue(actual.getJobInfo().getSucceeded());
    verify(configRepository).getSourceConnection(source.getSourceId());
    verify(configRepository).getActorCatalog(eq(request.getSourceId()), any(), any());
    verify(configRepository).writeActorCatalogFetchEvent(any(), any(), any(), any());
    verify(synchronousSchedulerClient).createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE);
  }

  @Test
  void testDiscoverSchemaForSourceFromSourceIdFailed() throws IOException, JsonValidationException, ConfigNotFoundException {
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    final SourceDiscoverSchemaRequestBody request = new SourceDiscoverSchemaRequestBody().sourceId(source.getSourceId());

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
    when(secretsRepositoryWriter.statefulSplitEphemeralSecrets(
        eq(source.getConfiguration()),
        any())).thenReturn(source.getConfiguration());

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
    when(secretsRepositoryWriter.statefulSplitEphemeralSecrets(
        eq(source.getConfiguration()),
        any())).thenReturn(source.getConfiguration());
    when(completedJob.getSuccessOutput()).thenReturn(Optional.empty());
    when(completedJob.getStatus()).thenReturn(JobStatus.FAILED);

    final SourceDiscoverSchemaRead actual = schedulerHandler.discoverSchemaForSourceFromSourceCreate(sourceCoreConfig);

    assertNull(actual.getCatalog());
    assertNotNull(actual.getJobInfo());
    assertFalse(actual.getJobInfo().getSucceeded());
    verify(synchronousSchedulerClient).createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE);
  }

  @Test
  void testEnumConversion() {
    assertTrue(Enums.isCompatible(StandardCheckConnectionOutput.Status.class, CheckConnectionRead.StatusEnum.class));
    assertTrue(Enums.isCompatible(JobStatus.class, io.airbyte.api.model.generated.JobStatus.class));
  }

  @Test
  void testSyncConnection() throws IOException {
    final UUID connectionId = UUID.randomUUID();

    final long jobId = 123L;
    final ManualOperationResult manualOperationResult = ManualOperationResult
        .builder()
        .failingReason(Optional.empty())
        .jobId(Optional.of(jobId))
        .build();

    when(eventRunner.startNewManualSync(connectionId))
        .thenReturn(manualOperationResult);

    doReturn(new JobInfoRead())
        .when(jobConverter).getJobInfoRead(any());

    schedulerHandler.syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    verify(eventRunner).startNewManualSync(connectionId);
  }

  @Test
  void testResetConnection() throws IOException, JsonValidationException, ConfigNotFoundException {
    final UUID connectionId = UUID.randomUUID();

    final long jobId = 123L;
    final ManualOperationResult manualOperationResult = ManualOperationResult
        .builder()
        .failingReason(Optional.empty())
        .jobId(Optional.of(jobId))
        .build();

    final List<StreamDescriptor> streamDescriptors = List.of(STREAM_DESCRIPTOR);
    when(configRepository.getAllStreamsForConnection(connectionId))
        .thenReturn(streamDescriptors);

    when(eventRunner.resetConnection(connectionId, streamDescriptors))
        .thenReturn(manualOperationResult);

    doReturn(new JobInfoRead())
        .when(jobConverter).getJobInfoRead(any());

    schedulerHandler.resetConnection(new ConnectionIdRequestBody().connectionId(connectionId));

    verify(eventRunner).resetConnection(connectionId, streamDescriptors);
  }

  @Test
  void testCancelJob() throws IOException {
    final UUID connectionId = UUID.randomUUID();
    final long jobId = 123L;
    final Job job = mock(Job.class);
    when(job.getScope()).thenReturn(connectionId.toString());
    when(jobPersistence.getJob(jobId)).thenReturn(job);

    final ManualOperationResult manualOperationResult = ManualOperationResult
        .builder()
        .failingReason(Optional.empty())
        .jobId(Optional.of(jobId))
        .build();

    when(eventRunner.startNewCancellation(connectionId))
        .thenReturn(manualOperationResult);

    doReturn(new JobInfoRead())
        .when(jobConverter).getJobInfoRead(any());

    schedulerHandler.cancelJob(new JobIdRequestBody().id(jobId));

    verify(eventRunner).startNewCancellation(connectionId);
  }

}
