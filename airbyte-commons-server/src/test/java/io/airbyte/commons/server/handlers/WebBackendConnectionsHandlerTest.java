/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyBoolean;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.inOrder;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Lists;
import io.airbyte.api.model.generated.AirbyteCatalog;
import io.airbyte.api.model.generated.AirbyteStream;
import io.airbyte.api.model.generated.AirbyteStreamAndConfiguration;
import io.airbyte.api.model.generated.AttemptRead;
import io.airbyte.api.model.generated.AttemptStatus;
import io.airbyte.api.model.generated.CatalogDiff;
import io.airbyte.api.model.generated.ConnectionCreate;
import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.ConnectionRead;
import io.airbyte.api.model.generated.ConnectionSchedule;
import io.airbyte.api.model.generated.ConnectionSchedule.TimeUnitEnum;
import io.airbyte.api.model.generated.ConnectionState;
import io.airbyte.api.model.generated.ConnectionStateType;
import io.airbyte.api.model.generated.ConnectionStatus;
import io.airbyte.api.model.generated.ConnectionUpdate;
import io.airbyte.api.model.generated.DestinationIdRequestBody;
import io.airbyte.api.model.generated.DestinationRead;
import io.airbyte.api.model.generated.DestinationSyncMode;
import io.airbyte.api.model.generated.FieldAdd;
import io.airbyte.api.model.generated.FieldRemove;
import io.airbyte.api.model.generated.FieldTransform;
import io.airbyte.api.model.generated.Geography;
import io.airbyte.api.model.generated.JobConfigType;
import io.airbyte.api.model.generated.JobInfoRead;
import io.airbyte.api.model.generated.JobRead;
import io.airbyte.api.model.generated.JobStatus;
import io.airbyte.api.model.generated.JobWithAttemptsRead;
import io.airbyte.api.model.generated.NamespaceDefinitionType;
import io.airbyte.api.model.generated.NonBreakingChangesPreference;
import io.airbyte.api.model.generated.OperationRead;
import io.airbyte.api.model.generated.OperationReadList;
import io.airbyte.api.model.generated.OperationUpdate;
import io.airbyte.api.model.generated.ResourceRequirements;
import io.airbyte.api.model.generated.SchemaChange;
import io.airbyte.api.model.generated.SelectedFieldInfo;
import io.airbyte.api.model.generated.SourceDiscoverSchemaRead;
import io.airbyte.api.model.generated.SourceDiscoverSchemaRequestBody;
import io.airbyte.api.model.generated.SourceIdRequestBody;
import io.airbyte.api.model.generated.SourceRead;
import io.airbyte.api.model.generated.StreamDescriptor;
import io.airbyte.api.model.generated.StreamTransform;
import io.airbyte.api.model.generated.StreamTransform.TransformTypeEnum;
import io.airbyte.api.model.generated.SyncMode;
import io.airbyte.api.model.generated.SynchronousJobRead;
import io.airbyte.api.model.generated.WebBackendConnectionCreate;
import io.airbyte.api.model.generated.WebBackendConnectionListItem;
import io.airbyte.api.model.generated.WebBackendConnectionListRequestBody;
import io.airbyte.api.model.generated.WebBackendConnectionRead;
import io.airbyte.api.model.generated.WebBackendConnectionReadList;
import io.airbyte.api.model.generated.WebBackendConnectionRequestBody;
import io.airbyte.api.model.generated.WebBackendConnectionUpdate;
import io.airbyte.api.model.generated.WebBackendOperationCreateOrUpdate;
import io.airbyte.api.model.generated.WebBackendWorkspaceState;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.server.handlers.helpers.CatalogConverter;
import io.airbyte.commons.server.helpers.ConnectionHelpers;
import io.airbyte.commons.server.helpers.DestinationDefinitionHelpers;
import io.airbyte.commons.server.helpers.DestinationHelpers;
import io.airbyte.commons.server.helpers.SourceDefinitionHelpers;
import io.airbyte.commons.server.helpers.SourceHelpers;
import io.airbyte.commons.server.scheduler.EventRunner;
import io.airbyte.commons.temporal.TemporalClient.ManualOperationResult;
import io.airbyte.config.ActorCatalog;
import io.airbyte.config.ActorCatalogFetchEvent;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.ConfigRepository.DestinationAndDefinition;
import io.airbyte.config.persistence.ConfigRepository.SourceAndDefinition;
import io.airbyte.config.persistence.ConfigRepository.StandardSyncQuery;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.lang.reflect.Method;
import java.time.Instant;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.InOrder;

class WebBackendConnectionsHandlerTest {

  private ConnectionsHandler connectionsHandler;
  private OperationsHandler operationsHandler;
  private SchedulerHandler schedulerHandler;
  private StateHandler stateHandler;
  private WebBackendConnectionsHandler wbHandler;
  private SourceRead sourceRead;
  private ConnectionRead connectionRead;
  private ConnectionRead brokenConnectionRead;
  private WebBackendConnectionListItem expectedListItem;
  private OperationReadList operationReadList;
  private OperationReadList brokenOperationReadList;
  private WebBackendConnectionRead expected;
  private WebBackendConnectionRead expectedWithNewSchema;
  private WebBackendConnectionRead expectedWithNewSchemaAndBreakingChange;
  private WebBackendConnectionRead expectedWithNewSchemaBroken;
  private WebBackendConnectionRead expectedNoDiscoveryWithNewSchema;
  private EventRunner eventRunner;
  private ConfigRepository configRepository;

  private static final String STREAM1 = "stream1";
  private static final String STREAM2 = "stream2";
  private static final String FIELD1 = "field1";
  private static final String FIELD2 = "field2";
  private static final String FIELD3 = "field3";
  private static final String FIELD5 = "field5";

  // needs to match name of file in src/test/resources/icons
  private static final String SOURCE_ICON = "test-source.svg";
  private static final String DESTINATION_ICON = "test-destination.svg";
  private static final String SVG = "<svg>";

  @BeforeEach
  void setup() throws IOException, JsonValidationException, ConfigNotFoundException {
    connectionsHandler = mock(ConnectionsHandler.class);
    stateHandler = mock(StateHandler.class);
    operationsHandler = mock(OperationsHandler.class);
    final SourceHandler sourceHandler = mock(SourceHandler.class);
    final DestinationHandler destinationHandler = mock(DestinationHandler.class);
    final JobHistoryHandler jobHistoryHandler = mock(JobHistoryHandler.class);
    configRepository = mock(ConfigRepository.class);
    schedulerHandler = mock(SchedulerHandler.class);
    eventRunner = mock(EventRunner.class);
    wbHandler = new WebBackendConnectionsHandler(
        connectionsHandler,
        stateHandler,
        sourceHandler,
        destinationHandler,
        jobHistoryHandler,
        schedulerHandler,
        operationsHandler,
        eventRunner,
        configRepository);

    final StandardSourceDefinition sourceDefinition = SourceDefinitionHelpers.generateSourceDefinition();
    sourceDefinition.setIcon(SOURCE_ICON);
    final SourceConnection source = SourceHelpers.generateSource(sourceDefinition.getSourceDefinitionId());
    sourceRead = SourceHelpers.getSourceRead(source, sourceDefinition);

    final StandardDestinationDefinition destinationDefinition = DestinationDefinitionHelpers.generateDestination();
    destinationDefinition.setIcon(DESTINATION_ICON);
    final DestinationConnection destination = DestinationHelpers.generateDestination(destinationDefinition.getDestinationDefinitionId());
    final DestinationRead destinationRead = DestinationHelpers.getDestinationRead(destination, destinationDefinition);

    final StandardSync standardSync =
        ConnectionHelpers.generateSyncWithSourceAndDestinationId(source.getSourceId(), destination.getDestinationId(), false, Status.ACTIVE);
    final StandardSync brokenStandardSync =
        ConnectionHelpers.generateSyncWithSourceAndDestinationId(source.getSourceId(), destination.getDestinationId(), true, Status.INACTIVE);

    when(configRepository.listWorkspaceStandardSyncs(new StandardSyncQuery(sourceRead.getWorkspaceId(), null, null, false)))
        .thenReturn(Collections.singletonList(standardSync));
    when(configRepository.getSourceAndDefinitionsFromSourceIds(Collections.singletonList(source.getSourceId())))
        .thenReturn(Collections.singletonList(new SourceAndDefinition(source, sourceDefinition)));
    when(configRepository.getDestinationAndDefinitionsFromDestinationIds(Collections.singletonList(destination.getDestinationId())))
        .thenReturn(Collections.singletonList(new DestinationAndDefinition(destination, destinationDefinition)));

    connectionRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync);
    brokenConnectionRead = ConnectionHelpers.generateExpectedConnectionRead(brokenStandardSync);
    operationReadList = new OperationReadList()
        .operations(List.of(new OperationRead()
            .operationId(connectionRead.getOperationIds().get(0))
            .name("Test Operation")));
    brokenOperationReadList = new OperationReadList()
        .operations(List.of(new OperationRead()
            .operationId(brokenConnectionRead.getOperationIds().get(0))
            .name("Test Operation")));

    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody();
    sourceIdRequestBody.setSourceId(connectionRead.getSourceId());
    when(sourceHandler.getSource(sourceIdRequestBody)).thenReturn(sourceRead);

