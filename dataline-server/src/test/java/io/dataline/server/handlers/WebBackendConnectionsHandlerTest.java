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

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.dataline.api.model.ConnectionIdRequestBody;
import io.dataline.api.model.ConnectionRead;
import io.dataline.api.model.ConnectionReadList;
import io.dataline.api.model.JobConfigType;
import io.dataline.api.model.JobListRequestBody;
import io.dataline.api.model.JobRead;
import io.dataline.api.model.JobReadList;
import io.dataline.api.model.SourceImplementationIdRequestBody;
import io.dataline.api.model.SourceImplementationRead;
import io.dataline.api.model.WbConnectionRead;
import io.dataline.api.model.WbConnectionReadList;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.commons.enums.Enums;
import io.dataline.commons.json.JsonValidationException;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSource;
import io.dataline.config.StandardSync;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.server.helpers.ConnectionHelpers;
import io.dataline.server.helpers.SourceHelpers;
import io.dataline.server.helpers.SourceImplementationHelpers;
import java.io.IOException;
import java.time.Instant;
import java.util.Collections;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class WebBackendConnectionsHandlerTest {

  private ConnectionsHandler connectionsHandler;
  private WebBackendConnectionsHandler wbHandler;

  private SourceImplementationRead sourceImplementationRead;
  private ConnectionRead connectionRead;
  private WbConnectionRead expected;

  @BeforeEach
  public void setup() throws IOException, JsonValidationException, ConfigNotFoundException {
    connectionsHandler = mock(ConnectionsHandler.class);
    SourceImplementationsHandler sourceImplementationsHandler = mock(SourceImplementationsHandler.class);
    JobHistoryHandler jobHistoryHandler = mock(JobHistoryHandler.class);
    wbHandler = new WebBackendConnectionsHandler(connectionsHandler, sourceImplementationsHandler, jobHistoryHandler);

    final StandardSource standardSource = SourceHelpers.generateSource();
    SourceConnectionImplementation sourceImplementation = SourceImplementationHelpers.generateSourceImplementation(UUID.randomUUID());
    sourceImplementationRead = SourceImplementationHelpers.getSourceImplementationRead(sourceImplementation, standardSource);

    final StandardSync standardSync = ConnectionHelpers.generateSync(sourceImplementation.getSourceImplementationId());
    connectionRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync);

    final SourceImplementationIdRequestBody sourceImplementationIdRequestBody = new SourceImplementationIdRequestBody();
    sourceImplementationIdRequestBody.setSourceImplementationId(connectionRead.getSourceImplementationId());
    when(sourceImplementationsHandler.getSourceImplementation(sourceImplementationIdRequestBody)).thenReturn(sourceImplementationRead);

    Instant now = Instant.now();
    final JobRead jobRead = new JobRead();
    jobRead.setConfigId(connectionRead.getConnectionId().toString());
    jobRead.setConfigType(JobConfigType.SYNC);
    jobRead.setId(10L);
    jobRead.setStatus(JobRead.StatusEnum.COMPLETED);
    jobRead.setCreatedAt(now.getEpochSecond());
    jobRead.setStartedAt(now.getEpochSecond());
    jobRead.setUpdatedAt(now.getEpochSecond());

    final JobReadList jobReadList = new JobReadList();
    jobReadList.setJobs(Collections.singletonList(jobRead));
    final JobListRequestBody jobListRequestBody = new JobListRequestBody();
    jobListRequestBody.setConfigType(JobConfigType.SYNC);
    jobListRequestBody.setConfigId(connectionRead.getConnectionId().toString());
    when(jobHistoryHandler.listJobsFor(jobListRequestBody)).thenReturn(jobReadList);

    expected = new WbConnectionRead();
    expected.setConnectionId(connectionRead.getConnectionId());
    expected.setSourceImplementationId(connectionRead.getSourceImplementationId());
    expected.setDestinationImplementationId(connectionRead.getDestinationImplementationId());
    expected.setName(connectionRead.getName());
    expected.setSyncSchema(connectionRead.getSyncSchema());
    expected.setStatus(connectionRead.getStatus());
    expected.setSyncMode(Enums.convertTo(connectionRead.getSyncMode(), WbConnectionRead.SyncModeEnum.class));
    expected.setSchedule(connectionRead.getSchedule());
    expected.setSource(this.sourceImplementationRead);
    expected.setLastSync(now.getEpochSecond());
  }

  @Test
  public void testWebBackendListConnectionsForWorkspace() throws ConfigNotFoundException, IOException, JsonValidationException {
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody();
    workspaceIdRequestBody.setWorkspaceId(sourceImplementationRead.getWorkspaceId());

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

    when(connectionsHandler.getConnection(connectionIdRequestBody)).thenReturn(connectionRead);

    final WbConnectionRead wbConnectionRead = wbHandler.webBackendGetConnection(connectionIdRequestBody);

    assertEquals(expected, wbConnectionRead);
  }

  @Test
  public void testEnumConversion() {
    assertTrue(Enums.isCompatible(ConnectionRead.SyncModeEnum.class, WbConnectionRead.SyncModeEnum.class));
  }

}
