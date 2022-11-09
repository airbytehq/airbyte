/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.api.server.repositories;

import io.airbyte.public_api.server.model.generated.Connection;
import io.micronaut.data.repository.GenericRepository;
import java.util.UUID;

public interface ConnectionsRepository extends GenericRepository<Connection, UUID> {

  void sync(UUID connectionId, String xEndpointAPIUserInfo);

  void reset(UUID connectionId);

}
