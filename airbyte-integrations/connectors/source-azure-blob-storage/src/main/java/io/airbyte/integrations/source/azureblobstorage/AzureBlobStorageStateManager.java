/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.azureblobstorage;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.configoss.StateWrapper;
import io.airbyte.configoss.helpers.StateMessageHelper;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import java.util.List;
import java.util.Optional;

public class AzureBlobStorageStateManager {

  private AzureBlobStorageStateManager() {

  }

  public static StreamState deserializeStreamState(final JsonNode state, final boolean useStreamCapableState) {
    final Optional<StateWrapper> typedState =
        StateMessageHelper.getTypedState(state, useStreamCapableState);
    return typedState.map(stateWrapper -> switch (stateWrapper.getStateType()) {
      case STREAM:
        yield new StreamState(AirbyteStateMessage.AirbyteStateType.STREAM, stateWrapper.getStateMessages().stream()
            .map(sm -> Jsons.object(Jsons.jsonNode(sm), AirbyteStateMessage.class)).toList());
      case LEGACY:
        yield new StreamState(AirbyteStateMessage.AirbyteStateType.LEGACY, List.of(
            new AirbyteStateMessage().withType(AirbyteStateMessage.AirbyteStateType.LEGACY)
                .withData(stateWrapper.getLegacyState())));
      case GLOBAL:
        throw new UnsupportedOperationException("Unsupported stream state");
    }).orElseGet(() -> {
      // create empty initial state
      if (useStreamCapableState) {
        return new StreamState(AirbyteStateMessage.AirbyteStateType.STREAM, List.of(
            new AirbyteStateMessage().withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(new AirbyteStreamState())));
      } else {
        // TODO (itaseski) remove support for DbState
        return new StreamState(AirbyteStateMessage.AirbyteStateType.LEGACY, List.of(
            new AirbyteStateMessage().withType(AirbyteStateMessage.AirbyteStateType.LEGACY)
                .withData(Jsons.jsonNode(new DbState()))));
      }
    });
  }

  record StreamState(

                     AirbyteStateMessage.AirbyteStateType airbyteStateType,

                     List<AirbyteStateMessage> airbyteStateMessages) {

  }

}
