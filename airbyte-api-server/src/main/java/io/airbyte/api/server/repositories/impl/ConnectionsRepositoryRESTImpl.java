/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.api.server.repositories.impl;

import io.airbyte.api.server.repositories.ConnectionsRepository;
import io.airbyte.api.server.repositories.clients.ConfigApiClient;
import io.airbyte.api.server.repositories.clients.SyncDto;
import io.micronaut.data.annotation.Repository;
import io.micronaut.http.HttpResponse;
import java.util.UUID;
import javax.validation.constraints.NotBlank;
import lombok.extern.slf4j.Slf4j;

@Repository
@Slf4j
public class ConnectionsRepositoryRESTImpl implements ConnectionsRepository {

  private final ConfigApiClient client;

  public ConnectionsRepositoryRESTImpl(final ConfigApiClient client) {
    this.client = client;
  }

  @Override
  public HttpResponse<String> sync(@NotBlank final UUID connection, final String authorization) {
    final var syncDto = new SyncDto(connection.toString());
    return client.sync(syncDto, authorization);
  }

  @Override
  public HttpResponse<String> reset(@NotBlank final UUID connection) {
    // POST to Config API
    final var syncDto = new SyncDto(connection.toString());
    final HttpResponse<String> res = client.reset(syncDto);
    // log.info("HttpResponse body: " + res.body());
    log.info("HttpResponse status: " + res.getStatus());
    return res;
  }

}
