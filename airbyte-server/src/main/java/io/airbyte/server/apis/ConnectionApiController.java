/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.ConnectionApi;
import io.airbyte.api.model.generated.ConnectionCreate;
import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.ConnectionRead;
import io.airbyte.api.model.generated.ConnectionReadList;
import io.airbyte.api.model.generated.ConnectionSearch;
import io.airbyte.api.model.generated.ConnectionUpdate;
import io.airbyte.api.model.generated.JobInfoRead;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.server.handlers.ConnectionsHandler;
import io.airbyte.server.handlers.OperationsHandler;
import io.airbyte.server.handlers.SchedulerHandler;
import io.micronaut.context.annotation.Context;
import io.micronaut.http.annotation.Body;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;

@Controller("/api/v1/connections")
@Context()
public class ConnectionApiController implements ConnectionApi {

  private final ConnectionsHandler connectionsHandler;
  private final OperationsHandler operationsHandler;
  private final SchedulerHandler schedulerHandler;

  public ConnectionApiController(final ConnectionsHandler connectionsHandler,
                                 final OperationsHandler operationsHandler,
                                 final SchedulerHandler schedulerHandler) {
    this.connectionsHandler = connectionsHandler;
    this.operationsHandler = operationsHandler;
    this.schedulerHandler = schedulerHandler;
  }

  @Override
  @Post(uri = "/create")
  public ConnectionRead createConnection(@Body final ConnectionCreate connectionCreate) {
    return ApiHelper.execute(() -> connectionsHandler.createConnection(connectionCreate));
  }

  @Override
  @Post(uri = "/update")
  public ConnectionRead updateConnection(@Body final ConnectionUpdate connectionUpdate) {
    return ApiHelper.execute(() -> connectionsHandler.updateConnection(connectionUpdate));
  }

  @Override
  @Post(uri = "/list")
  public ConnectionReadList listConnectionsForWorkspace(@Body final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  @Post(uri = "/list_all")
  public ConnectionReadList listAllConnectionsForWorkspace(@Body final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> connectionsHandler.listAllConnectionsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  @Post(uri = "/search")
  public ConnectionReadList searchConnections(@Body final ConnectionSearch connectionSearch) {
    return ApiHelper.execute(() -> connectionsHandler.searchConnections(connectionSearch));
  }

  @Override
  @Post(uri = "/get")
  public ConnectionRead getConnection(@Body final ConnectionIdRequestBody connectionIdRequestBody) {
    return ApiHelper.execute(() -> connectionsHandler.getConnection(connectionIdRequestBody.getConnectionId()));
  }

  @Override
  @Post(uri = "/delete")
  public void deleteConnection(@Body final ConnectionIdRequestBody connectionIdRequestBody) {
    ApiHelper.execute(() -> {
      operationsHandler.deleteOperationsForConnection(connectionIdRequestBody);
      connectionsHandler.deleteConnection(connectionIdRequestBody.getConnectionId());
      return null;
    });
  }

  @Override
  @Post(uri = "/sync")
  public JobInfoRead syncConnection(@Body final ConnectionIdRequestBody connectionIdRequestBody) {
    return ApiHelper.execute(() -> schedulerHandler.syncConnection(connectionIdRequestBody));
  }

  @Override
  @Post(uri = "/reset")
  public JobInfoRead resetConnection(@Body final ConnectionIdRequestBody connectionIdRequestBody) {
    return ApiHelper.execute(() -> schedulerHandler.resetConnection(connectionIdRequestBody));
  }

}
