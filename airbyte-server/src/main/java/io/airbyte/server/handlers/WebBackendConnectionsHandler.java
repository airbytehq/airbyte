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

import static java.util.stream.Collectors.toMap;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.api.model.AirbyteCatalog;
import io.airbyte.api.model.AirbyteStream;
import io.airbyte.api.model.AirbyteStreamAndConfiguration;
import io.airbyte.api.model.AirbyteStreamConfiguration;
import io.airbyte.api.model.ConnectionCreate;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionUpdate;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.api.model.JobConfigType;
import io.airbyte.api.model.JobListRequestBody;
import io.airbyte.api.model.JobRead;
import io.airbyte.api.model.JobReadList;
import io.airbyte.api.model.JobStatus;
import io.airbyte.api.model.JobWithAttemptsRead;
import io.airbyte.api.model.OperationCreate;
import io.airbyte.api.model.OperationReadList;
import io.airbyte.api.model.OperationUpdate;
import io.airbyte.api.model.SourceDiscoverSchemaRead;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceRead;
import io.airbyte.api.model.WebBackendConnectionCreate;
import io.airbyte.api.model.WebBackendConnectionRead;
import io.airbyte.api.model.WebBackendConnectionReadList;
import io.airbyte.api.model.WebBackendConnectionRequestBody;
import io.airbyte.api.model.WebBackendConnectionUpdate;
import io.airbyte.api.model.WebBackendOperationCreateOrUpdate;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.MoreBooleans;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.function.Predicate;

public class WebBackendConnectionsHandler {

  private static final Set<JobStatus> TERMINAL_STATUSES = Sets.newHashSet(JobStatus.FAILED, JobStatus.SUCCEEDED, JobStatus.CANCELLED);

  private final ConnectionsHandler connectionsHandler;
  private final SourceHandler sourceHandler;
  private final DestinationHandler destinationHandler;
  private final JobHistoryHandler jobHistoryHandler;
  private final SchedulerHandler schedulerHandler;
  private final OperationsHandler operationsHandler;

  public WebBackendConnectionsHandler(final ConnectionsHandler connectionsHandler,
                                      final SourceHandler sourceHandler,
                                      final DestinationHandler destinationHandler,
                                      final JobHistoryHandler jobHistoryHandler,
                                      final SchedulerHandler schedulerHandler,
                                      final OperationsHandler operationsHandler) {
    this.connectionsHandler = connectionsHandler;
    this.sourceHandler = sourceHandler;
    this.destinationHandler = destinationHandler;
    this.jobHistoryHandler = jobHistoryHandler;
    this.schedulerHandler = schedulerHandler;
    this.operationsHandler = operationsHandler;
  }

  public WebBackendConnectionReadList webBackendListConnectionsForWorkspace(WorkspaceIdRequestBody workspaceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {

    final List<WebBackendConnectionRead> reads = Lists.newArrayList();
    for (ConnectionRead connection : connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody).getConnections()) {
      reads.add(buildWebBackendConnectionRead(connection));
    }
    return new WebBackendConnectionReadList().connections(reads);
  }

  private WebBackendConnectionRead buildWebBackendConnectionRead(ConnectionRead connectionRead)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final SourceRead source = getSourceRead(connectionRead);
    final DestinationRead destination = getDestinationRead(connectionRead);
    final OperationReadList operations = getOperationReadList(connectionRead);
    final WebBackendConnectionRead WebBackendConnectionRead = getWebBackendConnectionRead(connectionRead, source, destination, operations);

