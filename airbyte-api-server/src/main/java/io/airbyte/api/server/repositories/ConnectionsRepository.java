package io.airbyte.api.server.repositories;

import io.airbyte.api.server.model.generated.Connection;
import io.micronaut.data.repository.GenericRepository;
import java.util.UUID;

public interface ConnectionsRepository extends GenericRepository<Connection, UUID> {
    void sync(UUID connection);
    void reset(UUID connection);
}
