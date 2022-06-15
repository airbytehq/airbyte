/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.vavr.control.Either;
import java.util.ArrayList;
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
  public static Either<JsonNode, List<AirbyteStateMessage>> getTypedState(JsonNode state) {
    if (state == null) {
      return Either.right(new ArrayList<>());
    }
    try {
      return Either.right(Jsons.object(state, new AirbyteStateMessageListTypeReference()));
    } catch (final IllegalArgumentException e) {
      return Either.left(state);
    }
  }

}
