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
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Lists;
import io.airbyte.api.model.generated.ConnectionRead;
import io.airbyte.api.model.generated.ConnectionReadList;
import io.airbyte.api.model.generated.SourceCloneConfiguration;
import io.airbyte.api.model.generated.SourceCloneRequestBody;
import io.airbyte.api.model.generated.SourceCreate;
import io.airbyte.api.model.generated.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.generated.SourceDefinitionSpecificationRead;
import io.airbyte.api.model.generated.SourceDiscoverSchemaRead;
import io.airbyte.api.model.generated.SourceDiscoverSchemaRequestBody;
import io.airbyte.api.model.generated.SourceIdRequestBody;
import io.airbyte.api.model.generated.SourceRead;
import io.airbyte.api.model.generated.SourceReadList;
import io.airbyte.api.model.generated.SourceSearch;
import io.airbyte.api.model.generated.SourceUpdate;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.Version;
import io.airbyte.config.ActorCatalog;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.persistence.job.models.JobStatus;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.server.converters.ConfigurationUpdate;
import io.airbyte.server.helpers.ConnectionHelpers;
import io.airbyte.server.helpers.ConnectorSpecificationHelpers;
import io.airbyte.server.helpers.SourceHelpers;
import io.airbyte.server.scheduler.SynchronousJobMetadata;
import io.airbyte.server.scheduler.SynchronousResponse;
import io.airbyte.server.scheduler.SynchronousSchedulerClient;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SourceHandlerTest {

  private static final String SOURCE_DOCKER_REPO = "srcimage";
  private static final String SOURCE_DOCKER_TAG = "tag";
  private static final String SOURCE_DOCKER_IMAGE = DockerUtils.getTaggedImageName(SOURCE_DOCKER_REPO, SOURCE_DOCKER_TAG);
  private static final String SOURCE_PROTOCOL_VERSION = "0.4.5";
  private static final String SHOES = "shoes";
  private static final String SKU = "sku";

  private static final AirbyteCatalog airbyteCatalog = CatalogHelpers.createAirbyteCatalog(SHOES,
      Field.of(SKU, JsonSchemaType.STRING));

  private ConfigRepository configRepository;
  private SecretsRepositoryReader secretsRepositoryReader;
  private SecretsRepositoryWriter secretsRepositoryWriter;
  private StandardSourceDefinition standardSourceDefinition;
  private SourceDefinitionSpecificationRead sourceDefinitionSpecificationRead;
  private SourceConnection sourceConnection;
  private SourceHandler sourceHandler;
  private JsonSchemaValidator validator;
  private ConnectionsHandler connectionsHandler;
  private SchedulerHandler schedulerHandler;
  private SynchronousSchedulerClient synchronousSchedulerClient;
  private ConfigurationUpdate configurationUpdate;
  private Supplier<UUID> uuidGenerator;
  private JsonSecretsProcessor secretsProcessor;
  private ConnectorSpecification connectorSpecification;
  private Job completedJob;
  private SynchronousResponse<?> jobResponse;

  // needs to match name of file in src/test/resources/icons
  private static final String ICON = "test-source.svg";

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() throws IOException {
    completedJob = mock(Job.class, RETURNS_DEEP_STUBS);
    jobResponse = mock(SynchronousResponse.class, RETURNS_DEEP_STUBS);
    configRepository = mock(ConfigRepository.class);
    secretsRepositoryReader = mock(SecretsRepositoryReader.class);
    secretsRepositoryWriter = mock(SecretsRepositoryWriter.class);
    validator = mock(JsonSchemaValidator.class);
    connectionsHandler = mock(ConnectionsHandler.class);
    schedulerHandler = mock(SchedulerHandler.class);
    synchronousSchedulerClient = mock(SynchronousSchedulerClient.class);
    configurationUpdate = mock(ConfigurationUpdate.class);
    uuidGenerator = mock(Supplier.class);
    secretsProcessor = mock(JsonSecretsProcessor.class);

    connectorSpecification = ConnectorSpecificationHelpers.generateConnectorSpecification();

    standardSourceDefinition = new StandardSourceDefinition()
        .withSourceDefinitionId(UUID.randomUUID())
        .withName("marketo")
        .withDockerRepository("thebestrepo")
        .withDockerImageTag("thelatesttag")
        .withDocumentationUrl("https://wikipedia.org")
        .withSpec(connectorSpecification)
        .withIcon(ICON);

    sourceDefinitionSpecificationRead = new SourceDefinitionSpecificationRead()
        .sourceDefinitionId(standardSourceDefinition.getSourceDefinitionId())
        .connectionSpecification(connectorSpecification.getConnectionSpecification())
        .documentationUrl(connectorSpecification.getDocumentationUrl().toString());

    sourceConnection = SourceHelpers.generateSource(standardSourceDefinition.getSourceDefinitionId());

    sourceHandler = new SourceHandler(configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        validator,
        connectionsHandler,
        schedulerHandler,
        synchronousSchedulerClient,
        uuidGenerator,
        secretsProcessor,
        configurationUpdate);
  }

  @Test
  void testCreateSource() throws JsonValidationException, ConfigNotFoundException, IOException {
    final SourceCreate sourceCreate = new SourceCreate()
        .name(sourceConnection.getName())
        .workspaceId(sourceConnection.getWorkspaceId())
        .sourceDefinitionId(standardSourceDefinition.getSourceDefinitionId())
        .connectionConfiguration(sourceConnection.getConfiguration());

    when(uuidGenerator.get()).thenReturn(sourceConnection.getSourceId());
    when(configRepository.getSourceConnection(sourceConnection.getSourceId())).thenReturn(sourceConnection);
    when(configRepository.getStandardSourceDefinition(sourceDefinitionSpecificationRead.getSourceDefinitionId()))
        .thenReturn(standardSourceDefinition);
    when(secretsProcessor.prepareSecretsForOutput(sourceCreate.getConnectionConfiguration(),
        sourceDefinitionSpecificationRead.getConnectionSpecification()))
            .thenReturn(sourceCreate.getConnectionConfiguration());

    final SourceRead actualSourceRead = sourceHandler.createSource(sourceCreate);

    final SourceRead expectedSourceRead = SourceHelpers.getSourceRead(sourceConnection, standardSourceDefinition)
        .connectionConfiguration(sourceConnection.getConfiguration());

    assertEquals(expectedSourceRead, actualSourceRead);

    verify(secretsProcessor).prepareSecretsForOutput(sourceCreate.getConnectionConfiguration(),
        sourceDefinitionSpecificationRead.getConnectionSpecification());
    verify(secretsRepositoryWriter).writeSourceConnection(sourceConnection, connectorSpecification);
    verify(validator).ensure(sourceDefinitionSpecificationRead.getConnectionSpecification(), sourceConnection.getConfiguration());
  }

  @Test
  void testUpdateSource() throws JsonValidationException, ConfigNotFoundException, IOException {
    final String updatedSourceName = "my updated source name";
    final JsonNode newConfiguration = sourceConnection.getConfiguration();
    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final SourceConnection expectedSourceConnection = Jsons.clone(sourceConnection)
        .withName(updatedSourceName)
        .withConfiguration(newConfiguration)
        .withTombstone(false);

    final SourceUpdate sourceUpdate = new SourceUpdate()
        .name(updatedSourceName)
        .sourceId(sourceConnection.getSourceId())
        .connectionConfiguration(newConfiguration);

    when(secretsProcessor
        .copySecrets(sourceConnection.getConfiguration(), newConfiguration, sourceDefinitionSpecificationRead.getConnectionSpecification()))
            .thenReturn(newConfiguration);
    when(secretsProcessor.prepareSecretsForOutput(newConfiguration, sourceDefinitionSpecificationRead.getConnectionSpecification()))
        .thenReturn(newConfiguration);
    when(configRepository.getStandardSourceDefinition(sourceDefinitionSpecificationRead.getSourceDefinitionId()))
        .thenReturn(standardSourceDefinition);
    when(configRepository.getSourceDefinitionFromSource(sourceConnection.getSourceId()))
        .thenReturn(standardSourceDefinition);
    when(configRepository.getSourceConnection(sourceConnection.getSourceId()))
        .thenReturn(sourceConnection)
        .thenReturn(expectedSourceConnection);
    when(configurationUpdate.source(sourceConnection.getSourceId(), updatedSourceName, newConfiguration))
        .thenReturn(expectedSourceConnection);

    final SourceRead actualSourceRead = sourceHandler.updateSource(sourceUpdate);
    final SourceRead expectedSourceRead =
        SourceHelpers.getSourceRead(expectedSourceConnection, standardSourceDefinition).connectionConfiguration(newConfiguration);

    assertEquals(expectedSourceRead, actualSourceRead);

    verify(secretsProcessor).prepareSecretsForOutput(newConfiguration, sourceDefinitionSpecificationRead.getConnectionSpecification());
    verify(secretsRepositoryWriter).writeSourceConnection(expectedSourceConnection, connectorSpecification);
    verify(validator).ensure(sourceDefinitionSpecificationRead.getConnectionSpecification(), newConfiguration);
  }

  @Test
  void testGetSource() throws JsonValidationException, ConfigNotFoundException, IOException {
    final SourceRead expectedSourceRead = SourceHelpers.getSourceRead(sourceConnection, standardSourceDefinition);
    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody().sourceId(expectedSourceRead.getSourceId());

    when(configRepository.getSourceConnection(sourceConnection.getSourceId())).thenReturn(sourceConnection);
    when(configRepository.getStandardSourceDefinition(sourceDefinitionSpecificationRead.getSourceDefinitionId()))
        .thenReturn(standardSourceDefinition);
    when(configRepository.getSourceDefinitionFromSource(sourceConnection.getSourceId())).thenReturn(standardSourceDefinition);
    when(
        secretsProcessor.prepareSecretsForOutput(sourceConnection.getConfiguration(), sourceDefinitionSpecificationRead.getConnectionSpecification()))
            .thenReturn(sourceConnection.getConfiguration());

    final SourceRead actualSourceRead = sourceHandler.getSource(sourceIdRequestBody);

    assertEquals(expectedSourceRead, actualSourceRead);

    // make sure the icon was loaded into actual svg content
    assertTrue(expectedSourceRead.getIcon().startsWith("<svg>"));

    verify(secretsProcessor).prepareSecretsForOutput(sourceConnection.getConfiguration(),
        sourceDefinitionSpecificationRead.getConnectionSpecification());
  }

  @Test
  void testCloneSourceWithoutConfigChange() throws JsonValidationException, ConfigNotFoundException, IOException {
    final SourceConnection clonedConnection = SourceHelpers.generateSource(standardSourceDefinition.getSourceDefinitionId());
    final SourceRead expectedClonedSourceRead = SourceHelpers.getSourceRead(clonedConnection, standardSourceDefinition);
    final SourceRead sourceRead = SourceHelpers.getSourceRead(sourceConnection, standardSourceDefinition);

    final SourceCloneRequestBody sourceCloneRequestBody = new SourceCloneRequestBody().sourceCloneId(sourceRead.getSourceId());

    when(uuidGenerator.get()).thenReturn(clonedConnection.getSourceId());
    when(secretsRepositoryReader.getSourceConnectionWithSecrets(sourceConnection.getSourceId())).thenReturn(sourceConnection);
    when(configRepository.getSourceConnection(clonedConnection.getSourceId())).thenReturn(clonedConnection);

    when(configRepository.getStandardSourceDefinition(sourceDefinitionSpecificationRead.getSourceDefinitionId()))
        .thenReturn(standardSourceDefinition);
    when(configRepository.getSourceDefinitionFromSource(sourceConnection.getSourceId())).thenReturn(standardSourceDefinition);
    when(
        secretsProcessor.prepareSecretsForOutput(sourceConnection.getConfiguration(), sourceDefinitionSpecificationRead.getConnectionSpecification()))
            .thenReturn(sourceConnection.getConfiguration());

    final SourceRead actualSourceRead = sourceHandler.cloneSource(sourceCloneRequestBody);

    assertEquals(expectedClonedSourceRead, actualSourceRead);
  }

  @Test
  void testCloneSourceWithConfigChange() throws JsonValidationException, ConfigNotFoundException, IOException {
    final SourceConnection clonedConnection = SourceHelpers.generateSource(standardSourceDefinition.getSourceDefinitionId());
    final SourceRead expectedClonedSourceRead = SourceHelpers.getSourceRead(clonedConnection, standardSourceDefinition);
    final SourceRead sourceRead = SourceHelpers.getSourceRead(sourceConnection, standardSourceDefinition);

    final SourceCloneConfiguration sourceCloneConfiguration = new SourceCloneConfiguration().name("Copy Name");
    final SourceCloneRequestBody sourceCloneRequestBody =
        new SourceCloneRequestBody().sourceCloneId(sourceRead.getSourceId()).sourceConfiguration(sourceCloneConfiguration);

    when(uuidGenerator.get()).thenReturn(clonedConnection.getSourceId());
    when(secretsRepositoryReader.getSourceConnectionWithSecrets(sourceConnection.getSourceId())).thenReturn(sourceConnection);
    when(configRepository.getSourceConnection(clonedConnection.getSourceId())).thenReturn(clonedConnection);

    when(configRepository.getStandardSourceDefinition(sourceDefinitionSpecificationRead.getSourceDefinitionId()))
        .thenReturn(standardSourceDefinition);
    when(configRepository.getSourceDefinitionFromSource(sourceConnection.getSourceId())).thenReturn(standardSourceDefinition);
    when(
        secretsProcessor.prepareSecretsForOutput(sourceConnection.getConfiguration(), sourceDefinitionSpecificationRead.getConnectionSpecification()))
            .thenReturn(sourceConnection.getConfiguration());

    final SourceRead actualSourceRead = sourceHandler.cloneSource(sourceCloneRequestBody);

    assertEquals(expectedClonedSourceRead, actualSourceRead);
  }

  @Test
  void testListSourcesForWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    final SourceRead expectedSourceRead = SourceHelpers.getSourceRead(sourceConnection, standardSourceDefinition);
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(sourceConnection.getWorkspaceId());

    when(configRepository.getSourceConnection(sourceConnection.getSourceId())).thenReturn(sourceConnection);
    when(configRepository.getSourceConnection(sourceConnection.getSourceId())).thenReturn(sourceConnection);

    when(configRepository.listWorkspaceSourceConnection(sourceConnection.getWorkspaceId())).thenReturn(Lists.newArrayList(sourceConnection));
    when(configRepository.getStandardSourceDefinition(sourceDefinitionSpecificationRead.getSourceDefinitionId()))
        .thenReturn(standardSourceDefinition);
    when(configRepository.getSourceDefinitionFromSource(sourceConnection.getSourceId())).thenReturn(standardSourceDefinition);
    when(
        secretsProcessor.prepareSecretsForOutput(sourceConnection.getConfiguration(), sourceDefinitionSpecificationRead.getConnectionSpecification()))
            .thenReturn(sourceConnection.getConfiguration());

    final SourceReadList actualSourceReadList = sourceHandler.listSourcesForWorkspace(workspaceIdRequestBody);

    assertEquals(expectedSourceRead, actualSourceReadList.getSources().get(0));
    verify(secretsProcessor).prepareSecretsForOutput(sourceConnection.getConfiguration(),
        sourceDefinitionSpecificationRead.getConnectionSpecification());
  }

  @Test
  void testListSourcesForSourceDefinition() throws JsonValidationException, ConfigNotFoundException, IOException {
    final SourceRead expectedSourceRead = SourceHelpers.getSourceRead(sourceConnection, standardSourceDefinition);
    final SourceDefinitionIdRequestBody sourceDefinitionIdRequestBody =
        new SourceDefinitionIdRequestBody().sourceDefinitionId(sourceConnection.getSourceDefinitionId());

    when(configRepository.getSourceConnection(sourceConnection.getSourceId())).thenReturn(sourceConnection);
    when(configRepository.listSourcesForDefinition(sourceConnection.getSourceDefinitionId())).thenReturn(Lists.newArrayList(sourceConnection));
    when(configRepository.getStandardSourceDefinition(sourceDefinitionSpecificationRead.getSourceDefinitionId()))
        .thenReturn(standardSourceDefinition);
    when(configRepository.getSourceDefinitionFromSource(sourceConnection.getSourceId())).thenReturn(standardSourceDefinition);
    when(
        secretsProcessor.prepareSecretsForOutput(sourceConnection.getConfiguration(), sourceDefinitionSpecificationRead.getConnectionSpecification()))
            .thenReturn(sourceConnection.getConfiguration());

    final SourceReadList actualSourceReadList = sourceHandler.listSourcesForSourceDefinition(sourceDefinitionIdRequestBody);

    assertEquals(expectedSourceRead, actualSourceReadList.getSources().get(0));
    verify(secretsProcessor).prepareSecretsForOutput(sourceConnection.getConfiguration(),
        sourceDefinitionSpecificationRead.getConnectionSpecification());
  }

  @Test
  void testDiscoverSchemaForSourceFromSourceIdFailed() throws IOException, JsonValidationException, ConfigNotFoundException {
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    final SourceDiscoverSchemaRequestBody request = new SourceDiscoverSchemaRequestBody().sourceId(source.getSourceId());

    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withProtocolVersion(SOURCE_PROTOCOL_VERSION)
            .withSourceDefinitionId(source.getSourceDefinitionId()));
    when(configRepository.getSourceConnection(source.getSourceId())).thenReturn(source);
    when(synchronousSchedulerClient.createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE, SOURCE_DOCKER_TAG, new Version(SOURCE_PROTOCOL_VERSION),
        false))
        .thenReturn((SynchronousResponse<UUID>) jobResponse);
    when(completedJob.getSuccessOutput()).thenReturn(Optional.empty());
    when(completedJob.getStatus()).thenReturn(JobStatus.FAILED);

    final SourceDiscoverSchemaRead actual = sourceHandler.discoverSchemaForSourceFromSourceId(request);

    assertNull(actual.getCatalog());
    assertNotNull(actual.getJobInfo());
    assertFalse(actual.getJobInfo().getSucceeded());
    verify(configRepository).getSourceConnection(source.getSourceId());
    verify(synchronousSchedulerClient).createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE, SOURCE_DOCKER_TAG, new Version(SOURCE_PROTOCOL_VERSION),
        false);
  }


  @Test
  void testDiscoverSchemaForSourceFromSourceId() throws IOException, JsonValidationException, ConfigNotFoundException {
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    final SourceDiscoverSchemaRequestBody request = new SourceDiscoverSchemaRequestBody().sourceId(source.getSourceId());

    final SynchronousResponse<UUID> discoverResponse = (SynchronousResponse<UUID>) jobResponse;
    final SynchronousJobMetadata metadata = mock(SynchronousJobMetadata.class);
    when(discoverResponse.isSuccess()).thenReturn(true);
    when(discoverResponse.getOutput()).thenReturn(UUID.randomUUID());
    final ActorCatalog actorCatalog = new ActorCatalog()
        .withCatalog(Jsons.jsonNode(airbyteCatalog))
        .withCatalogHash("")
        .withId(UUID.randomUUID());
    when(configRepository.getActorCatalogById(any())).thenReturn(actorCatalog);
    when(discoverResponse.getMetadata()).thenReturn(metadata);
    when(metadata.isSucceeded()).thenReturn(true);

    final ConnectionRead connectionRead = new ConnectionRead();
    final ConnectionReadList connectionReadList = new ConnectionReadList().connections(List.of(connectionRead));
    when(connectionsHandler.listConnectionsForSource(source.getSourceId(), false)).thenReturn(connectionReadList);

    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withProtocolVersion(SOURCE_PROTOCOL_VERSION)
            .withSourceDefinitionId(source.getSourceDefinitionId()));
    when(configRepository.getSourceConnection(source.getSourceId())).thenReturn(source);
    when(configRepository.getActorCatalog(any(), any(), any())).thenReturn(Optional.empty());
    when(synchronousSchedulerClient.createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE, SOURCE_DOCKER_TAG, new Version(SOURCE_PROTOCOL_VERSION),
        false))
        .thenReturn(discoverResponse);

    final SourceDiscoverSchemaRead actual = sourceHandler.discoverSchemaForSourceFromSourceId(request);

    assertNotNull(actual.getCatalog());
    assertEquals(actual.getCatalogId(), discoverResponse.getOutput());
    assertNotNull(actual.getJobInfo());
    assertTrue(actual.getJobInfo().getSucceeded());
    verify(configRepository).getSourceConnection(source.getSourceId());
    verify(configRepository).getActorCatalog(eq(request.getSourceId()), eq(SOURCE_DOCKER_TAG), any());
    verify(synchronousSchedulerClient).createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE, SOURCE_DOCKER_TAG, new Version(SOURCE_PROTOCOL_VERSION),
        false);
  }

  @Test
  void testDiscoverSchemaForSourceFromSourceIdCachedCatalog() throws IOException, JsonValidationException, ConfigNotFoundException {
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    final SourceDiscoverSchemaRequestBody request = new SourceDiscoverSchemaRequestBody().sourceId(source.getSourceId());

    final SynchronousResponse<UUID> discoverResponse = (SynchronousResponse<UUID>) jobResponse;
    final SynchronousJobMetadata metadata = mock(SynchronousJobMetadata.class);
    final UUID thisCatalogId = UUID.randomUUID();
    when(discoverResponse.isSuccess()).thenReturn(true);
    when(discoverResponse.getOutput()).thenReturn(thisCatalogId);
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
        .withId(thisCatalogId);
    when(configRepository.getActorCatalog(any(), any(), any())).thenReturn(Optional.of(actorCatalog));
    when(synchronousSchedulerClient.createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE, SOURCE_DOCKER_TAG, new Version(SOURCE_PROTOCOL_VERSION),
        false))
        .thenReturn(discoverResponse);

    final SourceDiscoverSchemaRead actual = sourceHandler.discoverSchemaForSourceFromSourceId(request);

    assertNotNull(actual.getCatalog());
    assertNotNull(actual.getJobInfo());
    assertEquals(actual.getCatalogId(), discoverResponse.getOutput());
    assertTrue(actual.getJobInfo().getSucceeded());
    verify(configRepository).getSourceConnection(source.getSourceId());
    verify(configRepository).getActorCatalog(eq(request.getSourceId()), any(), any());
    verify(configRepository, never()).writeActorCatalogFetchEvent(any(), any(), any(), any());
    verify(synchronousSchedulerClient, never()).createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE, SOURCE_DOCKER_TAG,
        new Version(SOURCE_PROTOCOL_VERSION), false);
  }

  @Test
  void testDiscoverSchemaForSourceFromSourceIdDisableCache() throws IOException, JsonValidationException, ConfigNotFoundException {
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    final SourceDiscoverSchemaRequestBody request = new SourceDiscoverSchemaRequestBody().sourceId(source.getSourceId()).disableCache(true);

    final SynchronousResponse<UUID> discoverResponse = (SynchronousResponse<UUID>) jobResponse;
    final SynchronousJobMetadata metadata = mock(SynchronousJobMetadata.class);
    when(discoverResponse.isSuccess()).thenReturn(true);
    final UUID discoveredCatalogId = UUID.randomUUID();
    when(discoverResponse.getOutput()).thenReturn(discoveredCatalogId);
    when(discoverResponse.getMetadata()).thenReturn(metadata);
    when(metadata.isSucceeded()).thenReturn(true);

    when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPO)
            .withDockerImageTag(SOURCE_DOCKER_TAG)
            .withProtocolVersion(SOURCE_PROTOCOL_VERSION)
            .withSourceDefinitionId(source.getSourceDefinitionId()));
    when(configRepository.getSourceConnection(source.getSourceId())).thenReturn(source);
    final ActorCatalog actorCatalog = new ActorCatalog()
        .withCatalog(Jsons.jsonNode(airbyteCatalog))
        .withCatalogHash("")
        .withId(discoveredCatalogId);
    when(configRepository.getActorCatalogById(discoveredCatalogId)).thenReturn(actorCatalog);
    when(synchronousSchedulerClient.createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE, SOURCE_DOCKER_TAG, new Version(SOURCE_PROTOCOL_VERSION),
        false))
        .thenReturn(discoverResponse);

    final SourceDiscoverSchemaRead actual = sourceHandler.discoverSchemaForSourceFromSourceId(request);

    assertNotNull(actual.getCatalog());
    assertNotNull(actual.getJobInfo());
    assertTrue(actual.getJobInfo().getSucceeded());
    verify(configRepository).getSourceConnection(source.getSourceId());
    verify(configRepository).getActorCatalog(eq(request.getSourceId()), any(), any());
    verify(synchronousSchedulerClient).createDiscoverSchemaJob(source, SOURCE_DOCKER_IMAGE, SOURCE_DOCKER_TAG, new Version(SOURCE_PROTOCOL_VERSION),
        false);
  }


  @Test
  void testSearchSources() throws JsonValidationException, ConfigNotFoundException, IOException {
    final SourceRead expectedSourceRead = SourceHelpers.getSourceRead(sourceConnection, standardSourceDefinition);

    when(configRepository.getSourceConnection(sourceConnection.getSourceId())).thenReturn(sourceConnection);
    when(configRepository.listSourceConnection()).thenReturn(Lists.newArrayList(sourceConnection));
    when(configRepository.getStandardSourceDefinition(sourceDefinitionSpecificationRead.getSourceDefinitionId()))
        .thenReturn(standardSourceDefinition);
    when(configRepository.getSourceDefinitionFromSource(sourceConnection.getSourceId())).thenReturn(standardSourceDefinition);
    when(
        secretsProcessor.prepareSecretsForOutput(sourceConnection.getConfiguration(), sourceDefinitionSpecificationRead.getConnectionSpecification()))
            .thenReturn(sourceConnection.getConfiguration());

    when(connectionsHandler.matchSearch(new SourceSearch(), expectedSourceRead)).thenReturn(true);
    SourceReadList actualSourceReadList = sourceHandler.searchSources(new SourceSearch());
    assertEquals(1, actualSourceReadList.getSources().size());
    assertEquals(expectedSourceRead, actualSourceReadList.getSources().get(0));

    when(connectionsHandler.matchSearch(new SourceSearch(), expectedSourceRead)).thenReturn(false);
    actualSourceReadList = sourceHandler.searchSources(new SourceSearch());
    assertEquals(0, actualSourceReadList.getSources().size());
  }

  @Test
  void testDeleteSource() throws JsonValidationException, ConfigNotFoundException, IOException {
    final JsonNode newConfiguration = sourceConnection.getConfiguration();
    ((ObjectNode) newConfiguration).put("apiKey", "987-xyz");

    final SourceConnection expectedSourceConnection = Jsons.clone(sourceConnection).withTombstone(true);

    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody().sourceId(sourceConnection.getSourceId());
    final StandardSync standardSync = ConnectionHelpers.generateSyncWithSourceId(sourceConnection.getSourceId());
    final ConnectionRead connectionRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync);
    final ConnectionReadList connectionReadList = new ConnectionReadList().connections(Collections.singletonList(connectionRead));
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(sourceConnection.getWorkspaceId());

    when(configRepository.getSourceConnection(sourceConnection.getSourceId()))
        .thenReturn(sourceConnection)
        .thenReturn(expectedSourceConnection);
    when(secretsRepositoryReader.getSourceConnectionWithSecrets(sourceConnection.getSourceId()))
        .thenReturn(sourceConnection)
        .thenReturn(expectedSourceConnection);
    when(configRepository.getStandardSourceDefinition(sourceDefinitionSpecificationRead.getSourceDefinitionId()))
        .thenReturn(standardSourceDefinition);
    when(configRepository.getSourceDefinitionFromSource(sourceConnection.getSourceId())).thenReturn(standardSourceDefinition);
    when(connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody)).thenReturn(connectionReadList);
    when(
        secretsProcessor.prepareSecretsForOutput(sourceConnection.getConfiguration(), sourceDefinitionSpecificationRead.getConnectionSpecification()))
            .thenReturn(sourceConnection.getConfiguration());

    sourceHandler.deleteSource(sourceIdRequestBody);

    verify(secretsRepositoryWriter).writeSourceConnection(expectedSourceConnection, connectorSpecification);
    verify(connectionsHandler).listConnectionsForWorkspace(workspaceIdRequestBody);
    verify(connectionsHandler).deleteConnection(connectionRead.getConnectionId());
  }

}