    final DestinationIdRequestBody destinationIdRequestBody = new DestinationIdRequestBody();
    destinationIdRequestBody.setDestinationId(connectionRead.getDestinationId());
    when(destinationHandler.getDestination(destinationIdRequestBody)).thenReturn(destinationRead);

    final Instant now = Instant.now();
    final JobWithAttemptsRead jobRead = new JobWithAttemptsRead()
        .job(new JobRead()
            .configId(connectionRead.getConnectionId().toString())
            .configType(JobConfigType.SYNC)
            .id(10L)
            .status(JobStatus.SUCCEEDED)
            .createdAt(now.getEpochSecond())
            .updatedAt(now.getEpochSecond()))
        .attempts(Lists.newArrayList(new AttemptRead()
            .id(12L)
            .status(AttemptStatus.SUCCEEDED)
            .bytesSynced(100L)
            .recordsSynced(15L)
            .createdAt(now.getEpochSecond())
            .updatedAt(now.getEpochSecond())
            .endedAt(now.getEpochSecond())));

    when(jobHistoryHandler.getLatestSyncJob(connectionRead.getConnectionId())).thenReturn(Optional.of(jobRead.getJob()));

    when(jobHistoryHandler.getLatestSyncJobsForConnections(Collections.singletonList(connectionRead.getConnectionId())))
        .thenReturn(Collections.singletonList(jobRead.getJob()));

    final JobWithAttemptsRead brokenJobRead = new JobWithAttemptsRead()
        .job(new JobRead()
            .configId(brokenConnectionRead.getConnectionId().toString())
            .configType(JobConfigType.SYNC)
            .id(10L)
            .status(JobStatus.SUCCEEDED)
            .createdAt(now.getEpochSecond())
            .updatedAt(now.getEpochSecond()))
        .attempts(Lists.newArrayList(new AttemptRead()
            .id(12L)
            .status(AttemptStatus.SUCCEEDED)
            .bytesSynced(100L)
            .recordsSynced(15L)
            .createdAt(now.getEpochSecond())
            .updatedAt(now.getEpochSecond())
            .endedAt(now.getEpochSecond())));

    when(jobHistoryHandler.getLatestSyncJob(brokenConnectionRead.getConnectionId())).thenReturn(Optional.of(brokenJobRead.getJob()));

    when(jobHistoryHandler.getLatestSyncJobsForConnections(Collections.singletonList(brokenConnectionRead.getConnectionId())))
        .thenReturn(Collections.singletonList(brokenJobRead.getJob()));

    expectedListItem = ConnectionHelpers.generateExpectedWebBackendConnectionListItem(
        standardSync,
        sourceRead,
        destinationRead,
        false,
        jobRead.getJob().getCreatedAt(),
        jobRead.getJob().getStatus(),
        SchemaChange.NO_CHANGE);

    expected = expectedWebBackendConnectionReadObject(connectionRead, sourceRead, destinationRead, operationReadList, SchemaChange.NO_CHANGE, now,
        connectionRead.getSyncCatalog(), connectionRead.getSourceCatalogId());
    expectedNoDiscoveryWithNewSchema = expectedWebBackendConnectionReadObject(connectionRead, sourceRead, destinationRead, operationReadList,
        SchemaChange.NON_BREAKING, now, connectionRead.getSyncCatalog(), connectionRead.getSourceCatalogId());

    final AirbyteCatalog modifiedCatalog = ConnectionHelpers.generateMultipleStreamsApiCatalog(2);
    final SourceDiscoverSchemaRequestBody sourceDiscoverSchema = new SourceDiscoverSchemaRequestBody();
    sourceDiscoverSchema.setSourceId(connectionRead.getSourceId());
    sourceDiscoverSchema.setDisableCache(true);
    when(schedulerHandler.discoverSchemaForSourceFromSourceId(sourceDiscoverSchema)).thenReturn(
        new SourceDiscoverSchemaRead()
            .jobInfo(mock(SynchronousJobRead.class))
            .catalog(modifiedCatalog));

    expectedWithNewSchema = expectedWebBackendConnectionReadObject(connectionRead, sourceRead, destinationRead,
        new OperationReadList().operations(expected.getOperations()), SchemaChange.NON_BREAKING, now, modifiedCatalog, null)
            .catalogDiff(new CatalogDiff().transforms(List.of(
                new StreamTransform().transformType(TransformTypeEnum.ADD_STREAM)
                    .streamDescriptor(new io.airbyte.api.model.generated.StreamDescriptor().name("users-data1"))
                    .updateStream(null))));

    expectedWithNewSchemaAndBreakingChange = expectedWebBackendConnectionReadObject(brokenConnectionRead, sourceRead, destinationRead,
        new OperationReadList().operations(expected.getOperations()), SchemaChange.BREAKING, now, modifiedCatalog, null)
            .catalogDiff(new CatalogDiff().transforms(List.of(
                new StreamTransform().transformType(TransformTypeEnum.ADD_STREAM)
                    .streamDescriptor(new io.airbyte.api.model.generated.StreamDescriptor().name("users-data1"))
                    .updateStream(null))));

