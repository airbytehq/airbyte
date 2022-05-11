/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.inOrder;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.api.model.AirbyteCatalog;
import io.airbyte.api.model.AirbyteStreamAndConfiguration;
import io.airbyte.api.model.AttemptRead;
import io.airbyte.api.model.AttemptStatus;
import io.airbyte.api.model.ConnectionCreate;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionReadList;
import io.airbyte.api.model.ConnectionSchedule;
import io.airbyte.api.model.ConnectionSchedule.TimeUnitEnum;
import io.airbyte.api.model.ConnectionSearch;
import io.airbyte.api.model.ConnectionStatus;
import io.airbyte.api.model.ConnectionUpdate;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.api.model.DestinationSyncMode;
import io.airbyte.api.model.JobConfigType;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.JobListRequestBody;
import io.airbyte.api.model.JobRead;
import io.airbyte.api.model.JobReadList;
import io.airbyte.api.model.JobStatus;
import io.airbyte.api.model.JobWithAttemptsRead;
import io.airbyte.api.model.NamespaceDefinitionType;
import io.airbyte.api.model.OperationRead;
import io.airbyte.api.model.OperationReadList;
import io.airbyte.api.model.OperationUpdate;
import io.airbyte.api.model.ResourceRequirements;
import io.airbyte.api.model.SourceDiscoverSchemaRead;
import io.airbyte.api.model.SourceDiscoverSchemaRequestBody;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceRead;
import io.airbyte.api.model.SyncMode;
import io.airbyte.api.model.SynchronousJobRead;
import io.airbyte.api.model.WebBackendConnectionCreate;
import io.airbyte.api.model.WebBackendConnectionRead;
import io.airbyte.api.model.WebBackendConnectionReadList;
import io.airbyte.api.model.WebBackendConnectionRequestBody;
import io.airbyte.api.model.WebBackendConnectionSearch;
import io.airbyte.api.model.WebBackendConnectionUpdate;
import io.airbyte.api.model.WebBackendOperationCreateOrUpdate;
import io.airbyte.api.model.WebBackendWorkspaceState;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.scheduler.client.EventRunner;
import io.airbyte.server.helpers.ConnectionHelpers;
import io.airbyte.server.helpers.DestinationDefinitionHelpers;
import io.airbyte.server.helpers.DestinationHelpers;
import io.airbyte.server.helpers.SourceDefinitionHelpers;
import io.airbyte.server.helpers.SourceHelpers;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.helper.ConnectionHelper;
import java.io.IOException;
import java.lang.reflect.Method;
import java.time.Instant;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InOrder;

class WebBackendConnectionsHandlerTest {

  private ConnectionsHandler connectionsHandler;
  private OperationsHandler operationsHandler;
  private SchedulerHandler schedulerHandler;
  private WebBackendConnectionsHandler wbHandler;

  private SourceRead sourceRead;
  private ConnectionRead connectionRead;
  private OperationReadList operationReadList;
  private WebBackendConnectionRead expected;
  private WebBackendConnectionRead expectedWithNewSchema;
  private FeatureFlags featureFlags;
  private EventRunner eventRunner;
  private ConnectionHelper connectionHelper;
  private ConfigRepository configRepository;

