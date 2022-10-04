/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal.state_aggregator;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import java.util.List;

class SingleStateAggregator implements StateAggregator {

  AirbyteStateMessage state;

  @Override
  public void ingest(final AirbyteStateMessage stateMessage) {
    state = stateMessage;
  }

  @Override
  public State getAggregated() {
    if (state.getType() == null || state.getType() == AirbyteStateType.LEGACY) {
      return new State().withState(state.getData());
    } else {
      return new State()
          .withState(Jsons.jsonNode(List.of(state)));
    }
  }

}
