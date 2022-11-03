/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.api.server.repositories;

import io.airbyte.api.server.model.generated.Connection;
import io.micronaut.data.repository.GenericRepository;
import io.micronaut.http.HttpResponse;
import java.util.UUID;

public interface ConnectionsRepository extends GenericRepository<Connection, UUID> {

  HttpResponse<String> sync(UUID connection, String authorization);

  HttpResponse<String> reset(UUID connection);

}
