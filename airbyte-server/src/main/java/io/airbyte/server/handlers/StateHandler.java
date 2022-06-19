package io.airbyte.server.handlers;

import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.ConnectionState;
import io.airbyte.api.model.generated.ConnectionStateType;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.State;
import io.airbyte.config.persistence.ConfigRepository;
import java.io.IOException;
import java.util.Optional;

public class StateHandler {
  private final ConfigRepository configRepository;

  public StateHandler(final ConfigRepository configRepository) {
    this.configRepository = configRepository;
  }

  public ConnectionState getState(final ConnectionIdRequestBody connectionIdRequestBody) throws IOException {
    final Optional<State> currentState = configRepository.getConnectionState(connectionIdRequestBody.getConnectionId());

    final ConnectionState connectionState = new ConnectionState()
        .connectionId(connectionIdRequestBody.getConnectionId());

    currentState.ifPresent(state -> connectionState.state(state.getState()));

    return connectionState;
  }

  public ConnectionStateType getStateType(final ConnectionIdRequestBody connectionIdRequestBody) throws IOException {
    return Enums.convertTo(getState(connectionIdRequestBody).getStateType(), ConnectionStateType.class);
  }
}
