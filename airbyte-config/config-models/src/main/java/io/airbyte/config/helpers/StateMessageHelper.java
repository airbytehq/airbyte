/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StateType;
import io.airbyte.config.StateWrapper;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import java.util.List;
import java.util.Optional;

public class StateMessageHelper {

  public static class AirbyteStateMessageListTypeReference extends TypeReference<List<AirbyteStateMessage>> {}

  /**
   * This a takes a json blob state and tries return either a legacy state in the format of a json
   * object or a state message with the new format which is a list of airbyte state message.
   *
   * @param state - a blob representing the state
   * @return An optional state wrapper, if there is no state an empty optional will be returned
   */
  public static Optional<StateWrapper> getTypedState(final JsonNode state) {
    if (state == null) {
      return Optional.empty();
    } else {
      final List<AirbyteStateMessage> stateMessages;
      try {
        stateMessages = Jsons.object(state, new AirbyteStateMessageListTypeReference());
      } catch (final IllegalArgumentException e) {
        return Optional.of(getLegacyStateWrapper(state));
      }
      if (stateMessages.stream().anyMatch(streamMessage -> !streamMessage.getAdditionalProperties().isEmpty())) {
        return Optional.of(getLegacyStateWrapper(state));
      }
      if (stateMessages.size() == 1 && stateMessages.get(0).getStateType() == AirbyteStateType.GLOBAL) {
        return Optional.of(new StateWrapper()
            .withStateType(StateType.GLOBAL)
            .withGlobal(stateMessages.get(0)));
      } else if (stateMessages.size() >= 1
          && stateMessages.stream().allMatch(stateMessage -> stateMessage.getStateType() == AirbyteStateType.STREAM)) {
        return Optional.of(new StateWrapper()
            .withStateType(StateType.STREAM)
            .withStateMessages(stateMessages));
      } else {
        throw new IllegalStateException("Unexpected state blob");
      }
    }
  }

  private static StateWrapper getLegacyStateWrapper(final JsonNode state) {
    return new StateWrapper()
        .withStateType(StateType.LEGACY)
        .withLegacyState(state);
  }

}
