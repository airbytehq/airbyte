package io.airbyte.api.server.routes;

import io.airbyte.api.server.generated.ConnectionApi;
import io.airbyte.api.server.model.generated.Connection;
import io.airbyte.api.server.model.generated.ConnectionCreate;
import io.airbyte.api.server.model.generated.ConnectionList;
import io.airbyte.api.server.model.generated.Identifier;
import io.airbyte.api.server.repositories.ConnectionsRepository;

import javax.ws.rs.Path;
import java.util.UUID;


@Path("/connections")
public class Connections implements ConnectionApi {

    final ConnectionsRepository connectionsRepository;

    Connections(ConnectionsRepository connectionsRepository) {
        this.connectionsRepository = connectionsRepository;
    }

    @Override
    public Connection createConnection(ConnectionCreate connectionCreate) {
        return null;
    }

    @Override
    public ConnectionList listConnectionsForWorkspace(Identifier identifiers, UUID workspaceId, String slug, String cursor) {
        return null;
    }

    @Override
    public void resetConnection(UUID connectionId) {
        connectionsRepository.reset(connectionId);
    }

    @Override
    public void syncConnection(UUID connectionId) {
        connectionsRepository.sync(connectionId);
    }
}
