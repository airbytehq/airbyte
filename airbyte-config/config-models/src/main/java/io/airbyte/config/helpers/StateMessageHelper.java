/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Iterables;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.State;
import io.airbyte.config.StateType;
import io.airbyte.config.StateWrapper;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import java.util.List;
import java.util.Optional;
import javax.annotation.Nullable;

public class StateMessageHelper {

  public static class AirbyteStateMessageListTypeReference extends TypeReference<List<AirbyteStateMessage>> {}

  /**
   * This a takes a json blob state and tries return either a legacy state in the format of a json
   * object or a state message with the new format which is a list of airbyte state message.
   *
   * @param state - a blob representing the state
   * @return An optional state wrapper, if there is no state an empty optional will be returned
   */
  @SuppressWarnings("PMD.AvoidLiteralsInIfCondition")
  public static Optional<StateWrapper> getTypedState(final JsonNode state, final boolean useStreamCapableState) {
    if (state == null) {
      return Optional.empty();
    } else {
      final List<AirbyteStateMessage> stateMessages;
      try {
        stateMessages = Jsons.object(state, new AirbyteStateMessageListTypeReference());
      } catch (final IllegalArgumentException e) {
        return Optional.of(getLegacyStateWrapper(state));
      }
      if (stateMessages.isEmpty()) {
        return Optional.empty();
      }

      if (stateMessages.size() == 1) {
        if (stateMessages.get(0).getType() == null) {
          return Optional.of(getLegacyStateWrapper(state));
        } else {
          switch (stateMessages.get(0).getType()) {
            case GLOBAL -> {
              return Optional.of(provideGlobalState(stateMessages.get(0), useStreamCapableState));
            }
            case STREAM -> {
              return Optional.of(provideStreamState(stateMessages, useStreamCapableState));
            }
            case LEGACY -> {
              return Optional.of(getLegacyStateWrapper(stateMessages.get(0).getData()));
            }
            default -> {
              // Should not be reachable.
              throw new IllegalStateException("Unexpected state type");
            }
          }
        }
      } else {
        if (stateMessages.stream().allMatch(stateMessage -> stateMessage.getType() == AirbyteStateType.STREAM)) {
          return Optional.of(provideStreamState(stateMessages, useStreamCapableState));
        }
        if (stateMessages.stream().allMatch(stateMessage -> stateMessage.getType() == null)) {
          return Optional.of(getLegacyStateWrapper(state));
        }

        throw new IllegalStateException("Unexpected state blob, the state contains either multiple global or conflicting state type.");

      }
    }
  }

  /**
   * Converts a StateWrapper to a State
   *
   * LegacyStates are directly serialized into the state. GlobalStates and StreamStates are serialized
   * as a list of AirbyteStateMessage in the state attribute.
   *
   * @param stateWrapper the StateWrapper to convert
   * @return the Converted State
   */
  @SuppressWarnings("UnnecessaryDefault")
  public static State getState(final StateWrapper stateWrapper) {
    return switch (stateWrapper.getStateType()) {
      case LEGACY -> new State().withState(stateWrapper.getLegacyState());
      case STREAM -> new State().withState(Jsons.jsonNode(stateWrapper.getStateMessages()));
      case GLOBAL -> new State().withState(Jsons.jsonNode(List.of(stateWrapper.getGlobal())));
      default -> throw new RuntimeException("Unexpected StateType " + stateWrapper.getStateType());
    };
  }

  public static Boolean isMigration(final StateType currentStateType, final Optional<StateWrapper> previousState) {
    return previousState.isPresent() && isMigration(currentStateType, previousState.get().getStateType());
  }

  public static Boolean isMigration(final StateType currentStateType, final @Nullable StateType previousStateType) {
    return previousStateType == StateType.LEGACY && currentStateType != StateType.LEGACY;
  }

  private static StateWrapper provideGlobalState(final AirbyteStateMessage stateMessages, final boolean useStreamCapableState) {
    if (useStreamCapableState) {
      return new StateWrapper()
          .withStateType(StateType.GLOBAL)
          .withGlobal(stateMessages);
    } else {
      return new StateWrapper()
          .withStateType(StateType.LEGACY)
          .withLegacyState(stateMessages.getData());
    }
  }

  /**
   * This is returning a wrapped state, it assumes that the state messages are ordered.
   *
   * @param stateMessages - an ordered list of state message
   * @param useStreamCapableState - a flag that indicates whether to return the new format
   * @return a wrapped state
   */
  private static StateWrapper provideStreamState(final List<AirbyteStateMessage> stateMessages, final boolean useStreamCapableState) {
    if (useStreamCapableState) {
      return new StateWrapper()
          .withStateType(StateType.STREAM)
          .withStateMessages(stateMessages);
    } else {
      return new StateWrapper()
          .withStateType(StateType.LEGACY)
          .withLegacyState(Iterables.getLast(stateMessages).getData());
    }
  }

  private static StateWrapper getLegacyStateWrapper(final JsonNode state) {
    return new StateWrapper()
        .withStateType(StateType.LEGACY)
        .withLegacyState(state);
  }

}
