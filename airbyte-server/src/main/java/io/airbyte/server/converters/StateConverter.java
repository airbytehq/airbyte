/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import io.airbyte.api.model.generated.ConnectionState;
import io.airbyte.api.model.generated.ConnectionStateType;
import io.airbyte.api.model.generated.GlobalState;
import io.airbyte.api.model.generated.StreamState;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.StateType;
import io.airbyte.config.StateWrapper;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStreamState;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import javax.annotation.Nullable;

public class StateConverter {

  /**
   * Converts internal representation of state to API representation
   *
   * @param connectionId connection associated with the state
   * @param stateWrapper internal state representation to convert
   * @return api representation of state
   */
  public static ConnectionState toApi(final UUID connectionId, final @Nullable StateWrapper stateWrapper) {
    return new ConnectionState()
        .connectionId(connectionId)
        .stateType(convertStateType(stateWrapper))
        .state(stateWrapper != null ? stateWrapper.getLegacyState() : null)
        .globalState(globalStateToApi(stateWrapper).orElse(null))
        .streamState(streamStateToApi(stateWrapper).orElse(null));
  }

  /**
   * Convert to API representation of state type. API has an additional type (NOT_SET). This
   * represents the case where no state is saved so we do not know the state type.
   *
   * @param stateWrapper state to convert
   * @return api representation of state type
   */
  private static ConnectionStateType convertStateType(final @Nullable StateWrapper stateWrapper) {
    if (stateWrapper == null || stateWrapper.getStateType() == null) {
      return ConnectionStateType.NOT_SET;
    } else {
      return Enums.convertTo(stateWrapper.getStateType(), ConnectionStateType.class);
    }
  }

  /**
   * If wrapper is of type global state, returns global state. Otherwise, empty optional.
   *
   * @param stateWrapper state wrapper to extract from
   * @return global state if state wrapper is type global. Otherwise, empty optional.
   */
  private static Optional<GlobalState> globalStateToApi(final @Nullable StateWrapper stateWrapper) {
    if (stateWrapper != null
        && stateWrapper.getStateType() == StateType.GLOBAL
        && stateWrapper.getGlobal() != null
        && stateWrapper.getGlobal().getGlobal() != null) {
      return Optional.of(new GlobalState()
          .sharedState(stateWrapper.getGlobal().getGlobal().getSharedState())
          .streamStates(stateWrapper.getGlobal().getGlobal().getStreamStates()
              .stream()
              .map(StateConverter::streamStateStructToApi)
              .toList()));
    } else {
      return Optional.empty();
    }
  }

  /**
   * If wrapper is of type stream state, returns stream state. Otherwise, empty optional.
   *
   * @param stateWrapper state wrapper to extract from
   * @return stream state if state wrapper is type stream. Otherwise, empty optional.
   */
  private static Optional<List<StreamState>> streamStateToApi(final @Nullable StateWrapper stateWrapper) {
    if (stateWrapper != null && stateWrapper.getStateType() == StateType.STREAM && stateWrapper.getStateMessages() != null) {
      return Optional.ofNullable(stateWrapper.getStateMessages()
          .stream()
          .map(AirbyteStateMessage::getStream)
          .map(StateConverter::streamStateStructToApi)
          .toList());
    } else {
      return Optional.empty();
    }
  }

  private static StreamState streamStateStructToApi(final AirbyteStreamState streamState) {
    return new StreamState()
        .streamDescriptor(ProtocolConverters.streamDescriptorToApi(streamState.getStreamDescriptor()))
        .streamState(streamState.getStreamState());
  }

}