  @BeforeEach
  public void setup() throws IOException, JsonValidationException, ConfigNotFoundException {
    connectionsHandler = mock(ConnectionsHandler.class);
    operationsHandler = mock(OperationsHandler.class);
    final SourceHandler sourceHandler = mock(SourceHandler.class);
    final DestinationHandler destinationHandler = mock(DestinationHandler.class);
    final JobHistoryHandler jobHistoryHandler = mock(JobHistoryHandler.class);
    configRepository = mock(ConfigRepository.class);
    schedulerHandler = mock(SchedulerHandler.class);
    featureFlags = mock(FeatureFlags.class);
    eventRunner = mock(EventRunner.class);
    connectionHelper = mock(ConnectionHelper.class);
    wbHandler = new WebBackendConnectionsHandler(connectionsHandler,
        sourceHandler,
        destinationHandler,
        jobHistoryHandler,
        schedulerHandler,
        operationsHandler,
        featureFlags,
        eventRunner,
        configRepository);

    final StandardSourceDefinition standardSourceDefinition = SourceDefinitionHelpers.generateSourceDefinition();
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    sourceRead = SourceHelpers.getSourceRead(source, standardSourceDefinition);

    final StandardDestinationDefinition destinationDefinition = DestinationDefinitionHelpers.generateDestination();
    final DestinationConnection destination = DestinationHelpers.generateDestination(UUID.randomUUID());
    final DestinationRead destinationRead = DestinationHelpers.getDestinationRead(destination, destinationDefinition);

    final StandardSync standardSync = ConnectionHelpers.generateSyncWithSourceId(source.getSourceId());
    connectionRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync);
    operationReadList = new OperationReadList()
        .operations(List.of(new OperationRead()
            .operationId(connectionRead.getOperationIds().get(0))
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

    final JobReadList jobReadList = new JobReadList();
    jobReadList.setJobs(Collections.singletonList(jobRead));
    final JobListRequestBody jobListRequestBody = new JobListRequestBody();
    jobListRequestBody.setConfigTypes(Collections.singletonList(JobConfigType.SYNC));
    jobListRequestBody.setConfigId(connectionRead.getConnectionId().toString());
    when(jobHistoryHandler.listJobsFor(jobListRequestBody)).thenReturn(jobReadList);

    expected = new WebBackendConnectionRead()
        .connectionId(connectionRead.getConnectionId())
        .sourceId(connectionRead.getSourceId())
        .destinationId(connectionRead.getDestinationId())
        .operationIds(connectionRead.getOperationIds())
        .name(connectionRead.getName())
        .namespaceDefinition(connectionRead.getNamespaceDefinition())
        .namespaceFormat(connectionRead.getNamespaceFormat())
        .prefix(connectionRead.getPrefix())
        .syncCatalog(connectionRead.getSyncCatalog())
        .status(connectionRead.getStatus())
        .schedule(connectionRead.getSchedule())
        .source(sourceRead)
        .destination(destinationRead)
        .operations(operationReadList.getOperations())
        .latestSyncJobCreatedAt(now.getEpochSecond())
        .latestSyncJobStatus(JobStatus.SUCCEEDED)
        .isSyncing(false)
        .resourceRequirements(new ResourceRequirements()
            .cpuRequest(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getCpuRequest())
            .cpuLimit(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getCpuLimit())
            .memoryRequest(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getMemoryRequest())
            .memoryLimit(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getMemoryLimit()));

    final AirbyteCatalog modifiedCatalog = ConnectionHelpers.generateMultipleStreamsApiCatalog(2);

    final SourceDiscoverSchemaRequestBody sourceDiscoverSchema = new SourceDiscoverSchemaRequestBody();
    sourceDiscoverSchema.setSourceId(connectionRead.getSourceId());
    sourceDiscoverSchema.setDisableCache(true);
    when(schedulerHandler.discoverSchemaForSourceFromSourceId(sourceDiscoverSchema)).thenReturn(
        new SourceDiscoverSchemaRead()
            .jobInfo(mock(SynchronousJobRead.class))
            .catalog(modifiedCatalog));

    expectedWithNewSchema = new WebBackendConnectionRead()
        .connectionId(expected.getConnectionId())
        .sourceId(expected.getSourceId())
        .destinationId(expected.getDestinationId())
        .operationIds(expected.getOperationIds())
        .name(expected.getName())
        .namespaceDefinition(expected.getNamespaceDefinition())
        .namespaceFormat(expected.getNamespaceFormat())
        .prefix(expected.getPrefix())
        .syncCatalog(modifiedCatalog)
        .status(expected.getStatus())
        .schedule(expected.getSchedule())
        .source(expected.getSource())
        .destination(expected.getDestination())
        .operations(expected.getOperations())
        .latestSyncJobCreatedAt(expected.getLatestSyncJobCreatedAt())
        .latestSyncJobStatus(expected.getLatestSyncJobStatus())
        .isSyncing(expected.getIsSyncing())
        .resourceRequirements(new ResourceRequirements()
            .cpuRequest(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getCpuRequest())
            .cpuLimit(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getCpuLimit())
            .memoryRequest(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getMemoryRequest())
            .memoryLimit(ConnectionHelpers.TESTING_RESOURCE_REQUIREMENTS.getMemoryLimit()));

    when(schedulerHandler.resetConnection(any(ConnectionIdRequestBody.class)))
        .thenReturn(new JobInfoRead().job(new JobRead().status(JobStatus.SUCCEEDED)));
  }

  @Test
  public void testGetWorkspaceState() throws IOException {
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
  public void testGetWorkspaceStateEmpty() throws IOException {
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
  public void testWebBackendListConnectionsForWorkspace() throws ConfigNotFoundException, IOException, JsonValidationException {
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody();
    workspaceIdRequestBody.setWorkspaceId(sourceRead.getWorkspaceId());

    final ConnectionReadList connectionReadList = new ConnectionReadList();
    connectionReadList.setConnections(Collections.singletonList(connectionRead));
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody();
    connectionIdRequestBody.setConnectionId(connectionRead.getConnectionId());
    when(connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody)).thenReturn(connectionReadList);
    when(operationsHandler.listOperationsForConnection(connectionIdRequestBody)).thenReturn(operationReadList);

    final WebBackendConnectionReadList WebBackendConnectionReadList = wbHandler.webBackendListConnectionsForWorkspace(workspaceIdRequestBody);
    assertEquals(1, WebBackendConnectionReadList.getConnections().size());
    assertEquals(expected, WebBackendConnectionReadList.getConnections().get(0));
  }

  @Test
  public void testWebBackendListAllConnectionsForWorkspace() throws ConfigNotFoundException, IOException, JsonValidationException {
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody();
    workspaceIdRequestBody.setWorkspaceId(sourceRead.getWorkspaceId());

    final ConnectionReadList connectionReadList = new ConnectionReadList();
    connectionReadList.setConnections(Collections.singletonList(connectionRead));
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody();
    connectionIdRequestBody.setConnectionId(connectionRead.getConnectionId());
    when(connectionsHandler.listAllConnectionsForWorkspace(workspaceIdRequestBody)).thenReturn(connectionReadList);
    when(operationsHandler.listOperationsForConnection(connectionIdRequestBody)).thenReturn(operationReadList);

    final WebBackendConnectionReadList WebBackendConnectionReadList = wbHandler.webBackendListAllConnectionsForWorkspace(workspaceIdRequestBody);
    assertEquals(1, WebBackendConnectionReadList.getConnections().size());
    assertEquals(expected, WebBackendConnectionReadList.getConnections().get(0));
  }

  @Test
  public void testWebBackendSearchConnections() throws ConfigNotFoundException, IOException, JsonValidationException {
    final ConnectionReadList connectionReadList = new ConnectionReadList();
    connectionReadList.setConnections(Collections.singletonList(connectionRead));
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody();
    connectionIdRequestBody.setConnectionId(connectionRead.getConnectionId());

    when(operationsHandler.listOperationsForConnection(connectionIdRequestBody)).thenReturn(operationReadList);
    when(connectionsHandler.listConnections()).thenReturn(connectionReadList);
    when(connectionsHandler.matchSearch(new ConnectionSearch(), connectionRead)).thenReturn(true);

    final WebBackendConnectionSearch webBackendConnectionSearch = new WebBackendConnectionSearch();
    WebBackendConnectionReadList webBackendConnectionReadList = wbHandler.webBackendSearchConnections(webBackendConnectionSearch);
    assertEquals(1, webBackendConnectionReadList.getConnections().size());
    assertEquals(expected, webBackendConnectionReadList.getConnections().get(0));

    when(connectionsHandler.matchSearch(new ConnectionSearch(), connectionRead)).thenReturn(false);
    webBackendConnectionReadList = wbHandler.webBackendSearchConnections(webBackendConnectionSearch);
    assertEquals(0, webBackendConnectionReadList.getConnections().size());
  }

  @Test
  public void testWebBackendGetConnection() throws ConfigNotFoundException, IOException, JsonValidationException {
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody();
    connectionIdRequestBody.setConnectionId(connectionRead.getConnectionId());

    final WebBackendConnectionRequestBody webBackendConnectionRequestBody = new WebBackendConnectionRequestBody();
    webBackendConnectionRequestBody.setConnectionId(connectionRead.getConnectionId());

    when(connectionsHandler.getConnection(connectionRead.getConnectionId())).thenReturn(connectionRead);
    when(operationsHandler.listOperationsForConnection(connectionIdRequestBody)).thenReturn(operationReadList);

    final WebBackendConnectionRead WebBackendConnectionRead = wbHandler.webBackendGetConnection(webBackendConnectionRequestBody);

    assertEquals(expected, WebBackendConnectionRead);
  }

  public WebBackendConnectionRead testWebBackendGetConnection(final boolean withCatalogRefresh)
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
  public void testWebBackendGetConnectionWithDiscovery() throws ConfigNotFoundException, IOException, JsonValidationException {
    final WebBackendConnectionRead result = testWebBackendGetConnection(true);
    verify(schedulerHandler).discoverSchemaForSourceFromSourceId(any());
    assertEquals(expectedWithNewSchema, result);
  }

  @Test
  public void testWebBackendGetConnectionNoRefreshCatalog()
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final WebBackendConnectionRead result = testWebBackendGetConnection(false);
    verify(schedulerHandler, never()).discoverSchemaForSourceFromSourceId(any());
    assertEquals(expected, result);
  }

  @Test
  public void testToConnectionCreate() throws IOException {
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
        .sourceCatalogId(sourceCatalogId);

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
        .sourceCatalogId(sourceCatalogId);

    final ConnectionCreate actual = WebBackendConnectionsHandler.toConnectionCreate(input, operationIds);

    assertEquals(expected, actual);
  }

  @Test
  public void testToConnectionUpdate() throws IOException {
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
        .operationIds(List.of(newOperationId))
        .status(ConnectionStatus.INACTIVE)
        .schedule(schedule)
        .name(standardSync.getName())
        .syncCatalog(catalog)
        .withRefreshedCatalog(false);

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
        .syncCatalog(catalog);

    final ConnectionUpdate actual = WebBackendConnectionsHandler.toConnectionUpdate(input, operationIds);

    assertEquals(expected, actual);
  }

  @Test
  public void testForConnectionCreateCompleteness() {
    final Set<String> handledMethods =
        Set.of("name", "namespaceDefinition", "namespaceFormat", "prefix", "sourceId", "destinationId", "operationIds", "syncCatalog", "schedule",
            "status", "resourceRequirements", "sourceCatalogId");

    final Set<String> methods = Arrays.stream(ConnectionCreate.class.getMethods())
        .filter(method -> method.getReturnType() == ConnectionCreate.class)
        .map(Method::getName)
        .collect(Collectors.toSet());

    final String message =
        "If this test is failing, it means you added a field to ConnectionCreate!\nCongratulations, but you're not done yet...\n"
            + "\tYou should update WebBackendConnectionsHandler::toConnectionCreate\n"
            + "\tand ensure that the field is tested in WebBackendConnectionsHandlerTest::testToConnectionCreate\n"
            + "Then you can add the field name here to make this test pass. Cheers!";
    assertEquals(handledMethods, methods, message);
  }

  @Test
  public void testForConnectionUpdateCompleteness() {
    final Set<String> handledMethods =
        Set.of("schedule", "connectionId", "syncCatalog", "namespaceDefinition", "namespaceFormat", "prefix", "status", "operationIds",
            "resourceRequirements", "name", "sourceCatalogId");

    final Set<String> methods = Arrays.stream(ConnectionUpdate.class.getMethods())
        .filter(method -> method.getReturnType() == ConnectionUpdate.class)
        .map(Method::getName)
        .collect(Collectors.toSet());

    final String message =
        "If this test is failing, it means you added a field to ConnectionUpdate!\nCongratulations, but you're not done yet...\n"
            + "\tYou should update WebBackendConnectionsHandler::toConnectionUpdate\n"
            + "\tand ensure that the field is tested in WebBackendConnectionsHandlerTest::testToConnectionUpdate\n"
            + "Then you can add the field name here to make this test pass. Cheers!";
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
            .schedule(expected.getSchedule()));
    when(operationsHandler.listOperationsForConnection(any())).thenReturn(operationReadList);

    final WebBackendConnectionRead connectionRead = wbHandler.webBackendUpdateConnection(updateBody);

    assertEquals(expected.getSyncCatalog(), connectionRead.getSyncCatalog());

    final ConnectionIdRequestBody connectionId = new ConnectionIdRequestBody().connectionId(connectionRead.getConnectionId());
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

    when(connectionsHandler.getConnection(expected.getConnectionId())).thenReturn(
        new ConnectionRead()
            .connectionId(expected.getConnectionId())
            .operationIds(connectionRead.getOperationIds()));
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
            .schedule(expected.getSchedule()));
    when(operationsHandler.updateOperation(operationUpdate)).thenReturn(new OperationRead().operationId(operationUpdate.getOperationId()));
    when(operationsHandler.listOperationsForConnection(any())).thenReturn(operationReadList);
    final WebBackendConnectionRead actualConnectionRead = wbHandler.webBackendUpdateConnection(updateBody);