    expectedWithNewSchemaBroken = expectedWebBackendConnectionReadObject(brokenConnectionRead, sourceRead, destinationRead, brokenOperationReadList,
        SchemaChange.BREAKING, now, connectionRead.getSyncCatalog(), brokenConnectionRead.getSourceCatalogId());
    when(schedulerHandler.resetConnection(any(ConnectionIdRequestBody.class)))
        .thenReturn(new JobInfoRead().job(new JobRead().status(JobStatus.SUCCEEDED)));
  }

  WebBackendConnectionRead expectedWebBackendConnectionReadObject(
                                                                  final ConnectionRead connectionRead,
                                                                  final SourceRead sourceRead,
                                                                  final DestinationRead destinationRead,
                                                                  final OperationReadList operationReadList,
                                                                  final SchemaChange schemaChange,
                                                                  final Instant now,
                                                                  final AirbyteCatalog syncCatalog,
                                                                  final UUID catalogId) {
    return new WebBackendConnectionRead()
        .connectionId(connectionRead.getConnectionId())
        .sourceId(connectionRead.getSourceId())
        .destinationId(connectionRead.getDestinationId())
        .operationIds(connectionRead.getOperationIds())
        .name(connectionRead.getName())
        .namespaceDefinition(connectionRead.getNamespaceDefinition())
        .namespaceFormat(connectionRead.getNamespaceFormat())
        .prefix(connectionRead.getPrefix())
        .syncCatalog(syncCatalog)
        .catalogId(catalogId)
        .status(connectionRead.getStatus())
        .schedule(connectionRead.getSchedule())
        .scheduleType(connectionRead.getScheduleType())
        .scheduleData(connectionRead.getScheduleData())
        .source(sourceRead)
        .destination(destinationRead)
        .operations(operationReadList.getOperations())
        .latestSyncJobCreatedAt(now.getEpochSecond())
        .latestSyncJobStatus(JobStatus.SUCCEEDED)
        .isSyncing(false)
        .schemaChange(schemaChange)
        .resourceRequirements(new ResourceRequirements()
            .cpuRequest(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getCpuRequest())
            .cpuLimit(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getCpuLimit())
            .memoryRequest(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getMemoryRequest())
            .memoryLimit(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getMemoryLimit()));
  }

  @Test
  void testGetWorkspaceState() throws IOException {
    final UUID uuid = UUID.randomUUID();
    final WebBackendWorkspaceState request = new WebBackendWorkspaceState().workspaceId(uuid);
    when(configRepository.countSourcesForWorkspace(uuid)).thenReturn(5);
    when(configRepository.countDestinationsForWorkspace(uuid)).thenReturn(2);
    when(configRepository.countConnectionsForWorkspace(uuid)).thenReturn(8);
    final var actual = wbHandler.getWorkspaceState(request);
    assertTrue(actual.getHasConnections());
    assertTrue(actual.getHasDestinations());
    assertTrue((actual.getHasSources()));
  }

  @Test
  void testGetWorkspaceStateEmpty() throws IOException {
    final UUID uuid = UUID.randomUUID();
    final WebBackendWorkspaceState request = new WebBackendWorkspaceState().workspaceId(uuid);
    when(configRepository.countSourcesForWorkspace(uuid)).thenReturn(0);
    when(configRepository.countDestinationsForWorkspace(uuid)).thenReturn(0);
    when(configRepository.countConnectionsForWorkspace(uuid)).thenReturn(0);
    final var actual = wbHandler.getWorkspaceState(request);
    assertFalse(actual.getHasConnections());
    assertFalse(actual.getHasDestinations());
    assertFalse(actual.getHasSources());
  }

  @Test
  void testWebBackendListConnectionsForWorkspace() throws IOException, JsonValidationException, ConfigNotFoundException {
    final WebBackendConnectionListRequestBody webBackendConnectionListRequestBody = new WebBackendConnectionListRequestBody();
    webBackendConnectionListRequestBody.setWorkspaceId(sourceRead.getWorkspaceId());

    final WebBackendConnectionReadList WebBackendConnectionReadList =
        wbHandler.webBackendListConnectionsForWorkspace(webBackendConnectionListRequestBody);

    assertEquals(1, WebBackendConnectionReadList.getConnections().size());
    assertEquals(expectedListItem, WebBackendConnectionReadList.getConnections().get(0));

    // make sure the icons were loaded into actual svg content
    assertTrue(expectedListItem.getSource().getIcon().startsWith(SVG));
    assertTrue(expectedListItem.getDestination().getIcon().startsWith(SVG));
  }

  @Test
  void testWebBackendGetConnection() throws ConfigNotFoundException, IOException, JsonValidationException {
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody();
    connectionIdRequestBody.setConnectionId(connectionRead.getConnectionId());

    final WebBackendConnectionRequestBody webBackendConnectionRequestBody = new WebBackendConnectionRequestBody();
    webBackendConnectionRequestBody.setConnectionId(connectionRead.getConnectionId());

    when(connectionsHandler.getConnection(connectionRead.getConnectionId())).thenReturn(connectionRead);
    when(operationsHandler.listOperationsForConnection(connectionIdRequestBody)).thenReturn(operationReadList);

    final WebBackendConnectionRead webBackendConnectionRead = wbHandler.webBackendGetConnection(webBackendConnectionRequestBody);

    assertEquals(expected, webBackendConnectionRead);

    // make sure the icons were loaded into actual svg content
    assertTrue(expected.getSource().getIcon().startsWith(SVG));
    assertTrue(expected.getDestination().getIcon().startsWith(SVG));
  }

  WebBackendConnectionRead testWebBackendGetConnection(final boolean withCatalogRefresh,
                                                       final ConnectionRead connectionRead,
                                                       final OperationReadList operationReadList)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody();
    connectionIdRequestBody.setConnectionId(connectionRead.getConnectionId());

    final WebBackendConnectionRequestBody webBackendConnectionIdRequestBody = new WebBackendConnectionRequestBody();
    webBackendConnectionIdRequestBody.setConnectionId(connectionRead.getConnectionId());
    if (withCatalogRefresh) {
      webBackendConnectionIdRequestBody.setWithRefreshedCatalog(true);
    }

    when(connectionsHandler.getConnection(connectionRead.getConnectionId())).thenReturn(connectionRead);
    when(operationsHandler.listOperationsForConnection(connectionIdRequestBody)).thenReturn(operationReadList);

    return wbHandler.webBackendGetConnection(webBackendConnectionIdRequestBody);
  }

  @Test
  void testWebBackendGetConnectionWithDiscoveryAndNewSchema() throws ConfigNotFoundException,
      IOException, JsonValidationException {
    final UUID newCatalogId = UUID.randomUUID();
    when(configRepository.getMostRecentActorCatalogFetchEventForSource(any()))
        .thenReturn(Optional.of(new ActorCatalogFetchEvent().withActorCatalogId(newCatalogId)));
    when(configRepository.getActorCatalogById(any())).thenReturn(new ActorCatalog().withId(UUID.randomUUID()));
    final SourceDiscoverSchemaRead schemaRead =
        new SourceDiscoverSchemaRead().catalogDiff(expectedWithNewSchema.getCatalogDiff()).catalog(expectedWithNewSchema.getSyncCatalog())
            .breakingChange(false).connectionStatus(ConnectionStatus.ACTIVE);
    when(schedulerHandler.discoverSchemaForSourceFromSourceId(any())).thenReturn(schemaRead);
    when(connectionsHandler.getConnectionAirbyteCatalog(connectionRead.getConnectionId())).thenReturn(Optional.of(connectionRead.getSyncCatalog()));

    final WebBackendConnectionRead result = testWebBackendGetConnection(true, connectionRead,
        operationReadList);
    assertEquals(expectedWithNewSchema, result);
  }

  @Test
  void testWebBackendGetConnectionWithDiscoveryAndNewSchemaBreakingChange() throws ConfigNotFoundException,
      IOException, JsonValidationException {
    final UUID newCatalogId = UUID.randomUUID();
    when(configRepository.getMostRecentActorCatalogFetchEventForSource(any()))
        .thenReturn(Optional.of(new ActorCatalogFetchEvent().withActorCatalogId(newCatalogId)));
    when(configRepository.getActorCatalogById(any())).thenReturn(new ActorCatalog().withId(UUID.randomUUID()));
    final SourceDiscoverSchemaRead schemaRead =
        new SourceDiscoverSchemaRead().catalogDiff(expectedWithNewSchema.getCatalogDiff()).catalog(expectedWithNewSchema.getSyncCatalog())
            .breakingChange(true).connectionStatus(ConnectionStatus.INACTIVE);
    when(schedulerHandler.discoverSchemaForSourceFromSourceId(any())).thenReturn(schemaRead);
    when(connectionsHandler.getConnectionAirbyteCatalog(brokenConnectionRead.getConnectionId()))
        .thenReturn(Optional.of(connectionRead.getSyncCatalog()));

    final WebBackendConnectionRead result = testWebBackendGetConnection(true, brokenConnectionRead,
        operationReadList);
    assertEquals(expectedWithNewSchemaAndBreakingChange, result);
  }

  @Test
  void testWebBackendGetConnectionWithDiscoveryMissingCatalogUsedToMakeConfiguredCatalog()
      throws IOException, ConfigNotFoundException, JsonValidationException {
    final UUID newCatalogId = UUID.randomUUID();
    when(configRepository.getMostRecentActorCatalogFetchEventForSource(any()))
        .thenReturn(Optional.of(new ActorCatalogFetchEvent().withActorCatalogId(newCatalogId)));
    when(configRepository.getActorCatalogById(any())).thenReturn(new ActorCatalog().withId(UUID.randomUUID()));
    final SourceDiscoverSchemaRead schemaRead =
        new SourceDiscoverSchemaRead().catalogDiff(expectedWithNewSchema.getCatalogDiff()).catalog(expectedWithNewSchema.getSyncCatalog())
            .breakingChange(false).connectionStatus(ConnectionStatus.ACTIVE);
    when(schedulerHandler.discoverSchemaForSourceFromSourceId(any())).thenReturn(schemaRead);
    when(connectionsHandler.getConnectionAirbyteCatalog(connectionRead.getConnectionId())).thenReturn(Optional.empty());

    final WebBackendConnectionRead result = testWebBackendGetConnection(true, connectionRead,
        operationReadList);
    assertEquals(expectedWithNewSchema, result);
  }

  @Test
  void testWebBackendGetConnectionWithDiscoveryAndFieldSelectionAddField() throws ConfigNotFoundException,
      IOException, JsonValidationException {
    // Mock this because the API uses it to determine whether there was a schema change.
    when(configRepository.getMostRecentActorCatalogFetchEventForSource(any()))
        .thenReturn(Optional.of(new ActorCatalogFetchEvent().withActorCatalogId(UUID.randomUUID())));

    // Original configured catalog has two fields, and only one of them is selected.
    final AirbyteCatalog originalConfiguredCatalog = ConnectionHelpers.generateApiCatalogWithTwoFields();
    originalConfiguredCatalog.getStreams().get(0).getConfig().fieldSelectionEnabled(true)
        .selectedFields(List.of(new SelectedFieldInfo().addFieldPathItem(
            ConnectionHelpers.FIELD_NAME)));
    connectionRead.syncCatalog(originalConfiguredCatalog);

    // Original discovered catalog has the same two fields but no selection info because it's a
    // discovered catalog.
    when(connectionsHandler.getConnectionAirbyteCatalog(connectionRead.getConnectionId())).thenReturn(
        Optional.of(ConnectionHelpers.generateApiCatalogWithTwoFields()));

    // Newly-discovered catalog has an extra field. There is no field selection info because it's a
    // discovered catalog.
    final AirbyteCatalog newCatalogToDiscover = ConnectionHelpers.generateApiCatalogWithTwoFields();
    final JsonNode newFieldSchema = Jsons.deserialize("{\"type\": \"string\"}");
    ((ObjectNode) newCatalogToDiscover.getStreams().get(0).getStream().getJsonSchema().findPath("properties"))
        .putObject("a-new-field")
        .put("type", "string");
    final SourceDiscoverSchemaRead schemaRead =
        new SourceDiscoverSchemaRead()
            .catalogDiff(
                new CatalogDiff().addTransformsItem(new StreamTransform().addUpdateStreamItem(new FieldTransform().transformType(
                    FieldTransform.TransformTypeEnum.ADD_FIELD).addFieldNameItem("a-new-field").breaking(false)
                    .addField(new FieldAdd().schema(newFieldSchema)))))
            .catalog(newCatalogToDiscover)
            .breakingChange(false)
            .connectionStatus(ConnectionStatus.ACTIVE);
    when(schedulerHandler.discoverSchemaForSourceFromSourceId(any())).thenReturn(schemaRead);

    final WebBackendConnectionRead result = testWebBackendGetConnection(true, connectionRead,
        operationReadList);

    // We expect the discovered catalog with two fields selected: the one that was originally selected,
    // plus the newly-discovered field.
    final AirbyteCatalog expectedNewCatalog = Jsons.clone(newCatalogToDiscover);
    expectedNewCatalog.getStreams().get(0).getConfig().fieldSelectionEnabled(true).selectedFields(
        List.of(new SelectedFieldInfo().addFieldPathItem(ConnectionHelpers.FIELD_NAME), new SelectedFieldInfo().addFieldPathItem("a-new-field")));
    expectedWithNewSchema.catalogDiff(schemaRead.getCatalogDiff()).syncCatalog(expectedNewCatalog);
    assertEquals(expectedWithNewSchema, result);
  }

  @Test
  void testWebBackendGetConnectionWithDiscoveryAndFieldSelectionRemoveField() throws ConfigNotFoundException,
      IOException, JsonValidationException {
    // Mock this because the API uses it to determine whether there was a schema change.
    when(configRepository.getMostRecentActorCatalogFetchEventForSource(any()))
        .thenReturn(Optional.of(new ActorCatalogFetchEvent().withActorCatalogId(UUID.randomUUID())));

    // Original configured catalog has two fields, and both of them are selected.
    final AirbyteCatalog originalConfiguredCatalog = ConnectionHelpers.generateApiCatalogWithTwoFields();
    originalConfiguredCatalog.getStreams().get(0).getConfig().fieldSelectionEnabled(true)
        .selectedFields(List.of(new SelectedFieldInfo().addFieldPathItem(
            ConnectionHelpers.FIELD_NAME), new SelectedFieldInfo().addFieldPathItem(ConnectionHelpers.FIELD_NAME + "2")));
    connectionRead.syncCatalog(originalConfiguredCatalog);

    // Original discovered catalog has the same two fields but no selection info because it's a
    // discovered catalog.
    when(connectionsHandler.getConnectionAirbyteCatalog(connectionRead.getConnectionId())).thenReturn(
        Optional.of(ConnectionHelpers.generateApiCatalogWithTwoFields()));

    // Newly-discovered catalog has one of the fields removed. There is no field selection info because
    // it's a
    // discovered catalog.
    final AirbyteCatalog newCatalogToDiscover = ConnectionHelpers.generateBasicApiCatalog();
    final JsonNode removedFieldSchema = Jsons.deserialize("{\"type\": \"string\"}");
    final SourceDiscoverSchemaRead schemaRead =
        new SourceDiscoverSchemaRead()
            .catalogDiff(new CatalogDiff().addTransformsItem(new StreamTransform().addUpdateStreamItem(
                new FieldTransform().transformType(FieldTransform.TransformTypeEnum.REMOVE_FIELD).addFieldNameItem(ConnectionHelpers.FIELD_NAME + "2")
                    .breaking(false).removeField(new FieldRemove().schema(removedFieldSchema)))))
            .catalog(newCatalogToDiscover)
            .breakingChange(false)
            .connectionStatus(ConnectionStatus.ACTIVE);
    when(schedulerHandler.discoverSchemaForSourceFromSourceId(any())).thenReturn(schemaRead);

    final WebBackendConnectionRead result = testWebBackendGetConnection(true, connectionRead,
        operationReadList);

    // We expect the discovered catalog with two fields selected: the one that was originally selected,
    // plus the newly-discovered field.
    final AirbyteCatalog expectedNewCatalog = Jsons.clone(newCatalogToDiscover);
    expectedNewCatalog.getStreams().get(0).getConfig().fieldSelectionEnabled(true).selectedFields(
        List.of(new SelectedFieldInfo().addFieldPathItem(ConnectionHelpers.FIELD_NAME)));
    expectedWithNewSchema.catalogDiff(schemaRead.getCatalogDiff()).syncCatalog(expectedNewCatalog);
    assertEquals(expectedWithNewSchema, result);
  }

  @Test
  void testWebBackendGetConnectionNoRefreshCatalog()
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final WebBackendConnectionRead result = testWebBackendGetConnection(false, connectionRead, operationReadList);
    verify(schedulerHandler, never()).discoverSchemaForSourceFromSourceId(any());
    assertEquals(expected, result);
  }

  @Test
  void testWebBackendGetConnectionNoDiscoveryWithNewSchema() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.getMostRecentActorCatalogFetchEventForSource(any()))
        .thenReturn(Optional.of(new ActorCatalogFetchEvent().withActorCatalogId(UUID.randomUUID())));
    when(configRepository.getActorCatalogById(any())).thenReturn(new ActorCatalog().withId(UUID.randomUUID()));
    final WebBackendConnectionRead result = testWebBackendGetConnection(false, connectionRead, operationReadList);
    assertEquals(expectedNoDiscoveryWithNewSchema, result);
  }

  @Test
  void testWebBackendGetConnectionNoDiscoveryWithNewSchemaBreaking() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(connectionsHandler.getConnection(brokenConnectionRead.getConnectionId())).thenReturn(brokenConnectionRead);
    when(configRepository.getMostRecentActorCatalogFetchEventForSource(any()))
        .thenReturn(Optional.of(new ActorCatalogFetchEvent().withActorCatalogId(UUID.randomUUID())));
    when(configRepository.getActorCatalogById(any())).thenReturn(new ActorCatalog().withId(UUID.randomUUID()));
    final WebBackendConnectionRead result = testWebBackendGetConnection(false, brokenConnectionRead, brokenOperationReadList);
    assertEquals(expectedWithNewSchemaBroken, result);
  }

  @Test
  void testToConnectionCreate() throws IOException {
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    final StandardSync standardSync = ConnectionHelpers.generateSyncWithSourceId(source.getSourceId());

    final AirbyteCatalog catalog = ConnectionHelpers.generateBasicApiCatalog();
    catalog.getStreams().get(0).getStream().setName("azkaban_users");

    final ConnectionSchedule schedule = new ConnectionSchedule().units(1L).timeUnit(TimeUnitEnum.MINUTES);

    final UUID newSourceId = UUID.randomUUID();
    final UUID newDestinationId = UUID.randomUUID();
    final UUID newOperationId = UUID.randomUUID();
    final UUID sourceCatalogId = UUID.randomUUID();
    final WebBackendConnectionCreate input = new WebBackendConnectionCreate()
        .name("testConnectionCreate")
        .namespaceDefinition(Enums.convertTo(standardSync.getNamespaceDefinition(), NamespaceDefinitionType.class))
        .namespaceFormat(standardSync.getNamespaceFormat())
        .prefix(standardSync.getPrefix())
        .sourceId(newSourceId)
        .destinationId(newDestinationId)
        .operationIds(List.of(newOperationId))
        .status(ConnectionStatus.INACTIVE)
        .schedule(schedule)
        .syncCatalog(catalog)
        .sourceCatalogId(sourceCatalogId)
        .geography(Geography.US)
        .nonBreakingChangesPreference(NonBreakingChangesPreference.DISABLE);

    final List<UUID> operationIds = List.of(newOperationId);

    final ConnectionCreate expected = new ConnectionCreate()
        .name("testConnectionCreate")
        .namespaceDefinition(Enums.convertTo(standardSync.getNamespaceDefinition(), NamespaceDefinitionType.class))
        .namespaceFormat(standardSync.getNamespaceFormat())
        .prefix(standardSync.getPrefix())
        .sourceId(newSourceId)
        .destinationId(newDestinationId)
        .operationIds(operationIds)
        .status(ConnectionStatus.INACTIVE)
        .schedule(schedule)
        .syncCatalog(catalog)
        .sourceCatalogId(sourceCatalogId)
        .geography(Geography.US)
        .nonBreakingChangesPreference(NonBreakingChangesPreference.DISABLE);

    final ConnectionCreate actual = WebBackendConnectionsHandler.toConnectionCreate(input, operationIds);

    assertEquals(expected, actual);
  }

  @Test
  void testToConnectionPatch() throws IOException {
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    final StandardSync standardSync = ConnectionHelpers.generateSyncWithSourceId(source.getSourceId());

    final AirbyteCatalog catalog = ConnectionHelpers.generateBasicApiCatalog();
    catalog.getStreams().get(0).getStream().setName("azkaban_users");

    final ConnectionSchedule schedule = new ConnectionSchedule().units(1L).timeUnit(TimeUnitEnum.MINUTES);

    final UUID newOperationId = UUID.randomUUID();
    final WebBackendConnectionUpdate input = new WebBackendConnectionUpdate()
        .namespaceDefinition(Enums.convertTo(standardSync.getNamespaceDefinition(), NamespaceDefinitionType.class))
        .namespaceFormat(standardSync.getNamespaceFormat())
        .prefix(standardSync.getPrefix())
        .connectionId(standardSync.getConnectionId())
        .operations(List.of(new WebBackendOperationCreateOrUpdate().operationId(newOperationId)))
        .status(ConnectionStatus.INACTIVE)
        .schedule(schedule)
        .name(standardSync.getName())
        .syncCatalog(catalog)
        .geography(Geography.US)
        .nonBreakingChangesPreference(NonBreakingChangesPreference.DISABLE)
        .notifySchemaChanges(false);

    final List<UUID> operationIds = List.of(newOperationId);

    final ConnectionUpdate expected = new ConnectionUpdate()
        .namespaceDefinition(Enums.convertTo(standardSync.getNamespaceDefinition(), NamespaceDefinitionType.class))
        .namespaceFormat(standardSync.getNamespaceFormat())
        .prefix(standardSync.getPrefix())
        .connectionId(standardSync.getConnectionId())
        .operationIds(operationIds)
        .status(ConnectionStatus.INACTIVE)
        .schedule(schedule)
        .name(standardSync.getName())
        .syncCatalog(catalog)
        .geography(Geography.US)
        .nonBreakingChangesPreference(NonBreakingChangesPreference.DISABLE)
        .notifySchemaChanges(false)
        .breakingChange(false);

    final ConnectionUpdate actual = WebBackendConnectionsHandler.toConnectionPatch(input, operationIds, false);

    assertEquals(expected, actual);
  }

  @Test
  void testForConnectionCreateCompleteness() {
    final Set<String> handledMethods =
        Set.of("name", "namespaceDefinition", "namespaceFormat", "prefix", "sourceId", "destinationId", "operationIds",
            "addOperationIdsItem", "removeOperationIdsItem", "syncCatalog", "schedule", "scheduleType", "scheduleData",
            "status", "resourceRequirements", "sourceCatalogId", "geography", "nonBreakingChangesPreference", "notifySchemaChanges");

    final Set<String> methods = Arrays.stream(ConnectionCreate.class.getMethods())
        .filter(method -> method.getReturnType() == ConnectionCreate.class)
        .map(Method::getName)
        .collect(Collectors.toSet());

    final String message =
        """
        If this test is failing, it means you added a field to ConnectionCreate!
        Congratulations, but you're not done yet..
        \tYou should update WebBackendConnectionsHandler::toConnectionCreate
        \tand ensure that the field is tested in WebBackendConnectionsHandlerTest::testToConnectionCreate
        Then you can add the field name here to make this test pass. Cheers!""";
    assertEquals(handledMethods, methods, message);
  }

  @Test
  void testForConnectionPatchCompleteness() {
    final Set<String> handledMethods =
        Set.of("schedule", "connectionId", "syncCatalog", "namespaceDefinition", "namespaceFormat", "prefix", "status",
            "operationIds", "addOperationIdsItem", "removeOperationIdsItem", "resourceRequirements", "name",
            "sourceCatalogId", "scheduleType", "scheduleData", "geography", "breakingChange", "notifySchemaChanges", "nonBreakingChangesPreference");

    final Set<String> methods = Arrays.stream(ConnectionUpdate.class.getMethods())
        .filter(method -> method.getReturnType() == ConnectionUpdate.class)
        .map(Method::getName)
        .collect(Collectors.toSet());

    final String message =
        """
        If this test is failing, it means you added a field to ConnectionUpdate!
        Congratulations, but you're not done yet..
        \tYou should update WebBackendConnectionsHandler::toConnectionPatch
        \tand ensure that the field is tested in WebBackendConnectionsHandlerTest::testToConnectionPatch
        Then you can add the field name here to make this test pass. Cheers!""";
    assertEquals(handledMethods, methods, message);
  }

  @Test
  void testUpdateConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    final WebBackendConnectionUpdate updateBody = new WebBackendConnectionUpdate()
        .namespaceDefinition(expected.getNamespaceDefinition())
        .namespaceFormat(expected.getNamespaceFormat())
        .prefix(expected.getPrefix())
        .connectionId(expected.getConnectionId())
        .schedule(expected.getSchedule())
        .status(expected.getStatus())
        .syncCatalog(expected.getSyncCatalog())
        .sourceCatalogId(expected.getCatalogId());

    when(configRepository.getConfiguredCatalogForConnection(expected.getConnectionId()))
        .thenReturn(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog());

    final CatalogDiff catalogDiff = new CatalogDiff().transforms(List.of());
    when(connectionsHandler.getDiff(any(), any(), any())).thenReturn(catalogDiff);
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody().connectionId(expected.getConnectionId());
    when(stateHandler.getState(connectionIdRequestBody)).thenReturn(new ConnectionState().stateType(ConnectionStateType.LEGACY));

    when(connectionsHandler.getConnection(expected.getConnectionId())).thenReturn(
        new ConnectionRead().connectionId(expected.getConnectionId()));
    when(connectionsHandler.updateConnection(any())).thenReturn(
        new ConnectionRead()
            .connectionId(expected.getConnectionId())
            .sourceId(expected.getSourceId())
            .destinationId(expected.getDestinationId())
            .name(expected.getName())
            .namespaceDefinition(expected.getNamespaceDefinition())
            .namespaceFormat(expected.getNamespaceFormat())
            .prefix(expected.getPrefix())
            .syncCatalog(expected.getSyncCatalog())
            .status(expected.getStatus())
            .schedule(expected.getSchedule()).breakingChange(false));
    when(operationsHandler.listOperationsForConnection(any())).thenReturn(operationReadList);
    final ConnectionIdRequestBody connectionId = new ConnectionIdRequestBody().connectionId(connectionRead.getConnectionId());

    final AirbyteCatalog fullAirbyteCatalog = ConnectionHelpers.generateMultipleStreamsApiCatalog(2);
    when(connectionsHandler.getConnectionAirbyteCatalog(connectionRead.getConnectionId())).thenReturn(Optional.ofNullable(fullAirbyteCatalog));

    final AirbyteCatalog expectedCatalogReturned =
        WebBackendConnectionsHandler.updateSchemaWithRefreshedDiscoveredCatalog(expected.getSyncCatalog(), expected.getSyncCatalog(),
            fullAirbyteCatalog);
    final WebBackendConnectionRead connectionRead = wbHandler.webBackendUpdateConnection(updateBody);

    assertEquals(expectedCatalogReturned, connectionRead.getSyncCatalog());

    verify(schedulerHandler, times(0)).resetConnection(connectionId);
    verify(schedulerHandler, times(0)).syncConnection(connectionId);
  }

  @Test
  void testUpdateConnectionWithOperations() throws JsonValidationException, ConfigNotFoundException, IOException {
    final WebBackendOperationCreateOrUpdate operationCreateOrUpdate = new WebBackendOperationCreateOrUpdate()
        .name("Test Operation")
        .operationId(connectionRead.getOperationIds().get(0));
    final OperationUpdate operationUpdate = WebBackendConnectionsHandler.toOperationUpdate(operationCreateOrUpdate);
    final WebBackendConnectionUpdate updateBody = new WebBackendConnectionUpdate()
        .namespaceDefinition(expected.getNamespaceDefinition())
        .namespaceFormat(expected.getNamespaceFormat())
        .prefix(expected.getPrefix())
        .connectionId(expected.getConnectionId())
        .schedule(expected.getSchedule())
        .status(expected.getStatus())
        .syncCatalog(expected.getSyncCatalog())
        .operations(List.of(operationCreateOrUpdate));

    when(configRepository.getConfiguredCatalogForConnection(expected.getConnectionId()))
        .thenReturn(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog());

    final CatalogDiff catalogDiff = new CatalogDiff().transforms(List.of());
    when(connectionsHandler.getDiff(any(), any(), any())).thenReturn(catalogDiff);
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody().connectionId(expected.getConnectionId());
    when(stateHandler.getState(connectionIdRequestBody)).thenReturn(new ConnectionState().stateType(ConnectionStateType.LEGACY));

    when(connectionsHandler.getConnection(expected.getConnectionId())).thenReturn(
        new ConnectionRead()
            .connectionId(expected.getConnectionId())
            .operationIds(connectionRead.getOperationIds())
            .breakingChange(false));
    when(connectionsHandler.updateConnection(any())).thenReturn(
        new ConnectionRead()
            .connectionId(expected.getConnectionId())
            .sourceId(expected.getSourceId())
            .destinationId(expected.getDestinationId())
            .operationIds(connectionRead.getOperationIds())
            .name(expected.getName())
            .namespaceDefinition(expected.getNamespaceDefinition())
            .namespaceFormat(expected.getNamespaceFormat())
            .prefix(expected.getPrefix())
            .syncCatalog(expected.getSyncCatalog())
            .status(expected.getStatus())
            .schedule(expected.getSchedule()).breakingChange(false));
    when(operationsHandler.updateOperation(operationUpdate)).thenReturn(new OperationRead().operationId(operationUpdate.getOperationId()));
    when(operationsHandler.listOperationsForConnection(any())).thenReturn(operationReadList);

    final WebBackendConnectionRead actualConnectionRead = wbHandler.webBackendUpdateConnection(updateBody);

    assertEquals(connectionRead.getOperationIds(), actualConnectionRead.getOperationIds());
    verify(operationsHandler, times(1)).updateOperation(operationUpdate);
  }

  @Test
  void testUpdateConnectionWithUpdatedSchemaLegacy() throws JsonValidationException, ConfigNotFoundException, IOException {
    final WebBackendConnectionUpdate updateBody = new WebBackendConnectionUpdate()
        .namespaceDefinition(expected.getNamespaceDefinition())
        .namespaceFormat(expected.getNamespaceFormat())
        .prefix(expected.getPrefix())
        .connectionId(expected.getConnectionId())
        .schedule(expected.getSchedule())
        .status(expected.getStatus())
        .syncCatalog(expectedWithNewSchema.getSyncCatalog());

    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody().connectionId(expected.getConnectionId());

    when(stateHandler.getState(connectionIdRequestBody)).thenReturn(new ConnectionState().stateType(ConnectionStateType.LEGACY));
    when(configRepository.getConfiguredCatalogForConnection(expected.getConnectionId()))
        .thenReturn(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog());

    final StreamDescriptor streamDescriptorAdd = new StreamDescriptor().name("addStream");
    final StreamTransform streamTransformAdd =
        new StreamTransform().streamDescriptor(streamDescriptorAdd).transformType(TransformTypeEnum.ADD_STREAM);

    final CatalogDiff catalogDiff = new CatalogDiff().transforms(List.of(streamTransformAdd));
    when(connectionsHandler.getDiff(any(), any(), any())).thenReturn(catalogDiff);

    when(operationsHandler.listOperationsForConnection(any())).thenReturn(operationReadList);
    when(connectionsHandler.getConnection(expected.getConnectionId())).thenReturn(
        new ConnectionRead().connectionId(expected.getConnectionId()));
    final ConnectionRead connectionRead = new ConnectionRead()
        .connectionId(expected.getConnectionId())
        .sourceId(expected.getSourceId())
        .destinationId(expected.getDestinationId())
        .name(expected.getName())
        .namespaceDefinition(expected.getNamespaceDefinition())
        .namespaceFormat(expected.getNamespaceFormat())
        .prefix(expected.getPrefix())
        .syncCatalog(expectedWithNewSchema.getSyncCatalog())
        .status(expected.getStatus())
        .schedule(expected.getSchedule()).breakingChange(false);
    when(connectionsHandler.updateConnection(any())).thenReturn(connectionRead);
    when(connectionsHandler.getConnection(expected.getConnectionId())).thenReturn(connectionRead);

    final List<io.airbyte.protocol.models.StreamDescriptor> connectionStreams = List.of(ConnectionHelpers.STREAM_DESCRIPTOR);
    when(configRepository.getAllStreamsForConnection(expected.getConnectionId())).thenReturn(connectionStreams);

    final ManualOperationResult successfulResult = ManualOperationResult.builder().jobId(Optional.empty()).failingReason(Optional.empty()).build();
    when(eventRunner.resetConnection(any(), any(), anyBoolean())).thenReturn(successfulResult);
    when(eventRunner.startNewManualSync(any())).thenReturn(successfulResult);

    final WebBackendConnectionRead result = wbHandler.webBackendUpdateConnection(updateBody);

    assertEquals(expectedWithNewSchema.getSyncCatalog(), result.getSyncCatalog());

    final ConnectionIdRequestBody connectionId = new ConnectionIdRequestBody().connectionId(result.getConnectionId());
    verify(schedulerHandler, times(0)).resetConnection(connectionId);
    verify(schedulerHandler, times(0)).syncConnection(connectionId);
    verify(connectionsHandler, times(1)).updateConnection(any());
    final InOrder orderVerifier = inOrder(eventRunner);
    orderVerifier.verify(eventRunner, times(1)).resetConnection(connectionId.getConnectionId(), connectionStreams, true);
  }

  @Test
  void testUpdateConnectionWithUpdatedSchemaPerStream() throws JsonValidationException, ConfigNotFoundException, IOException {
    final WebBackendConnectionUpdate updateBody = new WebBackendConnectionUpdate()
        .namespaceDefinition(expected.getNamespaceDefinition())
        .namespaceFormat(expected.getNamespaceFormat())
        .prefix(expected.getPrefix())
        .connectionId(expected.getConnectionId())
        .schedule(expected.getSchedule())
        .status(expected.getStatus())
        .syncCatalog(expectedWithNewSchema.getSyncCatalog());

    // state is per-stream
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody().connectionId(expected.getConnectionId());
    when(stateHandler.getState(connectionIdRequestBody)).thenReturn(new ConnectionState().stateType(ConnectionStateType.STREAM));
    when(configRepository.getConfiguredCatalogForConnection(expected.getConnectionId()))
        .thenReturn(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog());

    final StreamDescriptor streamDescriptorAdd = new StreamDescriptor().name("addStream");
    final StreamDescriptor streamDescriptorRemove = new StreamDescriptor().name("removeStream");
    final StreamDescriptor streamDescriptorUpdate = new StreamDescriptor().name("updateStream");

    final StreamTransform streamTransformAdd =
        new StreamTransform().streamDescriptor(streamDescriptorAdd).transformType(TransformTypeEnum.ADD_STREAM);
    final StreamTransform streamTransformRemove =
        new StreamTransform().streamDescriptor(streamDescriptorRemove).transformType(TransformTypeEnum.REMOVE_STREAM);
    final StreamTransform streamTransformUpdate =
        new StreamTransform().streamDescriptor(streamDescriptorUpdate).transformType(TransformTypeEnum.UPDATE_STREAM);

    final CatalogDiff catalogDiff = new CatalogDiff().transforms(List.of(streamTransformAdd, streamTransformRemove, streamTransformUpdate));
    when(connectionsHandler.getDiff(any(), any(), any())).thenReturn(catalogDiff);
    when(connectionsHandler.getConfigurationDiff(any(), any())).thenReturn(Set.of(new StreamDescriptor().name("configUpdateStream")));

    when(operationsHandler.listOperationsForConnection(any())).thenReturn(operationReadList);
    when(connectionsHandler.getConnection(expected.getConnectionId())).thenReturn(
        new ConnectionRead().connectionId(expected.getConnectionId()).breakingChange(false));
    final ConnectionRead connectionRead = new ConnectionRead()
        .connectionId(expected.getConnectionId())
        .sourceId(expected.getSourceId())
        .destinationId(expected.getDestinationId())
        .name(expected.getName())
        .namespaceDefinition(expected.getNamespaceDefinition())
        .namespaceFormat(expected.getNamespaceFormat())
        .prefix(expected.getPrefix())
        .syncCatalog(expectedWithNewSchema.getSyncCatalog())
        .status(expected.getStatus())
        .schedule(expected.getSchedule())
        .breakingChange(false);
    when(connectionsHandler.updateConnection(any())).thenReturn(connectionRead);
    when(connectionsHandler.getConnection(expected.getConnectionId())).thenReturn(connectionRead);

    final ManualOperationResult successfulResult = ManualOperationResult.builder().jobId(Optional.empty()).failingReason(Optional.empty()).build();
    when(eventRunner.resetConnection(any(), any(), anyBoolean())).thenReturn(successfulResult);
    when(eventRunner.startNewManualSync(any())).thenReturn(successfulResult);

    final WebBackendConnectionRead result = wbHandler.webBackendUpdateConnection(updateBody);

    assertEquals(expectedWithNewSchema.getSyncCatalog(), result.getSyncCatalog());

    final ConnectionIdRequestBody connectionId = new ConnectionIdRequestBody().connectionId(result.getConnectionId());
    verify(schedulerHandler, times(0)).resetConnection(connectionId);
    verify(schedulerHandler, times(0)).syncConnection(connectionId);
    verify(connectionsHandler, times(1)).updateConnection(any());
    final InOrder orderVerifier = inOrder(eventRunner);
    orderVerifier.verify(eventRunner, times(1)).resetConnection(connectionId.getConnectionId(),
        List.of(new io.airbyte.protocol.models.StreamDescriptor().withName("addStream"),
            new io.airbyte.protocol.models.StreamDescriptor().withName("updateStream"),
            new io.airbyte.protocol.models.StreamDescriptor().withName("configUpdateStream"),
            new io.airbyte.protocol.models.StreamDescriptor().withName("removeStream")),
        true);
  }

  @Test
  void testUpdateConnectionNoStreamsToReset() throws JsonValidationException, ConfigNotFoundException, IOException {
    final WebBackendConnectionUpdate updateBody = new WebBackendConnectionUpdate()
        .namespaceDefinition(expected.getNamespaceDefinition())
        .namespaceFormat(expected.getNamespaceFormat())
        .prefix(expected.getPrefix())
        .connectionId(expected.getConnectionId())
        .schedule(expected.getSchedule())
        .status(expected.getStatus())
        .syncCatalog(expectedWithNewSchema.getSyncCatalog());

    // state is per-stream
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody().connectionId(expected.getConnectionId());
    final ConfiguredAirbyteCatalog configuredAirbyteCatalog = ConnectionHelpers.generateBasicConfiguredAirbyteCatalog();
    when(stateHandler.getState(connectionIdRequestBody)).thenReturn(new ConnectionState().stateType(ConnectionStateType.STREAM));
    when(configRepository.getConfiguredCatalogForConnection(expected.getConnectionId()))
        .thenReturn(configuredAirbyteCatalog);

    final CatalogDiff catalogDiff = new CatalogDiff().transforms(List.of());
    when(connectionsHandler.getDiff(any(), any(), any())).thenReturn(catalogDiff);

    when(operationsHandler.listOperationsForConnection(any())).thenReturn(operationReadList);
    when(connectionsHandler.getConnection(expected.getConnectionId())).thenReturn(
        new ConnectionRead().connectionId(expected.getConnectionId()));
    final ConnectionRead connectionRead = new ConnectionRead()
        .connectionId(expected.getConnectionId())
        .sourceId(expected.getSourceId())
        .destinationId(expected.getDestinationId())
        .name(expected.getName())
        .namespaceDefinition(expected.getNamespaceDefinition())
        .namespaceFormat(expected.getNamespaceFormat())
        .prefix(expected.getPrefix())
        .syncCatalog(expectedWithNewSchema.getSyncCatalog())
        .status(expected.getStatus())
        .schedule(expected.getSchedule()).breakingChange(false);
    when(connectionsHandler.updateConnection(any())).thenReturn(connectionRead);
    when(connectionsHandler.getConnection(expected.getConnectionId())).thenReturn(connectionRead);

    final WebBackendConnectionRead result = wbHandler.webBackendUpdateConnection(updateBody);

    assertEquals(expectedWithNewSchema.getSyncCatalog(), result.getSyncCatalog());

    final ConnectionIdRequestBody connectionId = new ConnectionIdRequestBody().connectionId(result.getConnectionId());

    verify(connectionsHandler).getDiff(expected.getSyncCatalog(), expectedWithNewSchema.getSyncCatalog(),
        CatalogConverter.toConfiguredProtocol(result.getSyncCatalog()));
    verify(connectionsHandler).getConfigurationDiff(expected.getSyncCatalog(), expectedWithNewSchema.getSyncCatalog());
    verify(schedulerHandler, times(0)).resetConnection(connectionId);
    verify(schedulerHandler, times(0)).syncConnection(connectionId);
    verify(connectionsHandler, times(1)).updateConnection(any());
    final InOrder orderVerifier = inOrder(eventRunner);
    orderVerifier.verify(eventRunner, times(0)).resetConnection(eq(connectionId.getConnectionId()), any(), anyBoolean());
    orderVerifier.verify(eventRunner, times(0)).startNewManualSync(connectionId.getConnectionId());
  }

  @Test
  void testUpdateConnectionWithSkipReset() throws JsonValidationException, ConfigNotFoundException, IOException {
    final WebBackendConnectionUpdate updateBody = new WebBackendConnectionUpdate()
        .namespaceDefinition(expected.getNamespaceDefinition())
        .namespaceFormat(expected.getNamespaceFormat())
        .prefix(expected.getPrefix())
        .connectionId(expected.getConnectionId())
        .schedule(expected.getSchedule())
        .status(expected.getStatus())
        .syncCatalog(expectedWithNewSchema.getSyncCatalog())
        .skipReset(true);

    when(configRepository.getConfiguredCatalogForConnection(expected.getConnectionId()))
        .thenReturn(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog());
    when(operationsHandler.listOperationsForConnection(any())).thenReturn(operationReadList);
    when(connectionsHandler.getConnection(expected.getConnectionId())).thenReturn(
        new ConnectionRead().connectionId(expected.getConnectionId()));
    final ConnectionRead connectionRead = new ConnectionRead()
        .connectionId(expected.getConnectionId())
        .sourceId(expected.getSourceId())
        .destinationId(expected.getDestinationId())
        .name(expected.getName())
        .namespaceDefinition(expected.getNamespaceDefinition())
        .namespaceFormat(expected.getNamespaceFormat())
        .prefix(expected.getPrefix())
        .syncCatalog(expectedWithNewSchema.getSyncCatalog())
        .status(expected.getStatus())
        .schedule(expected.getSchedule())
        .breakingChange(false);
    when(connectionsHandler.updateConnection(any())).thenReturn(connectionRead);

    final WebBackendConnectionRead result = wbHandler.webBackendUpdateConnection(updateBody);

    assertEquals(expectedWithNewSchema.getSyncCatalog(), result.getSyncCatalog());

    final ConnectionIdRequestBody connectionId = new ConnectionIdRequestBody().connectionId(result.getConnectionId());
    verify(schedulerHandler, times(0)).resetConnection(connectionId);
    verify(schedulerHandler, times(0)).syncConnection(connectionId);
    verify(connectionsHandler, times(0)).getDiff(any(), any(), any());
    verify(connectionsHandler, times(1)).updateConnection(any());
    verify(eventRunner, times(0)).resetConnection(any(), any(), eq(true));
  }

  @Test
  void testUpdateConnectionFixingBreakingSchemaChange() throws JsonValidationException, ConfigNotFoundException, IOException {
    final WebBackendConnectionUpdate updateBody = new WebBackendConnectionUpdate()
        .namespaceDefinition(expected.getNamespaceDefinition())
        .namespaceFormat(expected.getNamespaceFormat())
        .prefix(expected.getPrefix())
        .connectionId(expected.getConnectionId())
        .schedule(expected.getSchedule())
        .status(expected.getStatus())
        .syncCatalog(expectedWithNewSchema.getSyncCatalog())
        .skipReset(false)
        .connectionId(expected.getConnectionId());

    final UUID sourceId = UUID.randomUUID();

    // existing connection has a breaking change
    when(connectionsHandler.getConnection(expected.getConnectionId())).thenReturn(
        new ConnectionRead().connectionId(expected.getConnectionId()).breakingChange(true).sourceId(sourceId));

    final CatalogDiff catalogDiff = new CatalogDiff().transforms(List.of());

    when(configRepository.getMostRecentActorCatalogForSource(sourceId)).thenReturn(Optional.of(new ActorCatalog().withCatalog(Jsons.deserialize(
        "{\"streams\": [{\"name\": \"cat_names\", \"namespace\": \"public\", \"json_schema\": {\"type\": \"object\", \"properties\": {\"id\": {\"type\": \"number\", \"airbyte_type\": \"integer\"}}}}]}"))));
    when(connectionsHandler.getDiff(any(), any(), any())).thenReturn(catalogDiff, catalogDiff);

    when(configRepository.getConfiguredCatalogForConnection(expected.getConnectionId()))
        .thenReturn(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog());
    when(operationsHandler.listOperationsForConnection(any())).thenReturn(operationReadList);

    final ConnectionRead connectionRead = new ConnectionRead()
        .connectionId(expected.getConnectionId())
        .sourceId(expected.getSourceId())
        .destinationId(expected.getDestinationId())
        .name(expected.getName())
        .namespaceDefinition(expected.getNamespaceDefinition())
        .namespaceFormat(expected.getNamespaceFormat())
        .prefix(expected.getPrefix())
        .syncCatalog(expectedWithNewSchema.getSyncCatalog())
        .status(expected.getStatus())
        .schedule(expected.getSchedule())
        .breakingChange(false);

    when(connectionsHandler.updateConnection(any())).thenReturn(connectionRead);

    final WebBackendConnectionRead result = wbHandler.webBackendUpdateConnection(updateBody);

    assertEquals(expectedWithNewSchema.getSyncCatalog(), result.getSyncCatalog());

    final ConnectionIdRequestBody connectionId = new ConnectionIdRequestBody().connectionId(result.getConnectionId());
    ArgumentCaptor<ConnectionUpdate> expectedArgumentCaptor = ArgumentCaptor.forClass(ConnectionUpdate.class);
    verify(connectionsHandler, times(1)).updateConnection(expectedArgumentCaptor.capture());
    List<ConnectionUpdate> connectionUpdateValues = expectedArgumentCaptor.getAllValues();
    // Expect the ConnectionUpdate object to have breakingChange: false
    assertEquals(false, connectionUpdateValues.get(0).getBreakingChange());

    verify(schedulerHandler, times(0)).resetConnection(connectionId);
    verify(schedulerHandler, times(0)).syncConnection(connectionId);
    verify(connectionsHandler, times(2)).getDiff(any(), any(), any());
    verify(connectionsHandler, times(1)).updateConnection(any());
  }

  @Test
  void testUpdateSchemaWithDiscoveryFromEmpty() {
    final AirbyteCatalog original = new AirbyteCatalog().streams(List.of());
    final AirbyteCatalog discovered = ConnectionHelpers.generateBasicApiCatalog();
    discovered.getStreams().get(0).getStream()
        .name(STREAM1)
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of(FIELD1, JsonSchemaType.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    discovered.getStreams().get(0).getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName(STREAM1);

    final AirbyteCatalog expected = ConnectionHelpers.generateBasicApiCatalog();
    expected.getStreams().get(0).getStream()
        .name(STREAM1)
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of(FIELD1, JsonSchemaType.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    expected.getStreams().get(0).getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName(STREAM1)
        .setSelected(false);

    final AirbyteCatalog actual = WebBackendConnectionsHandler.updateSchemaWithRefreshedDiscoveredCatalog(original, original, discovered);

    assertEquals(expected, actual);
  }

  @Test
  void testUpdateSchemaWithDiscoveryResetStream() {
    final AirbyteCatalog original = ConnectionHelpers.generateBasicApiCatalog();
    original.getStreams().get(0).getStream()
        .name("random-stream")
        .defaultCursorField(List.of(FIELD1))
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(
            Field.of(FIELD1, JsonSchemaType.NUMBER),
            Field.of(FIELD2, JsonSchemaType.NUMBER),
            Field.of(FIELD5, JsonSchemaType.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    original.getStreams().get(0).getConfig()
        .syncMode(SyncMode.INCREMENTAL)
        .cursorField(List.of(FIELD1))
        .destinationSyncMode(DestinationSyncMode.APPEND)
        .primaryKey(Collections.emptyList())
        .aliasName("random_stream");

    final AirbyteCatalog discovered = ConnectionHelpers.generateBasicApiCatalog();
    discovered.getStreams().get(0).getStream()
        .name(STREAM1)
        .defaultCursorField(List.of(FIELD3))
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of(FIELD2, JsonSchemaType.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    discovered.getStreams().get(0).getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName(STREAM1);

    final AirbyteCatalog expected = ConnectionHelpers.generateBasicApiCatalog();
    expected.getStreams().get(0).getStream()
        .name(STREAM1)
        .defaultCursorField(List.of(FIELD3))
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of(FIELD2, JsonSchemaType.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    expected.getStreams().get(0).getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName(STREAM1)
        .setSelected(false);

    final AirbyteCatalog actual = WebBackendConnectionsHandler.updateSchemaWithRefreshedDiscoveredCatalog(original, original, discovered);

    assertEquals(expected, actual);
  }

  @Test
  void testUpdateSchemaWithDiscoveryMergeNewStream() {
    final AirbyteCatalog original = ConnectionHelpers.generateBasicApiCatalog();
    original.getStreams().get(0).getStream()
        .name(STREAM1)
        .defaultCursorField(List.of(FIELD1))
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(
            Field.of(FIELD1, JsonSchemaType.NUMBER),
            Field.of(FIELD2, JsonSchemaType.NUMBER),
            Field.of(FIELD5, JsonSchemaType.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    original.getStreams().get(0).getConfig()
        .syncMode(SyncMode.INCREMENTAL)
        .cursorField(List.of(FIELD1))
        .destinationSyncMode(DestinationSyncMode.APPEND)
        .primaryKey(Collections.emptyList())
        .aliasName("renamed_stream");

    final AirbyteCatalog discovered = ConnectionHelpers.generateBasicApiCatalog();
    discovered.getStreams().get(0).getStream()
        .name(STREAM1)
        .defaultCursorField(List.of(FIELD3))
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of(FIELD2, JsonSchemaType.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    discovered.getStreams().get(0).getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName(STREAM1);
    final AirbyteStreamAndConfiguration newStream = ConnectionHelpers.generateBasicApiCatalog().getStreams().get(0);
    newStream.getStream()
        .name(STREAM2)
        .defaultCursorField(List.of(FIELD5))
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of(FIELD5, JsonSchemaType.BOOLEAN)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    newStream.getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName(STREAM2);
    discovered.getStreams().add(newStream);

    final AirbyteCatalog expected = ConnectionHelpers.generateBasicApiCatalog();
    expected.getStreams().get(0).getStream()
        .name(STREAM1)
        .defaultCursorField(List.of(FIELD3))
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of(FIELD2, JsonSchemaType.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    expected.getStreams().get(0).getConfig()
        .syncMode(SyncMode.INCREMENTAL)
        .cursorField(List.of(FIELD1))
        .destinationSyncMode(DestinationSyncMode.APPEND)
        .primaryKey(Collections.emptyList())
        .aliasName("renamed_stream")
        .setSelected(true);
    final AirbyteStreamAndConfiguration expectedNewStream = ConnectionHelpers.generateBasicApiCatalog().getStreams().get(0);
    expectedNewStream.getStream()
        .name(STREAM2)
        .defaultCursorField(List.of(FIELD5))
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of(FIELD5, JsonSchemaType.BOOLEAN)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    expectedNewStream.getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName(STREAM2)
        .setSelected(false);
    expected.getStreams().add(expectedNewStream);

    final AirbyteCatalog actual = WebBackendConnectionsHandler.updateSchemaWithRefreshedDiscoveredCatalog(original, original, discovered);

    assertEquals(expected, actual);
  }

  @Test
  void testUpdateSchemaWithNamespacedStreams() {
    final AirbyteCatalog original = ConnectionHelpers.generateBasicApiCatalog();
    final AirbyteStreamAndConfiguration stream1Config = original.getStreams().get(0);
    final AirbyteStream stream1 = stream1Config.getStream();
    final AirbyteStream stream2 = new AirbyteStream()
        .name(stream1.getName())
        .namespace("second_namespace")
        .jsonSchema(stream1.getJsonSchema())
        .defaultCursorField(stream1.getDefaultCursorField())
        .supportedSyncModes(stream1.getSupportedSyncModes())
        .sourceDefinedCursor(stream1.getSourceDefinedCursor())
        .sourceDefinedPrimaryKey(stream1.getSourceDefinedPrimaryKey());
    final AirbyteStreamAndConfiguration stream2Config = new AirbyteStreamAndConfiguration()
        .config(stream1Config.getConfig())
        .stream(stream2);
    original.getStreams().add(stream2Config);

    final AirbyteCatalog discovered = ConnectionHelpers.generateBasicApiCatalog();
    discovered.getStreams().get(0).getStream()
        .name(STREAM1)
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of(FIELD1, JsonSchemaType.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    discovered.getStreams().get(0).getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName(STREAM1);

    final AirbyteCatalog expected = ConnectionHelpers.generateBasicApiCatalog();
    expected.getStreams().get(0).getStream()
        .name(STREAM1)
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of(FIELD1, JsonSchemaType.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    expected.getStreams().get(0).getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName(STREAM1)
        .setSelected(false);

    final AirbyteCatalog actual = WebBackendConnectionsHandler.updateSchemaWithRefreshedDiscoveredCatalog(original, original, discovered);

    assertEquals(expected, actual);
  }

  @Test
  void testGetStreamsToReset() {
    final StreamTransform streamTransformAdd =
        new StreamTransform().transformType(TransformTypeEnum.ADD_STREAM).streamDescriptor(new StreamDescriptor().name("added_stream"));
    final StreamTransform streamTransformRemove =
        new StreamTransform().transformType(TransformTypeEnum.REMOVE_STREAM).streamDescriptor(new StreamDescriptor().name("removed_stream"));
    final StreamTransform streamTransformUpdate =
        new StreamTransform().transformType(TransformTypeEnum.UPDATE_STREAM).streamDescriptor(new StreamDescriptor().name("updated_stream"));
    final CatalogDiff catalogDiff = new CatalogDiff().transforms(List.of(streamTransformAdd, streamTransformRemove, streamTransformUpdate));
    final List<StreamDescriptor> resultList = WebBackendConnectionsHandler.getStreamsToReset(catalogDiff);
    assertTrue(
        resultList.stream().anyMatch(
            streamDescriptor -> "added_stream".equalsIgnoreCase(streamDescriptor.getName())));
    assertTrue(
        resultList.stream().anyMatch(
            streamDescriptor -> "removed_stream".equalsIgnoreCase(streamDescriptor.getName())));
    assertTrue(
        resultList.stream().anyMatch(
            streamDescriptor -> "updated_stream".equalsIgnoreCase(streamDescriptor.getName())));
  }

  @Test
  void testGetSchemaChangeNoChange() {
    final ConnectionRead connectionReadNotBreaking = new ConnectionRead().breakingChange(false);

    assertEquals(SchemaChange.NO_CHANGE, wbHandler.getSchemaChange(null, Optional.of(UUID.randomUUID()), Optional.of(new ActorCatalogFetchEvent())));
    assertEquals(SchemaChange.NO_CHANGE,
        wbHandler.getSchemaChange(connectionReadNotBreaking, Optional.empty(), Optional.of(new ActorCatalogFetchEvent())));

    final UUID catalogId = UUID.randomUUID();

    assertEquals(SchemaChange.NO_CHANGE, wbHandler.getSchemaChange(connectionReadNotBreaking, Optional.of(catalogId),
        Optional.of(new ActorCatalogFetchEvent().withActorCatalogId(catalogId))));
  }

  @Test
  void testGetSchemaChangeBreaking() {
    final UUID sourceId = UUID.randomUUID();
    final ConnectionRead connectionReadWithSourceId = new ConnectionRead().sourceCatalogId(UUID.randomUUID()).sourceId(sourceId).breakingChange(true);

    assertEquals(SchemaChange.BREAKING, wbHandler.getSchemaChange(connectionReadWithSourceId,
        Optional.of(UUID.randomUUID()), Optional.empty()));
  }

  @Test
  void testGetSchemaChangeNotBreaking() {
    final UUID catalogId = UUID.randomUUID();
    final UUID differentCatalogId = UUID.randomUUID();
    final ConnectionRead connectionReadWithSourceId =
        new ConnectionRead().breakingChange(false);

    assertEquals(SchemaChange.NON_BREAKING, wbHandler.getSchemaChange(connectionReadWithSourceId,
        Optional.of(catalogId), Optional.of(new ActorCatalogFetchEvent().withActorCatalogId(differentCatalogId))));
  }

}
