package io.airbyte.api.server.repositories;


import jakarta.inject.Singleton;

import java.util.UUID;

@Singleton
public interface ConnectionsRepository {
    void sync(UUID connection);
    void reset(UUID connection);
}