    assertEquals(connectionRead.getOperationIds(), actualConnectionRead.getOperationIds());
    verify(operationsHandler, times(1)).updateOperation(operationUpdate);
  }

  @Test
  void testUpdateConnectionWithUpdatedSchema() throws JsonValidationException, ConfigNotFoundException, IOException {
    final WebBackendConnectionUpdate updateBody = new WebBackendConnectionUpdate()
        .namespaceDefinition(expected.getNamespaceDefinition())
        .namespaceFormat(expected.getNamespaceFormat())
        .prefix(expected.getPrefix())
        .connectionId(expected.getConnectionId())
        .schedule(expected.getSchedule())
        .status(expected.getStatus())
        .syncCatalog(expectedWithNewSchema.getSyncCatalog())
        .withRefreshedCatalog(true);

    when(operationsHandler.listOperationsForConnection(any())).thenReturn(operationReadList);
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
            .syncCatalog(expectedWithNewSchema.getSyncCatalog())
            .status(expected.getStatus())
            .schedule(expected.getSchedule()));

    final WebBackendConnectionRead connectionRead = wbHandler.webBackendUpdateConnection(updateBody);

    assertEquals(expectedWithNewSchema.getSyncCatalog(), connectionRead.getSyncCatalog());

    final ConnectionIdRequestBody connectionId = new ConnectionIdRequestBody().connectionId(connectionRead.getConnectionId());
    verify(schedulerHandler, times(1)).resetConnection(connectionId);
    verify(schedulerHandler, times(1)).syncConnection(connectionId);
  }

  @Test
  void testUpdateConnectionWithUpdatedSchemaNewScheduler() throws JsonValidationException, ConfigNotFoundException, IOException {
    final WebBackendConnectionUpdate updateBody = new WebBackendConnectionUpdate()
        .namespaceDefinition(expected.getNamespaceDefinition())
        .namespaceFormat(expected.getNamespaceFormat())
        .prefix(expected.getPrefix())
        .connectionId(expected.getConnectionId())
        .schedule(expected.getSchedule())
        .status(expected.getStatus())
        .syncCatalog(expectedWithNewSchema.getSyncCatalog())
        .withRefreshedCatalog(true);

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
        .schedule(expected.getSchedule());
    when(connectionsHandler.updateConnection(any())).thenReturn(connectionRead);
    when(connectionsHandler.getConnection(expected.getConnectionId())).thenReturn(connectionRead);
    when(featureFlags.usesNewScheduler()).thenReturn(true);

    final WebBackendConnectionRead result = wbHandler.webBackendUpdateConnection(updateBody);

    assertEquals(expectedWithNewSchema.getSyncCatalog(), result.getSyncCatalog());

    final ConnectionIdRequestBody connectionId = new ConnectionIdRequestBody().connectionId(result.getConnectionId());
    verify(schedulerHandler, times(0)).resetConnection(connectionId);
    verify(schedulerHandler, times(0)).syncConnection(connectionId);
    verify(connectionsHandler, times(1)).updateConnection(any());
    final InOrder orderVerifier = inOrder(eventRunner);
    orderVerifier.verify(eventRunner, times(1)).synchronousResetConnection(connectionId.getConnectionId());
    orderVerifier.verify(eventRunner, times(1)).startNewManualSync(connectionId.getConnectionId());
  }

  @Test
  public void testUpdateSchemaWithDiscoveryFromEmpty() {
    final AirbyteCatalog original = new AirbyteCatalog().streams(List.of());
    final AirbyteCatalog discovered = ConnectionHelpers.generateBasicApiCatalog();
    discovered.getStreams().get(0).getStream()
        .name("stream1")
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of("field1", JsonSchemaType.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    discovered.getStreams().get(0).getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName("stream1");

    final AirbyteCatalog expected = ConnectionHelpers.generateBasicApiCatalog();
    expected.getStreams().get(0).getStream()
        .name("stream1")
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of("field1", JsonSchemaType.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    expected.getStreams().get(0).getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName("stream1")
        .setSelected(false);

    final AirbyteCatalog actual = WebBackendConnectionsHandler.updateSchemaWithDiscovery(original, discovered);

    assertEquals(expected, actual);
  }

  @Test
  public void testUpdateSchemaWithDiscoveryResetStream() {
    final AirbyteCatalog original = ConnectionHelpers.generateBasicApiCatalog();
    original.getStreams().get(0).getStream()
        .name("random-stream")
        .defaultCursorField(List.of("field1"))
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(
            Field.of("field1", JsonSchemaType.NUMBER),
            Field.of("field2", JsonSchemaType.NUMBER),
            Field.of("field5", JsonSchemaType.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    original.getStreams().get(0).getConfig()
        .syncMode(SyncMode.INCREMENTAL)
        .cursorField(List.of("field1"))
        .destinationSyncMode(DestinationSyncMode.APPEND)
        .primaryKey(Collections.emptyList())
        .aliasName("random_stream");

    final AirbyteCatalog discovered = ConnectionHelpers.generateBasicApiCatalog();
    discovered.getStreams().get(0).getStream()
        .name("stream1")
        .defaultCursorField(List.of("field3"))
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of("field2", JsonSchemaType.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    discovered.getStreams().get(0).getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName("stream1");

    final AirbyteCatalog expected = ConnectionHelpers.generateBasicApiCatalog();
    expected.getStreams().get(0).getStream()
        .name("stream1")
        .defaultCursorField(List.of("field3"))
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of("field2", JsonSchemaType.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    expected.getStreams().get(0).getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName("stream1")
        .setSelected(false);

    final AirbyteCatalog actual = WebBackendConnectionsHandler.updateSchemaWithDiscovery(original, discovered);

    assertEquals(expected, actual);
  }

  @Test
  public void testUpdateSchemaWithDiscoveryMergeNewStream() {
    final AirbyteCatalog original = ConnectionHelpers.generateBasicApiCatalog();
    original.getStreams().get(0).getStream()
        .name("stream1")
        .defaultCursorField(List.of("field1"))
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(
            Field.of("field1", JsonSchemaType.NUMBER),
            Field.of("field2", JsonSchemaType.NUMBER),
            Field.of("field5", JsonSchemaType.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    original.getStreams().get(0).getConfig()
        .syncMode(SyncMode.INCREMENTAL)
        .cursorField(List.of("field1"))
        .destinationSyncMode(DestinationSyncMode.APPEND)
        .primaryKey(Collections.emptyList())
        .aliasName("renamed_stream");

    final AirbyteCatalog discovered = ConnectionHelpers.generateBasicApiCatalog();
    discovered.getStreams().get(0).getStream()
        .name("stream1")
        .defaultCursorField(List.of("field3"))
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of("field2", JsonSchemaType.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    discovered.getStreams().get(0).getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName("stream1");
    final AirbyteStreamAndConfiguration newStream = ConnectionHelpers.generateBasicApiCatalog().getStreams().get(0);
    newStream.getStream()
        .name("stream2")
        .defaultCursorField(List.of("field5"))
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of("field5", JsonSchemaType.BOOLEAN)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    newStream.getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName("stream2");
    discovered.getStreams().add(newStream);

    final AirbyteCatalog expected = ConnectionHelpers.generateBasicApiCatalog();
    expected.getStreams().get(0).getStream()
        .name("stream1")
        .defaultCursorField(List.of("field3"))
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of("field2", JsonSchemaType.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    expected.getStreams().get(0).getConfig()
        .syncMode(SyncMode.INCREMENTAL)
        .cursorField(List.of("field1"))
        .destinationSyncMode(DestinationSyncMode.APPEND)
        .primaryKey(Collections.emptyList())
        .aliasName("renamed_stream")
        .setSelected(true);
    final AirbyteStreamAndConfiguration expectedNewStream = ConnectionHelpers.generateBasicApiCatalog().getStreams().get(0);
    expectedNewStream.getStream()
        .name("stream2")
        .defaultCursorField(List.of("field5"))
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of("field5", JsonSchemaType.BOOLEAN)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    expectedNewStream.getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName("stream2")
        .setSelected(false);
    expected.getStreams().add(expectedNewStream);

    final AirbyteCatalog actual = WebBackendConnectionsHandler.updateSchemaWithDiscovery(original, discovered);

    assertEquals(expected, actual);
  }

}
