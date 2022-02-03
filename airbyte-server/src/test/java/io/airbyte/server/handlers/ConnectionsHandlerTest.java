/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.api.model.AirbyteCatalog;
import io.airbyte.api.model.ConnectionCreate;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionReadList;
import io.airbyte.api.model.ConnectionSchedule;
import io.airbyte.api.model.ConnectionSearch;
import io.airbyte.api.model.ConnectionStatus;
import io.airbyte.api.model.ConnectionUpdate;
import io.airbyte.api.model.DestinationSearch;
import io.airbyte.api.model.NamespaceDefinitionType;
import io.airbyte.api.model.ResourceRequirements;
import io.airbyte.api.model.SourceSearch;
import io.airbyte.api.model.SyncMode;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DataType;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.Schedule;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.scheduler.persistence.job_factory.SyncJobFactory;
import io.airbyte.server.helpers.ConnectionHelpers;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.helper.ConnectionHelper;
import io.airbyte.workers.worker_run.TemporalWorkerRunFactory;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.Assert;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class ConnectionsHandlerTest {

  private ConfigRepository configRepository;
  private Supplier<UUID> uuidGenerator;

  private WorkerConfigs workerConfigs;
  private ConnectionsHandler connectionsHandler;
  private UUID workspaceId;
  private UUID sourceDefinitionId;
  private UUID sourceId;
  private UUID deletedSourceId;
  private UUID destinationDefinitionId;
  private UUID destinationId;

  private SourceConnection source;
  private DestinationConnection destination;
  private StandardSync standardSync;
  private StandardSync standardSyncDeleted;
  private UUID connectionId;
  private UUID operationId;
  private StandardSyncOperation standardSyncOperation;
  private WorkspaceHelper workspaceHelper;
  private TrackingClient trackingClient;
  private TemporalWorkerRunFactory temporalWorkflowHandler;
  private SyncJobFactory jobFactory;
  private JobPersistence jobPersistence;
  private LogConfigs logConfigs;
  private FeatureFlags featureFlags;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() throws IOException, JsonValidationException, ConfigNotFoundException {
    workerConfigs = new WorkerConfigs(new EnvConfigs());

    workspaceId = UUID.randomUUID();
    sourceDefinitionId = UUID.randomUUID();
    sourceId = UUID.randomUUID();
    destinationDefinitionId = UUID.randomUUID();
    destinationId = UUID.randomUUID();
    connectionId = UUID.randomUUID();
    operationId = UUID.randomUUID();
    source = new SourceConnection()
        .withSourceId(sourceId)
        .withWorkspaceId(workspaceId);
    destination = new DestinationConnection()
        .withDestinationId(destinationId)
        .withWorkspaceId(workspaceId)
        .withConfiguration(Jsons.jsonNode(Collections.singletonMap("apiKey", "123-abc")));
    standardSync = new StandardSync()
        .withConnectionId(connectionId)
        .withName("presto to hudi")
        .withNamespaceDefinition(JobSyncConfig.NamespaceDefinitionType.SOURCE)
        .withNamespaceFormat(null)
        .withPrefix("presto_to_hudi")
        .withStatus(StandardSync.Status.ACTIVE)
        .withCatalog(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog())
        .withSourceId(sourceId)
        .withDestinationId(destinationId)
        .withOperationIds(List.of(operationId))
        .withManual(false)
        .withSchedule(ConnectionHelpers.generateBasicSchedule())
        .withResourceRequirements(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS);
    standardSyncDeleted = new StandardSync()
        .withConnectionId(connectionId)
        .withName("presto to hudi2")
        .withNamespaceDefinition(JobSyncConfig.NamespaceDefinitionType.SOURCE)
        .withNamespaceFormat(null)
        .withPrefix("presto_to_hudi2")
        .withStatus(StandardSync.Status.DEPRECATED)
        .withCatalog(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog())
        .withSourceId(sourceId)
        .withDestinationId(destinationId)
        .withOperationIds(List.of(operationId))
        .withManual(false)
        .withSchedule(ConnectionHelpers.generateBasicSchedule())
        .withResourceRequirements(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS);

    standardSyncOperation = new StandardSyncOperation()
        .withOperationId(operationId)
        .withWorkspaceId(workspaceId);

    configRepository = mock(ConfigRepository.class);
    uuidGenerator = mock(Supplier.class);
    workspaceHelper = mock(WorkspaceHelper.class);
    trackingClient = mock(TrackingClient.class);
    featureFlags = mock(FeatureFlags.class);
    temporalWorkflowHandler = mock(TemporalWorkerRunFactory.class);

    when(workspaceHelper.getWorkspaceForSourceIdIgnoreExceptions(sourceId)).thenReturn(workspaceId);
    when(workspaceHelper.getWorkspaceForSourceIdIgnoreExceptions(deletedSourceId)).thenReturn(workspaceId);
    when(workspaceHelper.getWorkspaceForDestinationIdIgnoreExceptions(destinationId)).thenReturn(workspaceId);
    when(workspaceHelper.getWorkspaceForOperationIdIgnoreExceptions(operationId)).thenReturn(workspaceId);

    when(featureFlags.usesNewScheduler()).thenReturn(false);
  }

  // TODO: bmoric move to a mock
  private ConnectionHelper connectionHelper;

  @Nested
  class MockedConnectionHelper {

    @BeforeEach
    void setUp() {
      connectionHelper = mock(ConnectionHelper.class);

      connectionsHandler = new ConnectionsHandler(
          configRepository,
          uuidGenerator,
          workspaceHelper,
          trackingClient,
          temporalWorkflowHandler,
          featureFlags,
          connectionHelper,
          workerConfigs);
    }

    @Test
    void testUpdateConnectionWithNewScheduler() throws JsonValidationException, ConfigNotFoundException, IOException {
      final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
          .connectionId(standardSync.getConnectionId());

      when(featureFlags.usesNewScheduler()).thenReturn(true);
      connectionsHandler.updateConnection(connectionUpdate, false);

      verify(connectionHelper).updateConnection(connectionUpdate);
      verify(temporalWorkflowHandler).update(connectionUpdate);
    }

    @Test
    void testUpdateConnectionWithNewSchedulerForReset() throws JsonValidationException, ConfigNotFoundException, IOException {
      final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
          .connectionId(standardSync.getConnectionId());

      when(featureFlags.usesNewScheduler()).thenReturn(true);
      connectionsHandler.updateConnection(connectionUpdate, true);

      verify(connectionHelper).updateConnection(connectionUpdate);
      verifyNoInteractions(temporalWorkflowHandler);
    }

  }

  @Nested
  class UnMockedConnectionHelper {

    @BeforeEach
    void setUp() {
      connectionHelper = new ConnectionHelper(configRepository, workspaceHelper, workerConfigs);

      connectionsHandler = new ConnectionsHandler(
          configRepository,
          uuidGenerator,
          workspaceHelper,
          trackingClient,
          temporalWorkflowHandler,
          featureFlags,
          connectionHelper,
          workerConfigs);
    }

    @Test
    void testCreateConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
      when(uuidGenerator.get()).thenReturn(standardSync.getConnectionId());
      final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
          .withName("source-test")
          .withSourceDefinitionId(UUID.randomUUID());
      final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
          .withName("destination-test")
          .withDestinationDefinitionId(UUID.randomUUID());
      when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);
      when(configRepository.getSourceDefinitionFromConnection(standardSync.getConnectionId())).thenReturn(sourceDefinition);
      when(configRepository.getDestinationDefinitionFromConnection(standardSync.getConnectionId())).thenReturn(destinationDefinition);

      final AirbyteCatalog catalog = ConnectionHelpers.generateBasicApiCatalog();

      final ConnectionCreate connectionCreate = new ConnectionCreate()
          .sourceId(standardSync.getSourceId())
          .destinationId(standardSync.getDestinationId())
          .operationIds(standardSync.getOperationIds())
          .name("presto to hudi")
          .namespaceDefinition(NamespaceDefinitionType.SOURCE)
          .namespaceFormat(null)
          .prefix("presto_to_hudi")
          .status(ConnectionStatus.ACTIVE)
          .schedule(ConnectionHelpers.generateBasicConnectionSchedule())
          .syncCatalog(catalog)
          .resourceRequirements(new io.airbyte.api.model.ResourceRequirements()
              .cpuRequest(standardSync.getResourceRequirements().getCpuRequest())
              .cpuLimit(standardSync.getResourceRequirements().getCpuLimit())
              .memoryRequest(standardSync.getResourceRequirements().getMemoryRequest())
              .memoryLimit(standardSync.getResourceRequirements().getMemoryLimit()));

      final ConnectionRead actualConnectionRead = connectionsHandler.createConnection(connectionCreate);

      final ConnectionRead expectedConnectionRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync);

      assertEquals(expectedConnectionRead, actualConnectionRead);

      verify(configRepository).writeStandardSync(standardSync);
    }

    @Test
    void testValidateConnectionCreateSourceAndDestinationInDifferenceWorkspace() {
      when(workspaceHelper.getWorkspaceForDestinationIdIgnoreExceptions(destinationId)).thenReturn(UUID.randomUUID());

      final ConnectionCreate connectionCreate = new ConnectionCreate()
          .sourceId(standardSync.getSourceId())
          .destinationId(standardSync.getDestinationId());

      assertThrows(IllegalArgumentException.class, () -> connectionsHandler.createConnection(connectionCreate));
    }

    @Test
    void testValidateConnectionCreateOperationInDifferentWorkspace() {
      when(workspaceHelper.getWorkspaceForOperationIdIgnoreExceptions(operationId)).thenReturn(UUID.randomUUID());

      final ConnectionCreate connectionCreate = new ConnectionCreate()
          .sourceId(standardSync.getSourceId())
          .destinationId(standardSync.getDestinationId())
          .operationIds(Collections.singletonList(operationId));

      assertThrows(IllegalArgumentException.class, () -> connectionsHandler.createConnection(connectionCreate));
    }

    @Test
    void testCreateConnectionWithBadDefinitionIds() throws JsonValidationException, ConfigNotFoundException, IOException {
      when(uuidGenerator.get()).thenReturn(standardSync.getConnectionId());
      final UUID sourceIdBad = UUID.randomUUID();
      final UUID destinationIdBad = UUID.randomUUID();

      final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
          .withName("source-test")
          .withSourceDefinitionId(UUID.randomUUID());
      final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
          .withName("destination-test")
          .withDestinationDefinitionId(UUID.randomUUID());
      when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);
      when(configRepository.getSourceDefinitionFromConnection(standardSync.getConnectionId())).thenReturn(sourceDefinition);
      when(configRepository.getDestinationDefinitionFromConnection(standardSync.getConnectionId())).thenReturn(destinationDefinition);

      when(configRepository.getSourceConnection(sourceIdBad))
          .thenThrow(new ConfigNotFoundException(ConfigSchema.SOURCE_CONNECTION, sourceIdBad));
      when(configRepository.getDestinationConnection(destinationIdBad))
          .thenThrow(new ConfigNotFoundException(ConfigSchema.DESTINATION_CONNECTION, destinationIdBad));

      final AirbyteCatalog catalog = ConnectionHelpers.generateBasicApiCatalog();

      final ConnectionCreate connectionCreateBadSource = new ConnectionCreate()
          .sourceId(sourceIdBad)
          .destinationId(standardSync.getDestinationId())
          .operationIds(standardSync.getOperationIds())
          .name("presto to hudi")
          .namespaceDefinition(NamespaceDefinitionType.SOURCE)
          .namespaceFormat(null)
          .prefix("presto_to_hudi")
          .status(ConnectionStatus.ACTIVE)
          .schedule(ConnectionHelpers.generateBasicConnectionSchedule())
          .syncCatalog(catalog);

      assertThrows(ConfigNotFoundException.class, () -> connectionsHandler.createConnection(connectionCreateBadSource));

      final ConnectionCreate connectionCreateBadDestination = new ConnectionCreate()
          .sourceId(standardSync.getSourceId())
          .destinationId(destinationIdBad)
          .operationIds(standardSync.getOperationIds())
          .name("presto to hudi")
          .namespaceDefinition(NamespaceDefinitionType.SOURCE)
          .namespaceFormat(null)
          .prefix("presto_to_hudi")
          .status(ConnectionStatus.ACTIVE)
          .schedule(ConnectionHelpers.generateBasicConnectionSchedule())
          .syncCatalog(catalog);

      assertThrows(ConfigNotFoundException.class, () -> connectionsHandler.createConnection(connectionCreateBadDestination));

    }

    @Test
    void testUpdateConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
      final AirbyteCatalog catalog = ConnectionHelpers.generateBasicApiCatalog();
      catalog.getStreams().get(0).getStream().setName("azkaban_users");
      catalog.getStreams().get(0).getConfig().setAliasName("azkaban_users");

      final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
          .namespaceDefinition(Enums.convertTo(standardSync.getNamespaceDefinition(), NamespaceDefinitionType.class))
          .namespaceFormat(standardSync.getNamespaceFormat())
          .prefix(standardSync.getPrefix())
          .connectionId(standardSync.getConnectionId())
          .operationIds(standardSync.getOperationIds())
          .status(ConnectionStatus.INACTIVE)
          .schedule(null)
          .syncCatalog(catalog)
          .resourceRequirements(new ResourceRequirements()
              .cpuLimit(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getCpuLimit())
              .cpuRequest(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getCpuRequest())
              .memoryLimit(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getMemoryLimit())
              .memoryRequest(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getMemoryRequest()));

      final ConfiguredAirbyteCatalog configuredCatalog = ConnectionHelpers.generateBasicConfiguredAirbyteCatalog();
      configuredCatalog.getStreams().get(0).getStream().withName("azkaban_users");

      final StandardSync updatedStandardSync = new StandardSync()
          .withConnectionId(standardSync.getConnectionId())
          .withName("presto to hudi")
          .withNamespaceDefinition(io.airbyte.config.JobSyncConfig.NamespaceDefinitionType.SOURCE)
          .withNamespaceFormat(standardSync.getNamespaceFormat())
          .withPrefix("presto_to_hudi")
          .withSourceId(standardSync.getSourceId())
          .withDestinationId(standardSync.getDestinationId())
          .withOperationIds(standardSync.getOperationIds())
          .withStatus(StandardSync.Status.INACTIVE)
          .withCatalog(configuredCatalog)
          .withManual(true)
          .withResourceRequirements(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS);

      when(configRepository.getStandardSync(standardSync.getConnectionId()))
          .thenReturn(standardSync)
          .thenReturn(updatedStandardSync);

      final ConnectionRead actualConnectionRead = connectionsHandler.updateConnection(connectionUpdate);

      final ConnectionRead expectedConnectionRead = ConnectionHelpers.generateExpectedConnectionRead(
          standardSync.getConnectionId(),
          standardSync.getSourceId(),
          standardSync.getDestinationId(),
          standardSync.getOperationIds())
          .schedule(null)
          .syncCatalog(catalog)
          .status(ConnectionStatus.INACTIVE);

      assertEquals(expectedConnectionRead, actualConnectionRead);

      verify(configRepository).writeStandardSync(updatedStandardSync);
    }

    @Test
    void testValidateConnectionUpdateOperationInDifferentWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
      when(workspaceHelper.getWorkspaceForOperationIdIgnoreExceptions(operationId)).thenReturn(UUID.randomUUID());
      when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);

      final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
          .connectionId(standardSync.getConnectionId())
          .operationIds(Collections.singletonList(operationId));

      assertThrows(IllegalArgumentException.class, () -> connectionsHandler.updateConnection(connectionUpdate));
    }

    @Test
    void testGetConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
      when(configRepository.getStandardSync(standardSync.getConnectionId()))
          .thenReturn(standardSync);

      final ConnectionRead actualConnectionRead = connectionsHandler.getConnection(standardSync.getConnectionId());

      assertEquals(ConnectionHelpers.generateExpectedConnectionRead(standardSync), actualConnectionRead);
    }

    @Test
    void testListConnectionsForWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
      when(configRepository.listStandardSyncs())
          .thenReturn(Lists.newArrayList(standardSync, standardSyncDeleted));
      when(configRepository.getSourceConnection(source.getSourceId()))
          .thenReturn(source);
      when(configRepository.getStandardSync(standardSync.getConnectionId()))
          .thenReturn(standardSync);

      final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(source.getWorkspaceId());
      final ConnectionReadList actualConnectionReadList = connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody);
      assertEquals(1, actualConnectionReadList.getConnections().size());
      assertEquals(
          ConnectionHelpers.generateExpectedConnectionRead(standardSync),
          actualConnectionReadList.getConnections().get(0));

      final ConnectionReadList actualConnectionReadListWithDeleted = connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody, true);
      final List<ConnectionRead> connections = actualConnectionReadListWithDeleted.getConnections();
      assertEquals(2, connections.size());
      assertEquals(ConnectionHelpers.generateExpectedConnectionRead(standardSync), connections.get(0));
      assertEquals(ConnectionHelpers.generateExpectedConnectionRead(standardSyncDeleted), connections.get(1));

    }

    @Test
    void testListConnections() throws JsonValidationException, ConfigNotFoundException, IOException {
      when(configRepository.listStandardSyncs())
          .thenReturn(Lists.newArrayList(standardSync));
      when(configRepository.getSourceConnection(source.getSourceId()))
          .thenReturn(source);
      when(configRepository.getStandardSync(standardSync.getConnectionId()))
          .thenReturn(standardSync);

      final ConnectionReadList actualConnectionReadList = connectionsHandler.listConnections();

      assertEquals(
          ConnectionHelpers.generateExpectedConnectionRead(standardSync),
          actualConnectionReadList.getConnections().get(0));
    }

    @Test
    void testSearchConnections() throws JsonValidationException, ConfigNotFoundException, IOException {
      final ConnectionRead connectionRead1 = ConnectionHelpers.connectionReadFromStandardSync(standardSync);
      final StandardSync standardSync2 = new StandardSync()
          .withConnectionId(UUID.randomUUID())
          .withName("test connection")
          .withNamespaceDefinition(JobSyncConfig.NamespaceDefinitionType.CUSTOMFORMAT)
          .withNamespaceFormat("ns_format")
          .withPrefix("test_prefix")
          .withStatus(StandardSync.Status.ACTIVE)
          .withCatalog(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog())
          .withSourceId(sourceId)
          .withDestinationId(destinationId)
          .withOperationIds(List.of(operationId))
          .withManual(true)
          .withResourceRequirements(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS);
      final ConnectionRead connectionRead2 = ConnectionHelpers.connectionReadFromStandardSync(standardSync2);
      final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
          .withName("source-test")
          .withSourceDefinitionId(UUID.randomUUID());
      final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
          .withName("destination-test")
          .withDestinationDefinitionId(UUID.randomUUID());

      when(configRepository.listStandardSyncs())
          .thenReturn(Lists.newArrayList(standardSync, standardSync2));
      when(configRepository.getSourceConnection(source.getSourceId()))
          .thenReturn(source);
      when(configRepository.getDestinationConnection(destination.getDestinationId()))
          .thenReturn(destination);
      when(configRepository.getStandardSync(standardSync.getConnectionId()))
          .thenReturn(standardSync);
      when(configRepository.getStandardSync(standardSync2.getConnectionId()))
          .thenReturn(standardSync2);
      when(configRepository.getStandardSourceDefinition(source.getSourceDefinitionId()))
          .thenReturn(sourceDefinition);
      when(configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId()))
          .thenReturn(destinationDefinition);

      final ConnectionSearch connectionSearch = new ConnectionSearch();
      ConnectionReadList actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(1, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead1, actualConnectionReadList.getConnections().get(0));

      connectionSearch.namespaceDefinition(null);
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(2, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead1, actualConnectionReadList.getConnections().get(0));
      assertEquals(connectionRead2, actualConnectionReadList.getConnections().get(1));

      final SourceSearch sourceSearch = new SourceSearch().sourceId(UUID.randomUUID());
      connectionSearch.setSource(sourceSearch);
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(0, actualConnectionReadList.getConnections().size());

      sourceSearch.sourceId(connectionRead1.getSourceId());
      connectionSearch.setSource(sourceSearch);
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(2, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead1, actualConnectionReadList.getConnections().get(0));
      assertEquals(connectionRead2, actualConnectionReadList.getConnections().get(1));

      final DestinationSearch destinationSearch = new DestinationSearch();
      connectionSearch.setDestination(destinationSearch);
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(2, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead1, actualConnectionReadList.getConnections().get(0));
      assertEquals(connectionRead2, actualConnectionReadList.getConnections().get(1));

      destinationSearch.connectionConfiguration(Jsons.jsonNode(Collections.singletonMap("apiKey", "not-found")));
      connectionSearch.setDestination(destinationSearch);
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(0, actualConnectionReadList.getConnections().size());

      destinationSearch.connectionConfiguration(Jsons.jsonNode(Collections.singletonMap("apiKey", "123-abc")));
      connectionSearch.setDestination(destinationSearch);
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(2, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead1, actualConnectionReadList.getConnections().get(0));
      assertEquals(connectionRead2, actualConnectionReadList.getConnections().get(1));

      connectionSearch.name("non-existent");
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(0, actualConnectionReadList.getConnections().size());

      connectionSearch.name(connectionRead1.getName());
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(1, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead1, actualConnectionReadList.getConnections().get(0));

      connectionSearch.name(connectionRead2.getName());
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(1, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead2, actualConnectionReadList.getConnections().get(0));

      connectionSearch.namespaceDefinition(connectionRead1.getNamespaceDefinition());
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(0, actualConnectionReadList.getConnections().size());

      connectionSearch.name(null);
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(1, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead1, actualConnectionReadList.getConnections().get(0));

      connectionSearch.namespaceDefinition(connectionRead2.getNamespaceDefinition());
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(1, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead2, actualConnectionReadList.getConnections().get(0));

      connectionSearch.namespaceDefinition(null);
      connectionSearch.status(ConnectionStatus.INACTIVE);
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(0, actualConnectionReadList.getConnections().size());

      connectionSearch.status(ConnectionStatus.ACTIVE);
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(2, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead1, actualConnectionReadList.getConnections().get(0));
      assertEquals(connectionRead2, actualConnectionReadList.getConnections().get(1));

      connectionSearch.prefix(connectionRead1.getPrefix());
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(1, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead1, actualConnectionReadList.getConnections().get(0));

      connectionSearch.prefix(connectionRead2.getPrefix());
      actualConnectionReadList = connectionsHandler.searchConnections(connectionSearch);
      assertEquals(1, actualConnectionReadList.getConnections().size());
      assertEquals(connectionRead2, actualConnectionReadList.getConnections().get(0));
    }

    @Test
    void testDeleteConnection() throws JsonValidationException, IOException, ConfigNotFoundException {

      final ConnectionRead connectionRead = ConnectionHelpers.generateExpectedConnectionRead(
          standardSync.getConnectionId(),
          standardSync.getSourceId(),
          standardSync.getDestinationId(),
          standardSync.getOperationIds());

      final ConnectionUpdate expectedConnectionUpdate = new ConnectionUpdate()
          .namespaceDefinition(connectionRead.getNamespaceDefinition())
          .namespaceFormat(connectionRead.getNamespaceFormat())
          .prefix(connectionRead.getPrefix())
          .connectionId(connectionRead.getConnectionId())
          .operationIds(connectionRead.getOperationIds())
          .status(ConnectionStatus.DEPRECATED)
          .syncCatalog(connectionRead.getSyncCatalog())
          .schedule(connectionRead.getSchedule())
          .resourceRequirements(connectionRead.getResourceRequirements());

      final ConnectionsHandler spiedConnectionsHandler = spy(connectionsHandler);
      doReturn(connectionRead).when(spiedConnectionsHandler).getConnection(connectionId);
      doReturn(null).when(spiedConnectionsHandler).updateConnection(expectedConnectionUpdate);

      spiedConnectionsHandler.deleteConnection(connectionId);

      verify(spiedConnectionsHandler).getConnection(connectionId);
      verify(spiedConnectionsHandler).updateConnection(expectedConnectionUpdate);
    }

    @Test
    void failOnUnmatchedWorkspacesInCreate() throws JsonValidationException, ConfigNotFoundException, IOException {
      when(workspaceHelper.getWorkspaceForSourceIdIgnoreExceptions(standardSync.getSourceId())).thenReturn(UUID.randomUUID());
      when(workspaceHelper.getWorkspaceForDestinationIdIgnoreExceptions(standardSync.getDestinationId())).thenReturn(UUID.randomUUID());

      when(uuidGenerator.get()).thenReturn(standardSync.getConnectionId());
      final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
          .withName("source-test")
          .withSourceDefinitionId(UUID.randomUUID());
      final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
          .withName("destination-test")
          .withDestinationDefinitionId(UUID.randomUUID());
      when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);
      when(configRepository.getSourceDefinitionFromConnection(standardSync.getConnectionId())).thenReturn(sourceDefinition);
      when(configRepository.getDestinationDefinitionFromConnection(standardSync.getConnectionId())).thenReturn(destinationDefinition);

      final AirbyteCatalog catalog = ConnectionHelpers.generateBasicApiCatalog();

      final ConnectionCreate connectionCreate = new ConnectionCreate()
          .sourceId(standardSync.getSourceId())
          .destinationId(standardSync.getDestinationId())
          .operationIds(standardSync.getOperationIds())
          .name("presto to hudi")
          .namespaceDefinition(NamespaceDefinitionType.SOURCE)
          .namespaceFormat(null)
          .prefix("presto_to_hudi")
          .status(ConnectionStatus.ACTIVE)
          .schedule(ConnectionHelpers.generateBasicConnectionSchedule())
          .syncCatalog(catalog)
          .resourceRequirements(new io.airbyte.api.model.ResourceRequirements()
              .cpuRequest(standardSync.getResourceRequirements().getCpuRequest())
              .cpuLimit(standardSync.getResourceRequirements().getCpuLimit())
              .memoryRequest(standardSync.getResourceRequirements().getMemoryRequest())
              .memoryLimit(standardSync.getResourceRequirements().getMemoryLimit()));

      Assert.assertThrows(IllegalArgumentException.class, () -> {
        connectionsHandler.createConnection(connectionCreate);
      });
    }

    @Test
    void testEnumConversion() {
      assertTrue(Enums.isCompatible(ConnectionStatus.class, StandardSync.Status.class));
      assertTrue(Enums.isCompatible(io.airbyte.config.SyncMode.class, SyncMode.class));
      assertTrue(Enums.isCompatible(StandardSync.Status.class, ConnectionStatus.class));
      assertTrue(Enums.isCompatible(ConnectionSchedule.TimeUnitEnum.class, Schedule.TimeUnit.class));
      assertTrue(Enums.isCompatible(io.airbyte.api.model.DataType.class, DataType.class));
      assertTrue(Enums.isCompatible(DataType.class, io.airbyte.api.model.DataType.class));
      assertTrue(Enums.isCompatible(NamespaceDefinitionType.class, io.airbyte.config.JobSyncConfig.NamespaceDefinitionType.class));
    }

  }

}
