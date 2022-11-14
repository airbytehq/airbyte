/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.StateApi;
import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.ConnectionState;
import io.airbyte.api.model.generated.ConnectionStateCreateOrUpdate;
import io.airbyte.server.handlers.StateHandler;
import javax.ws.rs.Path;
import lombok.AllArgsConstructor;

@Path("/v1/state")
@AllArgsConstructor
public class StateApiController implements StateApi {

  private final StateHandler stateHandler;

  @Override
  public ConnectionState createOrUpdateState(final ConnectionStateCreateOrUpdate connectionStateCreateOrUpdate) {
    return ConfigurationApi.execute(() -> stateHandler.createOrUpdateState(connectionStateCreateOrUpdate));
  }

  @Override
  public ConnectionState getState(final ConnectionIdRequestBody connectionIdRequestBody) {
    return ConfigurationApi.execute(() -> stateHandler.getState(connectionIdRequestBody));
  }

}
