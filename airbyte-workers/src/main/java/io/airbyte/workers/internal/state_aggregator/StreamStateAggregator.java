/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal.state_aggregator;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.StreamDescriptor;
import java.util.HashMap;
import java.util.Map;

class StreamStateAggregator implements StateAggregator {

  Map<StreamDescriptor, AirbyteStateMessage> aggregatedState = new HashMap<>();

  @Override
  public void ingest(final AirbyteStateMessage stateMessage) {
    aggregatedState.put(stateMessage.getStream().getStreamDescriptor(), stateMessage);
  }

  @Override
  public State getAggregated() {

    return new State()
        .withState(
            Jsons.jsonNode(aggregatedState.values()));
  }

}
