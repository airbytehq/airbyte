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

public class StateMessageHelper {

  public static class AirbyteStateMessageListTypeReference extends TypeReference<List<AirbyteStateMessage>> {}

  /**
   * This a takes a json blob state and tries return either a legacy state in the format of a json
   * object or a state message with the new format which is a list of airbyte state message.
   *
   * @param state
   * @return Either a json blob (on the left) or a structure state message.
   */
  public static StateWrapper getTypedState(JsonNode state) {
    if (state == null) {
      return new StateWrapper()
          .withStateType(StateType.EMPTY);
    } else {
      try {
        List<AirbyteStateMessage> stateMessages = Jsons.object(state, new AirbyteStateMessageListTypeReference());
        if (stateMessages.size() == 1 && stateMessages.get(0).getStateType() == AirbyteStateType.GLOBAL) {
          return new StateWrapper()
              .withStateType(StateType.GLOBAL)
              .withGlobal(stateMessages.get(0));
        } else if (stateMessages.size() >= 1
            && stateMessages.stream().filter(stateMessage -> stateMessage.getStateType() != AirbyteStateType.STREAM).toList().isEmpty()) {
          return new StateWrapper()
              .withStateType(StateType.STREAM)
              .withStateMessages(stateMessages);
        } else {
          throw new IllegalStateException("Unexpected state blob");
        }

      } catch (final IllegalArgumentException e) {
        return new StateWrapper()
            .withStateType(StateType.LEGACY)
            .withLegacyState(state);
      }
    }
    /*
     * if (state == null) { // return Either.right(new ArrayList<>()); } try { return
     * Either.right(Jsons.object(state, new AirbyteStateMessageListTypeReference())); } catch (final
     * IllegalArgumentException e) { return Either.left(state); }
     */
  }

}