    final JobReadList syncJobReadList = getSyncJobs(connectionRead);
    Predicate<JobRead> hasRunningJob = (JobRead job) -> !TERMINAL_STATUSES.contains(job.getStatus());
    WebBackendConnectionRead.setIsSyncing(syncJobReadList.getJobs().stream().map(JobWithAttemptsRead::getJob).anyMatch(hasRunningJob));
    setLatestSyncJobProperties(WebBackendConnectionRead, syncJobReadList);
    return WebBackendConnectionRead;
  }

  private SourceRead getSourceRead(ConnectionRead connectionRead) throws JsonValidationException, IOException, ConfigNotFoundException {
    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody().sourceId(connectionRead.getSourceId());
    SourceRead sourceRead = sourceHandler.getSource(sourceIdRequestBody);

    return sourceRead;
  }

  private DestinationRead getDestinationRead(ConnectionRead connectionRead) throws JsonValidationException, IOException, ConfigNotFoundException {
    final DestinationIdRequestBody destinationIdRequestBody = new DestinationIdRequestBody().destinationId(connectionRead.getDestinationId());
    return destinationHandler.getDestination(destinationIdRequestBody);
  }

  private OperationReadList getOperationReadList(ConnectionRead connectionRead) throws JsonValidationException, IOException, ConfigNotFoundException {
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody().connectionId(connectionRead.getConnectionId());
    return operationsHandler.listOperationsForConnection(connectionIdRequestBody);
  }

  private WebBackendConnectionRead getWebBackendConnectionRead(ConnectionRead connectionRead,
                                                               SourceRead source,
                                                               DestinationRead destination,
                                                               OperationReadList operations) {
    return new WebBackendConnectionRead()
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
        .source(source)
        .destination(destination)
        .operations(operations.getOperations())
        .resourceRequirements(connectionRead.getResourceRequirements());
  }

  private JobReadList getSyncJobs(ConnectionRead connectionRead) throws IOException {
    final JobListRequestBody jobListRequestBody = new JobListRequestBody()
        .configId(connectionRead.getConnectionId().toString())
        .configTypes(Collections.singletonList(JobConfigType.SYNC));
    return jobHistoryHandler.listJobsFor(jobListRequestBody);
  }

  private void setLatestSyncJobProperties(WebBackendConnectionRead WebBackendConnectionRead, JobReadList syncJobReadList) {
    syncJobReadList.getJobs().stream().map(JobWithAttemptsRead::getJob).findFirst()
        .ifPresent(job -> {
          WebBackendConnectionRead.setLatestSyncJobCreatedAt(job.getCreatedAt());
          WebBackendConnectionRead.setLatestSyncJobStatus(job.getStatus());
        });
  }

  public WebBackendConnectionRead webBackendGetConnection(WebBackendConnectionRequestBody webBackendConnectionRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody()
        .connectionId(webBackendConnectionRequestBody.getConnectionId());

    final ConnectionRead connection = connectionsHandler.getConnection(connectionIdRequestBody);

    if (MoreBooleans.isTruthy(webBackendConnectionRequestBody.getWithRefreshedCatalog())) {
      final SourceIdRequestBody sourceId = new SourceIdRequestBody().sourceId(connection.getSourceId());
      final SourceDiscoverSchemaRead discoverSchema = schedulerHandler.discoverSchemaForSourceFromSourceId(sourceId);

      final AirbyteCatalog original = connection.getSyncCatalog();
      final AirbyteCatalog discovered = discoverSchema.getCatalog();
      final AirbyteCatalog combined = updateSchemaWithDiscovery(original, discovered);

      connection.setSyncCatalog(combined);
    }

    return buildWebBackendConnectionRead(connection);
  }

  @VisibleForTesting
  protected static AirbyteCatalog updateSchemaWithDiscovery(AirbyteCatalog original, AirbyteCatalog discovered) {
    final Map<String, AirbyteStreamAndConfiguration> originalStreamsByName = original.getStreams()
        .stream()
        .collect(toMap(s -> s.getStream().getName(), s -> s));

    final List<AirbyteStreamAndConfiguration> streams = new ArrayList<>();

    for (AirbyteStreamAndConfiguration s : discovered.getStreams()) {
      final AirbyteStream stream = s.getStream();
      final AirbyteStreamAndConfiguration originalStream = originalStreamsByName.get(stream.getName());
      AirbyteStreamConfiguration outputStreamConfig;

      if (originalStream != null) {
        final AirbyteStreamConfiguration originalStreamConfig = originalStream.getConfig();
        final AirbyteStreamConfiguration discoveredStreamConfig = s.getConfig();
        outputStreamConfig = new AirbyteStreamConfiguration();

        if (stream.getSupportedSyncModes().contains(originalStreamConfig.getSyncMode()))
          outputStreamConfig.setSyncMode(originalStreamConfig.getSyncMode());
        else
          outputStreamConfig.setSyncMode(discoveredStreamConfig.getSyncMode());

        if (originalStreamConfig.getCursorField().size() > 0) {
          outputStreamConfig.setCursorField(originalStreamConfig.getCursorField());
        } else {
          outputStreamConfig.setCursorField(discoveredStreamConfig.getCursorField());
        }

        outputStreamConfig.setDestinationSyncMode(originalStreamConfig.getDestinationSyncMode());
        if (originalStreamConfig.getPrimaryKey().size() > 0) {
          outputStreamConfig.setPrimaryKey(originalStreamConfig.getPrimaryKey());
        } else {
          outputStreamConfig.setPrimaryKey(discoveredStreamConfig.getPrimaryKey());
        }

        outputStreamConfig.setAliasName(originalStreamConfig.getAliasName());
        outputStreamConfig.setSelected(originalStreamConfig.getSelected());
      } else {
        outputStreamConfig = s.getConfig();
      }
      final AirbyteStreamAndConfiguration outputStream = new AirbyteStreamAndConfiguration()
          .stream(Jsons.clone(stream))
          .config(outputStreamConfig);
      streams.add(outputStream);
    }
    return new AirbyteCatalog().streams(streams);
  }

  public WebBackendConnectionRead webBackendCreateConnection(WebBackendConnectionCreate webBackendConnectionCreate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<UUID> operationIds = createOperations(webBackendConnectionCreate);
    final ConnectionCreate connectionCreate = toConnectionCreate(webBackendConnectionCreate, operationIds);
    return buildWebBackendConnectionRead(connectionsHandler.createConnection(connectionCreate));
  }

  public WebBackendConnectionRead webBackendUpdateConnection(WebBackendConnectionUpdate webBackendConnectionUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<UUID> operationIds = updateOperations(webBackendConnectionUpdate);
    final ConnectionUpdate connectionUpdate = toConnectionUpdate(webBackendConnectionUpdate, operationIds);
    final ConnectionRead connectionRead = connectionsHandler.updateConnection(connectionUpdate);

    if (MoreBooleans.isTruthy(webBackendConnectionUpdate.getWithRefreshedCatalog())) {
      ConnectionIdRequestBody connectionId = new ConnectionIdRequestBody().connectionId(webBackendConnectionUpdate.getConnectionId());

      // wait for this to execute
      schedulerHandler.resetConnection(connectionId);

      // just create the job
      schedulerHandler.syncConnection(connectionId);
    }
    return buildWebBackendConnectionRead(connectionRead);
  }

  private List<UUID> createOperations(WebBackendConnectionCreate webBackendConnectionCreate)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final List<UUID> operationIds = new ArrayList<>();
    for (var operationCreate : webBackendConnectionCreate.getOperations()) {
      operationIds.add(operationsHandler.createOperation(operationCreate).getOperationId());
    }
    return operationIds;
  }

  private List<UUID> updateOperations(WebBackendConnectionUpdate webBackendConnectionUpdate)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final ConnectionRead connectionRead = connectionsHandler
        .getConnection(new ConnectionIdRequestBody().connectionId(webBackendConnectionUpdate.getConnectionId()));
    final List<UUID> originalOperationIds = new ArrayList<>(connectionRead.getOperationIds());
    final List<UUID> operationIds = new ArrayList<>();

    for (var operationCreateOrUpdate : webBackendConnectionUpdate.getOperations()) {
      if (operationCreateOrUpdate.getOperationId() == null || !originalOperationIds.contains(operationCreateOrUpdate.getOperationId())) {
        final OperationCreate operationCreate = toOperationCreate(operationCreateOrUpdate);
        operationIds.add(operationsHandler.createOperation(operationCreate).getOperationId());
      } else {
        final OperationUpdate operationUpdate = toOperationUpdate(operationCreateOrUpdate);
        operationIds.add(operationsHandler.updateOperation(operationUpdate).getOperationId());
      }
    }
    originalOperationIds.removeAll(operationIds);
    operationsHandler.deleteOperationsForConnection(connectionRead.getConnectionId(), originalOperationIds);
    return operationIds;
  }

  private UUID getWorkspaceIdForConnection(UUID connectionId) throws JsonValidationException, ConfigNotFoundException, IOException {
    final UUID sourceId = connectionsHandler.getConnection(new ConnectionIdRequestBody().connectionId(connectionId)).getSourceId();
    return getWorkspaceIdForSource(sourceId);
  }

  private UUID getWorkspaceIdForSource(UUID sourceId) throws JsonValidationException, ConfigNotFoundException, IOException {
    return sourceHandler.getSource(new SourceIdRequestBody().sourceId(sourceId)).getWorkspaceId();
  }

  @VisibleForTesting
  protected static OperationCreate toOperationCreate(WebBackendOperationCreateOrUpdate operationCreateOrUpdate) {
    final OperationCreate operationCreate = new OperationCreate();

    operationCreate.name(operationCreateOrUpdate.getName());
    operationCreate.workspaceId(operationCreateOrUpdate.getWorkspaceId());
    operationCreate.operatorConfiguration(operationCreateOrUpdate.getOperatorConfiguration());

    return operationCreate;
  }

  @VisibleForTesting
  protected static OperationUpdate toOperationUpdate(WebBackendOperationCreateOrUpdate operationCreateOrUpdate) {
    final OperationUpdate operationUpdate = new OperationUpdate();

    operationUpdate.operationId(operationCreateOrUpdate.getOperationId());
    operationUpdate.name(operationCreateOrUpdate.getName());
    operationUpdate.operatorConfiguration(operationCreateOrUpdate.getOperatorConfiguration());

    return operationUpdate;
  }

  @VisibleForTesting
  protected static ConnectionCreate toConnectionCreate(WebBackendConnectionCreate webBackendConnectionCreate, List<UUID> operationIds) {
    final ConnectionCreate connectionCreate = new ConnectionCreate();

    connectionCreate.name(webBackendConnectionCreate.getName());
    connectionCreate.namespaceDefinition(webBackendConnectionCreate.getNamespaceDefinition());
    connectionCreate.namespaceFormat(webBackendConnectionCreate.getNamespaceFormat());
    connectionCreate.prefix(webBackendConnectionCreate.getPrefix());
    connectionCreate.sourceId(webBackendConnectionCreate.getSourceId());
    connectionCreate.destinationId(webBackendConnectionCreate.getDestinationId());
    connectionCreate.operationIds(operationIds);
    connectionCreate.syncCatalog(webBackendConnectionCreate.getSyncCatalog());
    connectionCreate.schedule(webBackendConnectionCreate.getSchedule());
    connectionCreate.status(webBackendConnectionCreate.getStatus());
    connectionCreate.resourceRequirements(webBackendConnectionCreate.getResourceRequirements());

    return connectionCreate;
  }

  @VisibleForTesting
  protected static ConnectionUpdate toConnectionUpdate(WebBackendConnectionUpdate webBackendConnectionUpdate, List<UUID> operationIds) {
    final ConnectionUpdate connectionUpdate = new ConnectionUpdate();

    connectionUpdate.connectionId(webBackendConnectionUpdate.getConnectionId());
    connectionUpdate.namespaceDefinition(webBackendConnectionUpdate.getNamespaceDefinition());
    connectionUpdate.namespaceFormat(webBackendConnectionUpdate.getNamespaceFormat());
    connectionUpdate.prefix(webBackendConnectionUpdate.getPrefix());
    connectionUpdate.operationIds(operationIds);
    connectionUpdate.syncCatalog(webBackendConnectionUpdate.getSyncCatalog());
    connectionUpdate.schedule(webBackendConnectionUpdate.getSchedule());
    connectionUpdate.status(webBackendConnectionUpdate.getStatus());
    connectionUpdate.resourceRequirements(webBackendConnectionUpdate.getResourceRequirements());

    return connectionUpdate;
  }

}
