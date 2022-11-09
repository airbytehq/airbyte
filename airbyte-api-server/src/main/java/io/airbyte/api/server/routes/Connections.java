/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.api.server.routes;

import io.airbyte.api.server.forwardingClient.InternalApiWrapper;
import io.airbyte.api.server.repositories.ConnectionsRepository;
import io.airbyte.public_api.server.generated.ConnectionApi;
import io.airbyte.public_api.server.model.generated.Connection;
import io.airbyte.public_api.server.model.generated.ConnectionCreate;
import io.airbyte.public_api.server.model.generated.ConnectionList;
import io.airbyte.public_api.server.model.generated.Identifier;
import io.micronaut.http.annotation.Controller;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;

@Controller("/connections")
@Slf4j
public class Connections implements ConnectionApi {

  // unused for now as the api-server does not currently touch underlying data sources
  final ConnectionsRepository connectionsRepository;
  final InternalApiWrapper internalApiWrapper;

  Connections(final ConnectionsRepository connectionsRepository, final InternalApiWrapper internalApiWrapper) {
    this.connectionsRepository = connectionsRepository;
    this.internalApiWrapper = internalApiWrapper;
  }

  @Override
  public Connection createConnection(final ConnectionCreate connectionCreate) {
    return null;
  }

  @Override
  public ConnectionList listConnectionsForWorkspace(final Identifier identifiers, final UUID workspaceId, final String slug, final String cursor) {
    return null;
  }

  @Override
  public void resetConnection(final UUID connectionId) {
    internalApiWrapper.reset(connectionId);
  }

  @Override
  public void syncConnection(final UUID connectionId, final String xEndpointAPIUserInfo) {
    internalApiWrapper.sync(connectionId, xEndpointAPIUserInfo);
  }

}
