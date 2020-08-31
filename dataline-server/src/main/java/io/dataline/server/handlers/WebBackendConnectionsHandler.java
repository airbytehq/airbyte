/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.server.handlers;

import io.dataline.api.model.ConnectionReadList;
import io.dataline.api.model.JobConfigType;
import io.dataline.api.model.JobListRequestBody;
import io.dataline.api.model.JobReadList;
import io.dataline.api.model.SourceImplementationIdRequestBody;
import io.dataline.api.model.SourceImplementationRead;
import io.dataline.api.model.WbConnectionRead;
import io.dataline.api.model.WbConnectionReadList;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.commons.enums.Enums;
import java.util.List;
import java.util.stream.Collectors;

public class WebBackendConnectionsHandler {

  private final ConnectionsHandler connectionsHandler;
  private final SourceImplementationsHandler sourceImplementationsHandler;
  private final JobHistoryHandler jobHistoryHandler;

  public WebBackendConnectionsHandler(
      ConnectionsHandler connectionsHandler,
      SourceImplementationsHandler sourceImplementationsHandler,
      JobHistoryHandler jobHistoryHandler) {
    this.connectionsHandler = connectionsHandler;
    this.sourceImplementationsHandler = sourceImplementationsHandler;
    this.jobHistoryHandler = jobHistoryHandler;
  }

  public WbConnectionReadList webBackendListConnectionsForWorkspace(
      WorkspaceIdRequestBody workspaceIdRequestBody) {
    final ConnectionReadList connectionReadList =
        connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody);

    final List<WbConnectionRead> reads =
        connectionReadList.getConnections().stream()
            .map(
                connectionRead -> {
                  final SourceImplementationIdRequestBody sourceImplementationIdRequestBody =
                      new SourceImplementationIdRequestBody();
                  sourceImplementationIdRequestBody.setSourceImplementationId(
                      connectionRead.getSourceImplementationId());
                  final SourceImplementationRead sourceImplementation =
                      sourceImplementationsHandler.getSourceImplementation(
                          sourceImplementationIdRequestBody);

                  final JobListRequestBody jobListRequestBody = new JobListRequestBody();
                  jobListRequestBody.setConfigId(connectionRead.getConnectionId().toString());
                  jobListRequestBody.setConfigType(JobConfigType.SYNC);
                  final JobReadList jobReadList = jobHistoryHandler.listJobsFor(jobListRequestBody);

                  final WbConnectionRead wbConnectionRead = new WbConnectionRead();
                  wbConnectionRead.setConnectionId(connectionRead.getConnectionId());
                  wbConnectionRead.setSourceImplementationId(
                      connectionRead.getSourceImplementationId());
                  wbConnectionRead.setDestinationImplementationId(
                      connectionRead.getDestinationImplementationId());
                  wbConnectionRead.setName(connectionRead.getName());
                  wbConnectionRead.setSyncSchema(connectionRead.getSyncSchema());
                  wbConnectionRead.setStatus(connectionRead.getStatus());
                  wbConnectionRead.setSyncMode(
                      Enums.convertTo(
                          connectionRead.getSyncMode(), WbConnectionRead.SyncModeEnum.class));
                  wbConnectionRead.setSchedule(connectionRead.getSchedule());
                  jobReadList.getJobs().stream()
                      .findFirst()
                      .ifPresent(job -> wbConnectionRead.setLastSync(job.getCreatedAt()));

                  wbConnectionRead.setSource(sourceImplementation);

                  return wbConnectionRead;
                })
            .collect(Collectors.toList());

    final WbConnectionReadList readList = new WbConnectionReadList();
    readList.setConnections(reads);

    return readList;
  }

}
