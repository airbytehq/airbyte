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

import com.google.common.collect.Lists;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.DestinationIdRequestBody;
import io.airbyte.api.model.DestinationRead;
import io.airbyte.api.model.JobConfigType;
import io.airbyte.api.model.JobListRequestBody;
import io.airbyte.api.model.JobReadList;
import io.airbyte.api.model.JobStatus;
import io.airbyte.api.model.SourceIdRequestBody;
import io.airbyte.api.model.SourceRead;
import io.airbyte.api.model.SyncMode;
import io.airbyte.api.model.WbConnectionRead;
import io.airbyte.api.model.WbConnectionReadList;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;

public class WebBackendConnectionsHandler {

  private final ConnectionsHandler connectionsHandler;
  private final SourceHandler sourceHandler;
  private final DestinationHandler destinationHandler;
  private final JobHistoryHandler jobHistoryHandler;

  public WebBackendConnectionsHandler(final ConnectionsHandler connectionsHandler,
                                      final SourceHandler sourceHandler,
                                      final DestinationHandler destinationHandler,
                                      final JobHistoryHandler jobHistoryHandler) {
    this.connectionsHandler = connectionsHandler;
    this.sourceHandler = sourceHandler;
    this.destinationHandler = destinationHandler;
    this.jobHistoryHandler = jobHistoryHandler;
  }

  public WbConnectionReadList webBackendListConnectionsForWorkspace(WorkspaceIdRequestBody workspaceIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {

    final List<WbConnectionRead> reads = Lists.newArrayList();
    for (ConnectionRead connection : connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody).getConnections()) {
      reads.add(buildWbConnectionRead(connection));
    }
    return new WbConnectionReadList().connections(reads);
  }

  public WbConnectionRead webBackendGetConnection(ConnectionIdRequestBody connectionIdRequestBody)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return buildWbConnectionRead(connectionsHandler.getConnection(connectionIdRequestBody));
  }

  private WbConnectionRead buildWbConnectionRead(ConnectionRead connectionRead) throws ConfigNotFoundException, IOException, JsonValidationException {
    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody()
        .sourceId(connectionRead.getSourceId());
    final SourceRead source = sourceHandler.getSource(sourceIdRequestBody);

    final DestinationIdRequestBody destinationIdRequestBody = new DestinationIdRequestBody().destinationId(connectionRead.getDestinationId());
    final DestinationRead destination = destinationHandler.getDestination(destinationIdRequestBody);

    final JobListRequestBody jobListRequestBody = new JobListRequestBody()
        .configId(connectionRead.getConnectionId().toString())
        .configType(JobConfigType.SYNC);

    final WbConnectionRead wbConnectionRead = new WbConnectionRead()
        .connectionId(connectionRead.getConnectionId())
        .sourceId(connectionRead.getSourceId())
        .destinationId(connectionRead.getDestinationId())
        .name(connectionRead.getName())
        .syncSchema(connectionRead.getSyncSchema())
        .status(connectionRead.getStatus())
        .syncMode(Enums.convertTo(connectionRead.getSyncMode(), SyncMode.class))
        .schedule(connectionRead.getSchedule())
        .source(source)
        .destination(destination);

    final JobReadList jobReadList = jobHistoryHandler.listJobsFor(jobListRequestBody);
    wbConnectionRead.setIsSyncing(
        jobReadList.getJobs().stream().anyMatch(job -> job.getStatus() != JobStatus.COMPLETED && job.getStatus() != JobStatus.CANCELLED));
    jobReadList.getJobs().stream().findFirst().ifPresent(job -> wbConnectionRead.setLastSync(job.getCreatedAt()));

    return wbConnectionRead;
  }

}
