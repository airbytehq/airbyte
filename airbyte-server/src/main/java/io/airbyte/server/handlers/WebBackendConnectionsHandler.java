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
import io.airbyte.api.model.JobConfigType;
import io.airbyte.api.model.JobListRequestBody;
import io.airbyte.api.model.JobReadList;
import io.airbyte.api.model.SourceImplementationIdRequestBody;
import io.airbyte.api.model.SourceImplementationRead;
import io.airbyte.api.model.WbConnectionRead;
import io.airbyte.api.model.WbConnectionReadList;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.JsonValidationException;
import io.airbyte.config.persistence.ConfigNotFoundException;
import java.io.IOException;
import java.util.List;

public class WebBackendConnectionsHandler {

  private final ConnectionsHandler connectionsHandler;
  private final SourceImplementationsHandler sourceImplementationsHandler;
  private final JobHistoryHandler jobHistoryHandler;

  public WebBackendConnectionsHandler(final ConnectionsHandler connectionsHandler,
                                      final SourceImplementationsHandler sourceImplementationsHandler,
                                      final JobHistoryHandler jobHistoryHandler) {
    this.connectionsHandler = connectionsHandler;
    this.sourceImplementationsHandler = sourceImplementationsHandler;
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
    final SourceImplementationIdRequestBody sourceImplementationIdRequestBody = new SourceImplementationIdRequestBody()
        .sourceImplementationId(connectionRead.getSourceImplementationId());
    final SourceImplementationRead sourceImplementation = sourceImplementationsHandler.getSourceImplementation(sourceImplementationIdRequestBody);

    final JobListRequestBody jobListRequestBody = new JobListRequestBody()
        .configId(connectionRead.getConnectionId().toString())
        .configType(JobConfigType.SYNC);

    final WbConnectionRead wbConnectionRead = new WbConnectionRead()
        .connectionId(connectionRead.getConnectionId())
        .sourceImplementationId(connectionRead.getSourceImplementationId())
        .destinationImplementationId(connectionRead.getDestinationImplementationId())
        .name(connectionRead.getName())
        .syncSchema(connectionRead.getSyncSchema())
        .status(connectionRead.getStatus())
        .syncMode(Enums.convertTo(connectionRead.getSyncMode(), WbConnectionRead.SyncModeEnum.class))
        .schedule(connectionRead.getSchedule())
        .source(sourceImplementation);

    final JobReadList jobReadList = jobHistoryHandler.listJobsFor(jobListRequestBody);
    jobReadList.getJobs().stream().findFirst().ifPresent(job -> wbConnectionRead.setLastSync(job.getCreatedAt()));

    return wbConnectionRead;
  }

}
