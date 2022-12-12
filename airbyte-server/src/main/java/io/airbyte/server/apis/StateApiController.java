/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.StateApi;
import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.ConnectionState;
import io.airbyte.api.model.generated.ConnectionStateCreateOrUpdate;
import io.airbyte.server.handlers.StateHandler;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;

@Controller("/api/v1/state")
public class StateApiController implements StateApi {

  private final StateHandler stateHandler;

  public StateApiController(final StateHandler stateHandler) {
    this.stateHandler = stateHandler;
  }

  @Post("/create_or_update")
  @Override
  public ConnectionState createOrUpdateState(final ConnectionStateCreateOrUpdate connectionStateCreateOrUpdate) {
    return ApiHelper.execute(() -> stateHandler.createOrUpdateState(connectionStateCreateOrUpdate));
  }

  @Post("/get")
  @Override
  public ConnectionState getState(final ConnectionIdRequestBody connectionIdRequestBody) {
    return ApiHelper.execute(() -> stateHandler.getState(connectionIdRequestBody));
  }

}
