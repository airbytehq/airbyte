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
import static java.util.stream.Collectors.toSet;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionUpdate;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.api.model.JobConfigType;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.JobListRequestBody;
import io.airbyte.api.model.JobReadList;
import io.airbyte.api.model.JobStatus;
import io.airbyte.api.model.JobWithAttemptsRead;
import io.airbyte.api.model.SourceDiscoverSchemaRead;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceRead;
import io.airbyte.api.model.SourceSchema;
import io.airbyte.api.model.SourceSchemaField;
import io.airbyte.api.model.SourceSchemaStream;
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

public class WebBackendConnectionsHandler {

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
    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody()
        .sourceId(connectionRead.getSourceId());
    final SourceRead source = sourceHandler.getSource(sourceIdRequestBody);

    final DestinationIdRequestBody destinationIdRequestBody = new DestinationIdRequestBody().destinationId(connectionRead.getDestinationId());
    final DestinationRead destination = destinationHandler.getDestination(destinationIdRequestBody);

    final JobListRequestBody jobListRequestBody = new JobListRequestBody()
        .configId(connectionRead.getConnectionId().toString())
        .configTypes(Collections.singletonList(JobConfigType.SYNC));

    final WbConnectionRead wbConnectionRead = new WbConnectionRead()
        .connectionId(connectionRead.getConnectionId())
        .sourceId(connectionRead.getSourceId())
        .destinationId(connectionRead.getDestinationId())
        .name(connectionRead.getName())
        .syncSchema(connectionRead.getSyncSchema())
        .status(connectionRead.getStatus())
        .schedule(connectionRead.getSchedule())
        .source(source)
        .destination(destination);

    final JobReadList jobReadList = jobHistoryHandler.listJobsFor(jobListRequestBody);
    wbConnectionRead.setIsSyncing(jobReadList.getJobs()
        .stream().map(JobWithAttemptsRead::getJob)
        .anyMatch(job -> job.getStatus() != JobStatus.FAILED && job.getStatus() != JobStatus.SUCCEEDED && job.getStatus() != JobStatus.CANCELLED));
    jobReadList.getJobs().stream().map(JobWithAttemptsRead::getJob).findFirst().ifPresent(job -> wbConnectionRead.setLastSync(job.getCreatedAt()));

    return wbConnectionRead;
  }

  public WbConnectionRead webBackendGetConnection(WebBackendConnectionRequestBody webBackendConnectionRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody()
        .connectionId(webBackendConnectionRequestBody.getConnectionId());

    final ConnectionRead connection = connectionsHandler.getConnection(connectionIdRequestBody);

    if (MoreBooleans.isTruthy(webBackendConnectionRequestBody.getWithRefreshedCatalog())) {
      final SourceIdRequestBody sourceId = new SourceIdRequestBody().sourceId(connection.getSourceId());
      final SourceDiscoverSchemaRead discoverSchema = schedulerHandler.discoverSchemaForSourceFromSourceId(sourceId);

      final SourceSchema original = connection.getSyncSchema();
      final SourceSchema discovered = discoverSchema.getSchema();
      final SourceSchema combined = updateSchemaWithDiscovery(original, discovered);

      connection.setSyncSchema(combined);
    }

    return buildWbConnectionRead(connection);
  }

  @VisibleForTesting
  protected static SourceSchema updateSchemaWithDiscovery(SourceSchema original, SourceSchema discovered) {
    final Map<String, SourceSchemaStream> originalStreamsByName = original.getStreams()
        .stream()
        .collect(toMap(SourceSchemaStream::getName, s -> s));

    final List<SourceSchemaStream> streams = new ArrayList<>();

    for (SourceSchemaStream stream : discovered.getStreams()) {
      final SourceSchemaStream outputStream = Jsons.clone(stream);
      final SourceSchemaStream originalStream = originalStreamsByName.get(outputStream.getName());

      if (originalStream != null) {
        final Set<String> fieldNames = outputStream.getFields().stream().map(SourceSchemaField::getName).collect(toSet());
        outputStream.setSelected(originalStream.getSelected());

        if (outputStream.getSupportedSyncModes().contains(originalStream.getSyncMode())) {
          outputStream.setSyncMode(originalStream.getSyncMode());
        }

        if (originalStream.getCursorField().size() > 0) {
          final String topLevelField = originalStream.getCursorField().get(0);
          if (fieldNames.contains(topLevelField)) {
            outputStream.setCursorField(originalStream.getCursorField());
          }
        }

        final Map<String, SourceSchemaField> originalFieldsByName = originalStream.getFields()
            .stream()
            .collect(toMap(SourceSchemaField::getName, f -> f));

        for (SourceSchemaField field : outputStream.getFields()) {
          if (originalFieldsByName.containsKey(field.getName())) {
            SourceSchemaField originalField = originalFieldsByName.get(field.getName());
            field.setSelected(originalField.getSelected());
          }
        }

      }
      streams.add(outputStream);
    }

    return new SourceSchema().streams(streams);
  }

  public ConnectionRead webBackendUpdateConnection(WebBackendConnectionUpdate webBackendConnectionUpdate)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final ConnectionUpdate connectionUpdate = toConnectionUpdate(webBackendConnectionUpdate);
    final ConnectionRead connectionRead = connectionsHandler.updateConnection(connectionUpdate);

    if (MoreBooleans.isTruthy(webBackendConnectionUpdate.getWithRefreshedCatalog())) {
      ConnectionIdRequestBody connectionId = new ConnectionIdRequestBody().connectionId(webBackendConnectionUpdate.getConnectionId());

      // wait for this to execute
      JobInfoRead resetJob = schedulerHandler.resetConnection(connectionId);

      if (!resetJob.getJob().getStatus().equals(JobStatus.SUCCEEDED)) {
        throw new RuntimeException("Resetting data after updating the connection failed! Please manually reset your data and launch a manual sync.");
      }

      // just create the job
      schedulerHandler.syncConnection(connectionId);
    }

    return connectionRead;
  }

  @VisibleForTesting
  protected static ConnectionUpdate toConnectionUpdate(WebBackendConnectionUpdate webBackendConnectionUpdate) {
    ConnectionUpdate connectionUpdate = new ConnectionUpdate();

    connectionUpdate.setConnectionId(webBackendConnectionUpdate.getConnectionId());
    connectionUpdate.setSchedule(webBackendConnectionUpdate.getSchedule());
    connectionUpdate.setStatus(webBackendConnectionUpdate.getStatus());
    connectionUpdate.setSyncSchema(webBackendConnectionUpdate.getSyncSchema());

    return connectionUpdate;
  }

}
