package io.airbyte.db.repositories.repositories;

import io.airbyte.db.repositories.models.StandardSyncModel;
import io.micronaut.data.annotation.Repository;
import io.micronaut.data.repository.PageableRepository;

import java.util.UUID;

@Repository
public interface StandardSyncRepository extends PageableRepository<StandardSyncModel, UUID> {
}
