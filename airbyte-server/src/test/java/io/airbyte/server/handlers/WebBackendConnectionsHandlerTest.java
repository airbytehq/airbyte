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
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.api.model.AirbyteCatalog;
import io.airbyte.api.model.AirbyteStreamAndConfiguration;
import io.airbyte.api.model.AttemptRead;
import io.airbyte.api.model.AttemptStatus;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionReadList;
import io.airbyte.api.model.ConnectionSchedule;
import io.airbyte.api.model.ConnectionSchedule.TimeUnitEnum;
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
import io.airbyte.api.model.SourceDiscoverSchemaRead;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceRead;
import io.airbyte.api.model.SyncMode;
import io.airbyte.api.model.SynchronousJobRead;
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
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
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
    DestinationRead destinationRead = DestinationHelpers.getDestinationRead(destination, destinationDefinition);

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
    jobListRequestBody.setConfigTypes(Collections.singletonList(JobConfigType.SYNC));
    jobListRequestBody.setConfigId(connectionRead.getConnectionId().toString());
    when(jobHistoryHandler.listJobsFor(jobListRequestBody)).thenReturn(jobReadList);

    expected = new WbConnectionRead()
        .connectionId(connectionRead.getConnectionId())
        .sourceId(connectionRead.getSourceId())
        .destinationId(connectionRead.getDestinationId())
        .name(connectionRead.getName())
        .prefix(connectionRead.getPrefix())
        .syncCatalog(connectionRead.getSyncCatalog())
        .status(connectionRead.getStatus())
        .schedule(connectionRead.getSchedule())
        .source(sourceRead)
        .destination(destinationRead)
        .latestSyncJobCreatedAt(now.getEpochSecond())
        .latestSyncJobStatus(JobStatus.SUCCEEDED)
        .isSyncing(false);

    final AirbyteCatalog modifiedCatalog = ConnectionHelpers.generateBasicApiCatalog();

    when(schedulerHandler.discoverSchemaForSourceFromSourceId(sourceIdRequestBody)).thenReturn(
        new SourceDiscoverSchemaRead()
            .jobInfo(mock(SynchronousJobRead.class))
            .catalog(modifiedCatalog));

    expectedWithNewSchema = new WbConnectionRead()
        .connectionId(expected.getConnectionId())
        .sourceId(expected.getSourceId())
        .destinationId(expected.getDestinationId())
        .name(expected.getName())
        .prefix(expected.getPrefix())
        .syncCatalog(modifiedCatalog)
        .status(expected.getStatus())
        .schedule(expected.getSchedule())
        .source(expected.getSource())
        .destination(expected.getDestination())
        .latestSyncJobCreatedAt(expected.getLatestSyncJobCreatedAt())
        .latestSyncJobStatus(expected.getLatestSyncJobStatus())
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

    final AirbyteCatalog catalog = ConnectionHelpers.generateBasicApiCatalog();
    catalog.getStreams().get(0).getStream().setName("azkaban_users");

    final ConnectionSchedule schedule = new ConnectionSchedule().units(1L).timeUnit(TimeUnitEnum.MINUTES);

    final WebBackendConnectionUpdate input = new WebBackendConnectionUpdate()
        .prefix(standardSync.getPrefix())
        .connectionId(standardSync.getConnectionId())
        .status(ConnectionStatus.INACTIVE)
        .schedule(schedule)
        .syncCatalog(catalog)
        .withRefreshedCatalog(false);

    final ConnectionUpdate expected = new ConnectionUpdate()
        .prefix(standardSync.getPrefix())
        .connectionId(standardSync.getConnectionId())
        .status(ConnectionStatus.INACTIVE)
        .schedule(schedule)
        .syncCatalog(catalog);

    final ConnectionUpdate actual = WebBackendConnectionsHandler.toConnectionUpdate(input);

    assertEquals(expected, actual);
  }

  @Test
  public void testForCompleteness() {
    final Set<String> handledMethods = Set.of("schedule", "connectionId", "syncCatalog", "prefix", "status");

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
        .prefix(expected.getPrefix())
        .connectionId(expected.getConnectionId())
        .schedule(expected.getSchedule())
        .status(expected.getStatus())
        .syncCatalog(expected.getSyncCatalog());

    when(connectionsHandler.updateConnection(any())).thenReturn(
        new ConnectionRead()
            .connectionId(expected.getConnectionId())
            .sourceId(expected.getSourceId())
            .destinationId(expected.getDestinationId())
            .name(expected.getName())
            .prefix(expected.getPrefix())
            .syncCatalog(expected.getSyncCatalog())
            .status(expected.getStatus())
            .schedule(expected.getSchedule()));

    ConnectionRead connectionRead = wbHandler.webBackendUpdateConnection(updateBody);

    assertEquals(expected.getSyncCatalog(), connectionRead.getSyncCatalog());

    ConnectionIdRequestBody connectionId = new ConnectionIdRequestBody().connectionId(connectionRead.getConnectionId());
    verify(schedulerHandler, times(0)).resetConnection(connectionId);
    verify(schedulerHandler, times(0)).syncConnection(connectionId);
  }

  @Test
  void testUpdateConnectionWithUpdatedSchema() throws JsonValidationException, ConfigNotFoundException, IOException {
    WebBackendConnectionUpdate updateBody = new WebBackendConnectionUpdate()
        .prefix(expected.getPrefix())
        .connectionId(expected.getConnectionId())
        .schedule(expected.getSchedule())
        .status(expected.getStatus())
        .syncCatalog(expectedWithNewSchema.getSyncCatalog())
        .withRefreshedCatalog(true);

    when(connectionsHandler.updateConnection(any())).thenReturn(
        new ConnectionRead()
            .connectionId(expected.getConnectionId())
            .sourceId(expected.getSourceId())
            .destinationId(expected.getDestinationId())
            .name(expected.getName())
            .prefix(expected.getPrefix())
            .syncCatalog(expectedWithNewSchema.getSyncCatalog())
            .status(expected.getStatus())
            .schedule(expected.getSchedule()));

    ConnectionRead connectionRead = wbHandler.webBackendUpdateConnection(updateBody);

    assertEquals(expectedWithNewSchema.getSyncCatalog(), connectionRead.getSyncCatalog());

    ConnectionIdRequestBody connectionId = new ConnectionIdRequestBody().connectionId(connectionRead.getConnectionId());
    verify(schedulerHandler, times(1)).resetConnection(connectionId);
    verify(schedulerHandler, times(1)).syncConnection(connectionId);
  }

  @Test
  public void testUpdateSchemaWithDiscoveryFromEmpty() {
    final AirbyteCatalog original = new AirbyteCatalog().streams(List.of());
    final AirbyteCatalog discovered = ConnectionHelpers.generateBasicApiCatalog();
    discovered.getStreams().get(0).getStream()
        .name("stream1")
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of("field1", JsonSchemaPrimitive.STRING)))
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
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of("field1", JsonSchemaPrimitive.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    expected.getStreams().get(0).getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName("stream1");

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
            Field.of("field1", JsonSchemaPrimitive.NUMBER),
            Field.of("field2", JsonSchemaPrimitive.NUMBER),
            Field.of("field5", JsonSchemaPrimitive.STRING)))
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
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of("field2", JsonSchemaPrimitive.STRING)))
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
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of("field2", JsonSchemaPrimitive.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    expected.getStreams().get(0).getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName("stream1");

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
            Field.of("field1", JsonSchemaPrimitive.NUMBER),
            Field.of("field2", JsonSchemaPrimitive.NUMBER),
            Field.of("field5", JsonSchemaPrimitive.STRING)))
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
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of("field2", JsonSchemaPrimitive.STRING)))
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
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of("field5", JsonSchemaPrimitive.BOOLEAN)))
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
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of("field2", JsonSchemaPrimitive.STRING)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    expected.getStreams().get(0).getConfig()
        .syncMode(SyncMode.INCREMENTAL)
        .cursorField(List.of("field1"))
        .destinationSyncMode(DestinationSyncMode.APPEND)
        .primaryKey(Collections.emptyList())
        .aliasName("renamed_stream");
    final AirbyteStreamAndConfiguration expectedNewStream = ConnectionHelpers.generateBasicApiCatalog().getStreams().get(0);
    expectedNewStream.getStream()
        .name("stream2")
        .defaultCursorField(List.of("field5"))
        .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of("field5", JsonSchemaPrimitive.BOOLEAN)))
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    expectedNewStream.getConfig()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.OVERWRITE)
        .primaryKey(Collections.emptyList())
        .aliasName("stream2");
    expected.getStreams().add(expectedNewStream);

    final AirbyteCatalog actual = WebBackendConnectionsHandler.updateSchemaWithDiscovery(original, discovered);

    assertEquals(expected, actual);
  }

}
