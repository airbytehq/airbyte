/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.ConnectionState;
import io.airbyte.api.model.generated.ConnectionStateCreateOrUpdate;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.workers.helper.StateConverter;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.util.Optional;
import java.util.UUID;

@Singleton
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

  public ConnectionState createOrUpdateState(final ConnectionStateCreateOrUpdate connectionStateCreateOrUpdate) throws IOException {
    final UUID connectionId = connectionStateCreateOrUpdate.getConnectionId();

    final StateWrapper convertedCreateOrUpdate = StateConverter.toInternal(connectionStateCreateOrUpdate.getConnectionState());
    statePersistence.updateOrCreateState(connectionId, convertedCreateOrUpdate);
    final Optional<StateWrapper> newInternalState = statePersistence.getCurrentState(connectionId);

    return StateConverter.toApi(connectionId, newInternalState.orElse(null));
  }

}
