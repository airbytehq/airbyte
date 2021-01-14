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

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.api.model.AttemptRead;
import io.airbyte.api.model.AttemptStatus;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionReadList;
import io.airbyte.api.model.ConnectionSchedule;
import io.airbyte.api.model.ConnectionStatus;
import io.airbyte.api.model.ConnectionUpdate;
import io.airbyte.api.model.DataType;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.api.model.JobConfigType;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.JobListRequestBody;
import io.airbyte.api.model.JobRead;
import io.airbyte.api.model.JobReadList;
import io.airbyte.api.model.JobStatus;
import io.airbyte.api.model.JobWithAttemptsRead;
import io.airbyte.api.model.SourceDiscoverSchemaRead;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceRead;
import io.airbyte.api.model.SourceSchema;
import io.airbyte.api.model.SourceSchemaField;
import io.airbyte.api.model.SourceSchemaStream;
import io.airbyte.api.model.SyncMode;
import io.airbyte.api.model.WbConnectionRead;
import io.airbyte.api.model.WbConnectionReadList;
import io.airbyte.api.model.WebBackendConnectionRequestBody;
import io.airbyte.api.model.WebBackendConnectionUpdate;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.server.helpers.ConnectionHelpers;
import io.airbyte.server.helpers.DestinationDefinitionHelpers;
import io.airbyte.server.helpers.DestinationHelpers;
import io.airbyte.server.helpers.SourceDefinitionHelpers;
import io.airbyte.server.helpers.SourceHelpers;
import io.airbyte.validation.json.JsonValidationException;
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

class WebBackendConnectionsHandlerTest {

  private ConnectionsHandler connectionsHandler;
  private SchedulerHandler schedulerHandler;
  private WebBackendConnectionsHandler wbHandler;

  private SourceRead sourceRead;
  private DestinationRead destinationRead;
  private ConnectionRead connectionRead;
  private WbConnectionRead expected;
  private WbConnectionRead expectedWithNewSchema;

  @BeforeEach
  public void setup() throws IOException, JsonValidationException, ConfigNotFoundException {
    connectionsHandler = mock(ConnectionsHandler.class);
    SourceHandler sourceHandler = mock(SourceHandler.class);
    DestinationHandler destinationHandler = mock(DestinationHandler.class);
    JobHistoryHandler jobHistoryHandler = mock(JobHistoryHandler.class);
    schedulerHandler = mock(SchedulerHandler.class);
    wbHandler = new WebBackendConnectionsHandler(connectionsHandler, sourceHandler, destinationHandler, jobHistoryHandler, schedulerHandler);

    final StandardSourceDefinition standardSourceDefinition = SourceDefinitionHelpers.generateSource();
    SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    sourceRead = SourceHelpers.getSourceRead(source, standardSourceDefinition);

    final StandardDestinationDefinition destinationDefinition = DestinationDefinitionHelpers.generateDestination();
    final DestinationConnection destination = DestinationHelpers.generateDestination(UUID.randomUUID());
    destinationRead = DestinationHelpers.getDestinationRead(destination, destinationDefinition);

    final StandardSync standardSync = ConnectionHelpers.generateSyncWithSourceId(source.getSourceId());
    connectionRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync);

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
    jobListRequestBody.setConfigType(JobConfigType.SYNC);
    jobListRequestBody.setConfigId(connectionRead.getConnectionId().toString());
    when(jobHistoryHandler.listJobsFor(jobListRequestBody)).thenReturn(jobReadList);

    expected = new WbConnectionRead()
        .connectionId(connectionRead.getConnectionId())
        .sourceId(connectionRead.getSourceId())
        .destinationId(connectionRead.getDestinationId())
        .name(connectionRead.getName())
        .syncSchema(connectionRead.getSyncSchema())
        .status(connectionRead.getStatus())
        .syncMode(connectionRead.getSyncMode())
        .schedule(connectionRead.getSchedule())
        .source(sourceRead)
        .destination(destinationRead)
        .lastSync(now.getEpochSecond())
        .isSyncing(false);

    final SourceSchemaField field = new SourceSchemaField()
        .dataType(DataType.NUMBER)
        .name("id")
        .cleanedName("id")
        .selected(true);

    final SourceSchemaStream stream = new SourceSchemaStream()
        .cleanedName("users")
        .name("users")
        .fields(Lists.newArrayList(field));

    final SourceSchema modifiedSchema = new SourceSchema().streams(Lists.newArrayList(stream));

    when(schedulerHandler.discoverSchemaForSourceFromSourceId(sourceIdRequestBody)).thenReturn(
        new SourceDiscoverSchemaRead()
            .jobInfo(mock(JobInfoRead.class))
            .schema(modifiedSchema));

