/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import io.airbyte.api.model.generated.ConnectionState;
import io.airbyte.api.model.generated.ConnectionStateType;
import io.airbyte.api.model.generated.GlobalState;
import io.airbyte.api.model.generated.StreamState;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.StateType;
import io.airbyte.config.StateWrapper;
import io.airbyte.protocol.models.AirbyteGlobalState;
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
        .stateType(convertStateTypeToApi(stateWrapper))
        .state(stateWrapper != null ? stateWrapper.getLegacyState() : null)
        .globalState(globalStateToApi(stateWrapper).orElse(null))
        .streamState(streamStateToApi(stateWrapper).orElse(null));
  }

  /**
   * Converts internal representation of state to client representation
   *
   * @param connectionId connection associated with the state
   * @param stateWrapper internal state representation to convert
   * @return client representation of state
   */
  public static io.airbyte.api.client.model.generated.ConnectionState toClient(final UUID connectionId, final @Nullable StateWrapper stateWrapper) {
    return new io.airbyte.api.client.model.generated.ConnectionState()
        .connectionId(connectionId)
        .stateType(convertStateTypeToClient(stateWrapper))
        .state(stateWrapper != null ? stateWrapper.getLegacyState() : null)
        .globalState(globalStateToClient(stateWrapper).orElse(null))
        .streamState(streamStateToClient(stateWrapper).orElse(null));
  }

  /**
   * Converts API representation of state to internal representation
   *
   * @param apiConnectionState api representation of state
   * @return internal representation of state
   */
  public static StateWrapper toInternal(final @Nullable ConnectionState apiConnectionState) {
    return new StateWrapper()
        .withStateType(convertStateTypeToInternal(apiConnectionState).orElse(null))
        .withGlobal(globalStateToInternal(apiConnectionState).orElse(null))
        .withLegacyState(apiConnectionState != null ? apiConnectionState.getState() : null)
        .withStateMessages(streamStateToInternal(apiConnectionState).orElse(null));

  }

  public static StateType convertClientStateTypeToInternal(final @Nullable io.airbyte.api.client.model.generated.ConnectionStateType connectionStateType) {
    if (connectionStateType == null || connectionStateType.equals(io.airbyte.api.client.model.generated.ConnectionStateType.NOT_SET)) {
      return null;
    } else {
      return Enums.convertTo(connectionStateType, StateType.class);
    }
  }

  /**
   * Convert to API representation of state type. API has an additional type (NOT_SET). This
   * represents the case where no state is saved so we do not know the state type.
   *
   * @param stateWrapper state to convert
   * @return api representation of state type
   */
  private static ConnectionStateType convertStateTypeToApi(final @Nullable StateWrapper stateWrapper) {
    if (stateWrapper == null || stateWrapper.getStateType() == null) {
      return ConnectionStateType.NOT_SET;
    } else {
      return Enums.convertTo(stateWrapper.getStateType(), ConnectionStateType.class);
    }
  }

  /**
   * Convert to client representation of state type. The client model has an additional type
   * (NOT_SET). This represents the case where no state is saved so we do not know the state type.
   *
   * @param stateWrapper state to convert
   * @return client representation of state type
   */
  private static io.airbyte.api.client.model.generated.ConnectionStateType convertStateTypeToClient(final @Nullable StateWrapper stateWrapper) {
    if (stateWrapper == null || stateWrapper.getStateType() == null) {
      return io.airbyte.api.client.model.generated.ConnectionStateType.NOT_SET;
    } else {
      return Enums.convertTo(stateWrapper.getStateType(), io.airbyte.api.client.model.generated.ConnectionStateType.class);
    }
  }

  /**
   * Convert to internal representation of state type, if set. Otherise, empty optional
   *
   * @param connectionState API state to convert.
   * @return internal state type, if set. Otherwise, empty optional.
   */
  private static Optional<StateType> convertStateTypeToInternal(final @Nullable ConnectionState connectionState) {
    if (connectionState == null || connectionState.getStateType().equals(ConnectionStateType.NOT_SET)) {
      return Optional.empty();
    } else {
      return Optional.of(Enums.convertTo(connectionState.getStateType(), StateType.class));
    }
  }

  /**
   * If wrapper is of type global state, returns API representation of global state. Otherwise, empty
   * optional.
   *
   * @param stateWrapper state wrapper to extract from
   * @return api representation of global state if state wrapper is type global. Otherwise, empty
   *         optional.
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
   * If wrapper is of type global state, returns client representation of global state. Otherwise,
   * empty optional.
   *
   * @param stateWrapper state wrapper to extract from
   * @return client representation of global state if state wrapper is type global. Otherwise, empty
   *         optional.
   */
  private static Optional<io.airbyte.api.client.model.generated.GlobalState> globalStateToClient(final @Nullable StateWrapper stateWrapper) {
    if (stateWrapper != null
        && stateWrapper.getStateType() == StateType.GLOBAL
        && stateWrapper.getGlobal() != null
        && stateWrapper.getGlobal().getGlobal() != null) {
      return Optional.of(new io.airbyte.api.client.model.generated.GlobalState()
          .sharedState(stateWrapper.getGlobal().getGlobal().getSharedState())
          .streamStates(stateWrapper.getGlobal().getGlobal().getStreamStates()
              .stream()
              .map(StateConverter::streamStateStructToClient)
              .toList()));
    } else {
      return Optional.empty();
    }
  }

  /**
   * If API state is of type global, returns internal representation of global state. Otherwise, empty
   * optional.
   *
   * @param connectionState API state representation to extract from
   * @return global state message if API state is of type global. Otherwise, empty optional.
   */
  private static Optional<AirbyteStateMessage> globalStateToInternal(final @Nullable ConnectionState connectionState) {
    if (connectionState != null
        && connectionState.getStateType() == ConnectionStateType.GLOBAL
        && connectionState.getGlobalState() != null) {
      return Optional.of(new AirbyteStateMessage()
          .withGlobal(new AirbyteGlobalState()
              .withSharedState(connectionState.getGlobalState().getSharedState())
              .withStreamStates(connectionState.getGlobalState().getStreamStates()
                  .stream()
                  .map(StateConverter::streamStateStructToInternal)
                  .toList())));
    } else {
      return Optional.empty();
    }
  }

  /**
   * If wrapper is of type stream state, returns API representation of stream state. Otherwise, empty
   * optional.
   *
   * @param stateWrapper state wrapper to extract from
   * @return api representation of stream state if state wrapper is type stream. Otherwise, empty
   *         optional.
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

  /**
   * If wrapper is of type stream state, returns client representation of stream state. Otherwise,
   * empty optional.
   *
   * @param stateWrapper state wrapper to extract from
   * @return client representation of stream state if state wrapper is type stream. Otherwise, empty
   *         optional.
   */
  private static Optional<List<io.airbyte.api.client.model.generated.StreamState>> streamStateToClient(final @Nullable StateWrapper stateWrapper) {
    if (stateWrapper != null && stateWrapper.getStateType() == StateType.STREAM && stateWrapper.getStateMessages() != null) {
      return Optional.ofNullable(stateWrapper.getStateMessages()
          .stream()
          .map(AirbyteStateMessage::getStream)
          .map(StateConverter::streamStateStructToClient)
          .toList());
    } else {
      return Optional.empty();
    }
  }

  /**
   * If API state is of type stream, returns internal representation of stream state. Otherwise, empty
   * optional.
   *
   * @param connectionState API representation of state to extract from
   * @return internal representation of stream state if API state representation is of type stream.
   *         Otherwise, empty optional.
   */
  private static Optional<List<AirbyteStateMessage>> streamStateToInternal(final @Nullable ConnectionState connectionState) {
    if (connectionState != null && connectionState.getStateType() == ConnectionStateType.STREAM && connectionState.getStreamState() != null) {
      return Optional.ofNullable(connectionState.getStreamState()
          .stream()
          .map(StateConverter::streamStateStructToInternal)
          .map(s -> new AirbyteStateMessage().withStream(s))
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

  private static io.airbyte.api.client.model.generated.StreamState streamStateStructToClient(final AirbyteStreamState streamState) {
    return new io.airbyte.api.client.model.generated.StreamState()
        .streamDescriptor(ProtocolConverters.streamDescriptorToClient(streamState.getStreamDescriptor()))
        .streamState(streamState.getStreamState());
  }

  private static AirbyteStreamState streamStateStructToInternal(final StreamState streamState) {
    return new AirbyteStreamState()
        .withStreamDescriptor(ProtocolConverters.streamDescriptorToProtocol(streamState.getStreamDescriptor()))
        .withStreamState(streamState.getStreamState());
  }

}
