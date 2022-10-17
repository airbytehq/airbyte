package io.airbyte.api.server.repositories.impl;

import io.airbyte.api.server.repositories.ConnectionsRepository;

import java.util.UUID;

public class ConnectionsRepositoryRESTImpl implements ConnectionsRepository {
    final String configServerUrl = "localhost:8080"; // TODO: Use the property
    @Override
    public void sync(UUID connection) {
        // POST to Config API

    }

    @Override
    public void reset(UUID connection) {
        // POST to Config API
    }
}