    expectedWithNewSchema = new WbConnectionRead()
        .connectionId(expected.getConnectionId())
        .sourceId(expected.getSourceId())
        .destinationId(expected.getDestinationId())
        .name(expected.getName())
        .syncSchema(modifiedSchema)
        .status(expected.getStatus())
        .syncMode(expected.getSyncMode())
        .schedule(expected.getSchedule())
        .source(expected.getSource())
        .destination(expected.getDestination())
        .lastSync(expected.getLastSync())
        .isSyncing(expected.getIsSyncing());

    when(schedulerHandler.resetConnection(any())).thenReturn(new JobInfoRead().job(new JobRead().status(JobStatus.SUCCEEDED)));
  }

  @Test
  public void testWebBackendListConnectionsForWorkspace() throws ConfigNotFoundException, IOException, JsonValidationException {
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody();
    workspaceIdRequestBody.setWorkspaceId(sourceRead.getWorkspaceId());

    final ConnectionReadList connectionReadList = new ConnectionReadList();
    connectionReadList.setConnections(Collections.singletonList(connectionRead));
    when(connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody)).thenReturn(connectionReadList);

    final WbConnectionReadList wbConnectionReadList = wbHandler.webBackendListConnectionsForWorkspace(workspaceIdRequestBody);
    assertEquals(1, wbConnectionReadList.getConnections().size());
    assertEquals(expected, wbConnectionReadList.getConnections().get(0));
  }

  @Test
  public void testWebBackendGetConnection() throws ConfigNotFoundException, IOException, JsonValidationException {
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody();
    connectionIdRequestBody.setConnectionId(connectionRead.getConnectionId());

    final WebBackendConnectionRequestBody webBackendConnectionRequestBody = new WebBackendConnectionRequestBody();
    webBackendConnectionRequestBody.setConnectionId(connectionRead.getConnectionId());

    when(connectionsHandler.getConnection(connectionIdRequestBody)).thenReturn(connectionRead);

    final WbConnectionRead wbConnectionRead = wbHandler.webBackendGetConnection(webBackendConnectionRequestBody);

    assertEquals(expected, wbConnectionRead);
  }

  @Test
  public void testWebBackendGetConnectionWithDiscovery() throws ConfigNotFoundException, IOException, JsonValidationException {
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody();
    connectionIdRequestBody.setConnectionId(connectionRead.getConnectionId());

    final WebBackendConnectionRequestBody webBackendConnectionIdRequestBody = new WebBackendConnectionRequestBody();
    webBackendConnectionIdRequestBody.setConnectionId(connectionRead.getConnectionId());
    webBackendConnectionIdRequestBody.setWithRefreshedCatalog(true);

    when(connectionsHandler.getConnection(connectionIdRequestBody)).thenReturn(connectionRead);

    final WbConnectionRead wbConnectionRead = wbHandler.webBackendGetConnection(webBackendConnectionIdRequestBody);

    assertEquals(expectedWithNewSchema, wbConnectionRead);
  }

  @Test
  public void testToConnectionUpdate() throws IOException {
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    final StandardSync standardSync = ConnectionHelpers.generateSyncWithSourceId(source.getSourceId());

    final SourceSchema newApiSchema = ConnectionHelpers.generateBasicApiSchema();
    newApiSchema.getStreams().get(0).setName("azkaban_users");
    newApiSchema.getStreams().get(0).cleanedName("azkaban_users");

    final ConnectionSchedule schedule = new ConnectionSchedule().units(1L).timeUnit(ConnectionSchedule.TimeUnitEnum.MINUTES);

    final WebBackendConnectionUpdate input = new WebBackendConnectionUpdate()
        .connectionId(standardSync.getConnectionId())
        .status(ConnectionStatus.INACTIVE)
        .schedule(schedule)
        .syncSchema(newApiSchema)
        .withRefreshedCatalog(false);

    final ConnectionUpdate expected = new ConnectionUpdate()
        .connectionId(standardSync.getConnectionId())
        .status(ConnectionStatus.INACTIVE)
        .schedule(schedule)
        .syncSchema(newApiSchema);

    final ConnectionUpdate actual = WebBackendConnectionsHandler.toConnectionUpdate(input);

    assertEquals(expected, actual);
  }

  @Test
  public void testForCompleteness() {
    final Set<String> handledMethods = Set.of("schedule", "connectionId", "syncSchema", "status");

    final Set<String> methods = Arrays.stream(ConnectionUpdate.class.getMethods())
        .filter(method -> method.getReturnType() == ConnectionUpdate.class)
        .map(Method::getName)
        .collect(Collectors.toSet());

    final String message =
        "If this test is failing, it means you added a field to ConnectionUpdate. Congratulations, but you're not done yet. You should update WebBackendConnectionsHandler::extractConnectionUpdate and ensure that the field is tested in testExtractConnectionUpdate. Then you can add the field name here to make this test pass.";

    assertEquals(handledMethods, methods, message);
  }

  @Test
  void testUpdateConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    WebBackendConnectionUpdate updateBody = new WebBackendConnectionUpdate()
        .connectionId(expected.getConnectionId())
        .schedule(expected.getSchedule())
        .status(expected.getStatus())
        .syncSchema(expected.getSyncSchema());

    when(connectionsHandler.updateConnection(any())).thenReturn(
        new ConnectionRead()
            .connectionId(expected.getConnectionId())
            .sourceId(expected.getSourceId())
            .destinationId(expected.getDestinationId())
            .name(expected.getName())
            .syncSchema(expected.getSyncSchema())
            .status(expected.getStatus())
            .syncMode(expected.getSyncMode())
            .schedule(expected.getSchedule()));

    ConnectionRead connectionRead = wbHandler.webBackendUpdateConnection(updateBody);

    assertEquals(expected.getSyncSchema(), connectionRead.getSyncSchema());

    ConnectionIdRequestBody connectionId = new ConnectionIdRequestBody().connectionId(connectionRead.getConnectionId());
    verify(schedulerHandler, times(0)).resetConnection(connectionId);
    verify(schedulerHandler, times(0)).syncConnection(connectionId);
  }

  @Test
  void testUpdateConnectionWithUpdatedSchema() throws JsonValidationException, ConfigNotFoundException, IOException {
    WebBackendConnectionUpdate updateBody = new WebBackendConnectionUpdate()
        .connectionId(expected.getConnectionId())
        .schedule(expected.getSchedule())
        .status(expected.getStatus())
        .syncSchema(expectedWithNewSchema.getSyncSchema())
        .withRefreshedCatalog(true);

    when(connectionsHandler.updateConnection(any())).thenReturn(
        new ConnectionRead()
            .connectionId(expected.getConnectionId())
            .sourceId(expected.getSourceId())
            .destinationId(expected.getDestinationId())
            .name(expected.getName())
            .syncSchema(expectedWithNewSchema.getSyncSchema())
            .status(expected.getStatus())
            .syncMode(expected.getSyncMode())
            .schedule(expected.getSchedule()));

    ConnectionRead connectionRead = wbHandler.webBackendUpdateConnection(updateBody);

    assertEquals(expectedWithNewSchema.getSyncSchema(), connectionRead.getSyncSchema());

    ConnectionIdRequestBody connectionId = new ConnectionIdRequestBody().connectionId(connectionRead.getConnectionId());
    verify(schedulerHandler, times(1)).resetConnection(connectionId);
    verify(schedulerHandler, times(1)).syncConnection(connectionId);
  }

  @Test
  public void testUpdateSchemaWithDiscovery() {
    SourceSchema original = new SourceSchema()
        .streams(List.of(
            new SourceSchemaStream()
                .name("stream1")
                .cleanedName("stream1")
                .syncMode(SyncMode.INCREMENTAL)
                .cursorField(List.of("field2"))
                .defaultCursorField(List.of("field1"))
                .fields(List.of(
                    new SourceSchemaField()
                        .name("field1")
                        .cleanedName("field1")
                        .dataType(DataType.NUMBER)
                        .selected(true),
                    new SourceSchemaField()
                        .name("field2")
                        .cleanedName("field2")
                        .dataType(DataType.NUMBER)
                        .selected(true),
                    new SourceSchemaField()
                        .name("field5")
                        .cleanedName("field5")
                        .dataType(DataType.STRING)
                        .selected(true)))
                .selected(true)
                .sourceDefinedCursor(false)
                .supportedSyncModes(List.of(SyncMode.INCREMENTAL, SyncMode.FULL_REFRESH))));
    SourceSchema discovered = new SourceSchema()
        .streams(List.of(
            new SourceSchemaStream()
                .name("stream1")
                .cleanedName("stream1")
                .syncMode(SyncMode.FULL_REFRESH)
                .defaultCursorField(List.of("field3"))
                .fields(List.of(
                    new SourceSchemaField()
                        .name("field2")
                        .cleanedName("field2")
                        .dataType(DataType.STRING)))
                .selected(true)
                .sourceDefinedCursor(false)
                .supportedSyncModes(List.of(SyncMode.FULL_REFRESH))));
    SourceSchema expected = new SourceSchema()
        .streams(List.of(
            new SourceSchemaStream()
                .name("stream1")
                .cleanedName("stream1")
                .syncMode(SyncMode.FULL_REFRESH)
                .cursorField(List.of("field2"))
                .defaultCursorField(List.of("field3"))
                .fields(List.of(
                    new SourceSchemaField()
                        .name("field2")
                        .cleanedName("field2")
                        .dataType(DataType.STRING)
                        .selected(true)))
                .selected(true)
                .sourceDefinedCursor(false)
                .supportedSyncModes(List.of(SyncMode.FULL_REFRESH))));

    SourceSchema actual = WebBackendConnectionsHandler.updateSchemaWithDiscovery(original, discovered);

    assertEquals(expected, actual);
  }

}
