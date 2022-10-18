package io.airbyte.api.server.repositories.impl;

import io.airbyte.api.server.repositories.ConnectionsRepository;

import jakarta.inject.Singleton;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;

@Singleton
@Slf4j
public class ConnectionsRepositoryRESTImpl implements ConnectionsRepository {
    final String configServerUrl = "localhost:8080"; // TODO: Use the property
    @Override
    public void sync(final UUID connection) {
        // POST to Config API
        log.info("test: ConnectionsRepositoryRESTImpl");
    }

    @Override
    public void reset(final UUID connection) {
        // POST to Config API
    }
}
