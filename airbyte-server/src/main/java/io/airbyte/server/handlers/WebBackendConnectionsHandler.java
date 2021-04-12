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
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionUpdate;
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
import io.airbyte.api.model.WbConnectionRead;
import io.airbyte.api.model.WbConnectionReadList;
import io.airbyte.api.model.WebBackendConnectionRequestBody;
import io.airbyte.api.model.WebBackendConnectionUpdate;
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
import java.util.function.Predicate;

public class WebBackendConnectionsHandler {

  private static final Set<JobStatus> TERMINAL_STATUSES = Sets.newHashSet(JobStatus.FAILED, JobStatus.SUCCEEDED, JobStatus.CANCELLED);

  private final ConnectionsHandler connectionsHandler;
  private final SourceHandler sourceHandler;
  private final DestinationHandler destinationHandler;
  private final JobHistoryHandler jobHistoryHandler;
  private final SchedulerHandler schedulerHandler;

  public WebBackendConnectionsHandler(final ConnectionsHandler connectionsHandler,
                                      final SourceHandler sourceHandler,
                                      final DestinationHandler destinationHandler,
                                      final JobHistoryHandler jobHistoryHandler,
                                      final SchedulerHandler schedulerHandler) {
    this.connectionsHandler = connectionsHandler;
    this.sourceHandler = sourceHandler;
    this.destinationHandler = destinationHandler;
    this.jobHistoryHandler = jobHistoryHandler;
    this.schedulerHandler = schedulerHandler;
  }

  public WbConnectionReadList webBackendListConnectionsForWorkspace(WorkspaceIdRequestBody workspaceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {

    final List<WbConnectionRead> reads = Lists.newArrayList();
    for (ConnectionRead connection : connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody).getConnections()) {
      reads.add(buildWbConnectionRead(connection));
    }
    return new WbConnectionReadList().connections(reads);
  }

  private WbConnectionRead buildWbConnectionRead(ConnectionRead connectionRead) throws ConfigNotFoundException, IOException, JsonValidationException {
    final SourceRead source = getSourceRead(connectionRead);
    final DestinationRead destination = getDestinationRead(connectionRead);
    final WbConnectionRead wbConnectionRead = getWbConnectionRead(connectionRead, source, destination);

    final JobReadList syncJobReadList = getSyncJobs(connectionRead);
    Predicate<JobRead> hasRunningJob = (JobRead job) -> !TERMINAL_STATUSES.contains(job.getStatus());
    wbConnectionRead.setIsSyncing(syncJobReadList.getJobs().stream().map(JobWithAttemptsRead::getJob).anyMatch(hasRunningJob));
    setLatestSyncJobProperties(wbConnectionRead, syncJobReadList);
    return wbConnectionRead;
  }

  private SourceRead getSourceRead(ConnectionRead connectionRead) throws JsonValidationException, IOException, ConfigNotFoundException {
    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody().sourceId(connectionRead.getSourceId());
    return sourceHandler.getSource(sourceIdRequestBody);
  }

  private DestinationRead getDestinationRead(ConnectionRead connectionRead) throws JsonValidationException, IOException, ConfigNotFoundException {
    final DestinationIdRequestBody destinationIdRequestBody = new DestinationIdRequestBody().destinationId(connectionRead.getDestinationId());
    return destinationHandler.getDestination(destinationIdRequestBody);
  }

  private WbConnectionRead getWbConnectionRead(ConnectionRead connectionRead, SourceRead source, DestinationRead destination) {
    return new WbConnectionRead()
        .connectionId(connectionRead.getConnectionId())
        .sourceId(connectionRead.getSourceId())
        .destinationId(connectionRead.getDestinationId())
        .name(connectionRead.getName())
        .prefix(connectionRead.getPrefix())
        .syncCatalog(connectionRead.getSyncCatalog())
        .status(connectionRead.getStatus())
        .schedule(connectionRead.getSchedule())
        .source(source)
        .destination(destination);
  }

  private JobReadList getSyncJobs(ConnectionRead connectionRead) throws IOException {
    final JobListRequestBody jobListRequestBody = new JobListRequestBody()
        .configId(connectionRead.getConnectionId().toString())
        .configTypes(Collections.singletonList(JobConfigType.SYNC));
    return jobHistoryHandler.listJobsFor(jobListRequestBody);
  }

  private void setLatestSyncJobProperties(WbConnectionRead wbConnectionRead, JobReadList syncJobReadList) {
    syncJobReadList.getJobs().stream().map(JobWithAttemptsRead::getJob).findFirst()
        .ifPresent(job -> {
          wbConnectionRead.setLatestSyncJobCreatedAt(job.getCreatedAt());
          wbConnectionRead.setLatestSyncJobStatus(job.getStatus());
        });
  }

  public WbConnectionRead webBackendGetConnection(WebBackendConnectionRequestBody webBackendConnectionRequestBody)
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

    return buildWbConnectionRead(connection);
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

  public ConnectionRead webBackendUpdateConnection(WebBackendConnectionUpdate webBackendConnectionUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final ConnectionUpdate connectionUpdate = toConnectionUpdate(webBackendConnectionUpdate);
    final ConnectionRead connectionRead = connectionsHandler.updateConnection(connectionUpdate);

    if (MoreBooleans.isTruthy(webBackendConnectionUpdate.getWithRefreshedCatalog())) {
      ConnectionIdRequestBody connectionId = new ConnectionIdRequestBody().connectionId(webBackendConnectionUpdate.getConnectionId());

      // wait for this to execute
      JobInfoRead resetJob = schedulerHandler.resetConnection(connectionId);

      // just create the job
      schedulerHandler.syncConnection(connectionId);
    }

    return connectionRead;
  }

  @VisibleForTesting
  protected static ConnectionUpdate toConnectionUpdate(WebBackendConnectionUpdate webBackendConnectionUpdate) {
    ConnectionUpdate connectionUpdate = new ConnectionUpdate();

    connectionUpdate.setPrefix(webBackendConnectionUpdate.getPrefix());
    connectionUpdate.setConnectionId(webBackendConnectionUpdate.getConnectionId());
    connectionUpdate.setSchedule(webBackendConnectionUpdate.getSchedule());
    connectionUpdate.setStatus(webBackendConnectionUpdate.getStatus());
    connectionUpdate.setSyncCatalog(webBackendConnectionUpdate.getSyncCatalog());

    return connectionUpdate;
  }

}
