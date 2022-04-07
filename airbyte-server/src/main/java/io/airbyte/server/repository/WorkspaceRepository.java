package io.airbyte.server.repository;

import io.airbyte.server.model.Workspace;
import io.micronaut.data.annotation.Repository;
import io.micronaut.data.repository.CrudRepository;
import java.util.UUID;

@Repository
public interface WorkspaceRepository extends CrudRepository<Workspace, UUID> {

}
