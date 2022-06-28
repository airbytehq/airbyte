/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.ConnectionState;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.server.converters.StateConverter;
import java.io.IOException;
import java.util.Optional;
import java.util.UUID;

public class StateHandler {

  private final StatePersistence statePersistence;

  public StateHandler(final StatePersistence statePersistence) {
    this.statePersistence = statePersistence;
  }

  public ConnectionState getState(final ConnectionIdRequestBody connectionIdRequestBody) throws IOException {
    final UUID connectionId = connectionIdRequestBody.getConnectionId();
    final Optional<StateWrapper> currentState = statePersistence.getCurrentState(connectionId);
    return StateConverter.toApi(connectionId, currentState.orElse(null));
  }

}
