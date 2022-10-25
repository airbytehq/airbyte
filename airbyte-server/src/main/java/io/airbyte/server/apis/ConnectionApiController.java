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
import io.airbyte.api.model.generated.ConnectionState;
import io.airbyte.api.model.generated.ConnectionStateCreateOrUpdate;
import io.airbyte.api.model.generated.ConnectionStateType;
import io.airbyte.api.model.generated.ConnectionUpdate;
import io.airbyte.api.model.generated.JobInfoRead;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.server.handlers.ConnectionsHandler;
import io.airbyte.server.handlers.OperationsHandler;
import io.airbyte.server.handlers.SchedulerHandler;
import io.airbyte.server.handlers.StateHandler;
import io.airbyte.server.handlers.WebBackendConnectionsHandler;

public class ConnectionApiController implements ConnectionApi {

  private final ConnectionsHandler connectionsHandler;
  private final OperationsHandler operationsHandler;
  private final SchedulerHandler schedulerHandler;
  private final StateHandler stateHandler;
  private final WebBackendConnectionsHandler webBackendConnectionsHandler;

  public ConnectionApiController(final ConnectionsHandler connectionsHandler,
                                 final OperationsHandler operationsHandler,
                                 final SchedulerHandler schedulerHandler,
                                 final StateHandler stateHandler,
                                 final WebBackendConnectionsHandler webBackendConnectionsHandler) {
    this.connectionsHandler = connectionsHandler;
    this.operationsHandler = operationsHandler;
    this.schedulerHandler = schedulerHandler;
    this.stateHandler = stateHandler;
    this.webBackendConnectionsHandler = webBackendConnectionsHandler;
  }

  @Override
  public ConnectionRead createConnection(final ConnectionCreate connectionCreate) {
    return ConfigurationApi.execute(() -> connectionsHandler.createConnection(connectionCreate));
  }

  @Override
  public ConnectionState createOrUpdateState(final ConnectionStateCreateOrUpdate connectionStateCreateOrUpdate) {
    return ConfigurationApi.execute(() -> stateHandler.createOrUpdateState(connectionStateCreateOrUpdate));
  }

  @Override
  public ConnectionRead updateConnection(final ConnectionUpdate connectionUpdate) {
    return ConfigurationApi.execute(() -> connectionsHandler.updateConnection(connectionUpdate));
  }

  @Override
  public ConnectionReadList listConnectionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ConfigurationApi.execute(() -> connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public ConnectionReadList listAllConnectionsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ConfigurationApi.execute(() -> connectionsHandler.listAllConnectionsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public ConnectionReadList searchConnections(final ConnectionSearch connectionSearch) {
    return ConfigurationApi.execute(() -> connectionsHandler.searchConnections(connectionSearch));
  }

  @Override
  public ConnectionRead getConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    return ConfigurationApi.execute(() -> connectionsHandler.getConnection(connectionIdRequestBody.getConnectionId()));
  }

  @Override
  public ConnectionState getState(final ConnectionIdRequestBody connectionIdRequestBody) {
    return ConfigurationApi.execute(() -> stateHandler.getState(connectionIdRequestBody));
  }

  @Override
  public ConnectionStateType getStateType(final ConnectionIdRequestBody connectionIdRequestBody) {
    // TODO: move to connectionHandler
    return ConfigurationApi.execute(() -> webBackendConnectionsHandler.getStateType(connectionIdRequestBody));
  }

  @Override
  public void deleteConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    ConfigurationApi.execute(() -> {
      operationsHandler.deleteOperationsForConnection(connectionIdRequestBody);
      connectionsHandler.deleteConnection(connectionIdRequestBody.getConnectionId());
      return null;
    });
  }

  @Override
  public JobInfoRead syncConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    return ConfigurationApi.execute(() -> schedulerHandler.syncConnection(connectionIdRequestBody));
  }

  @Override
  public JobInfoRead resetConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    return ConfigurationApi.execute(() -> schedulerHandler.resetConnection(connectionIdRequestBody));
  }

}
