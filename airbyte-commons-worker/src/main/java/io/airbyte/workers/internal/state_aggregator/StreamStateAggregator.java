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
    /**
     * The destination emit a Legacy state in order to be retro-compatible with old platform. If we are
     * running this code, we know that the platform has been upgraded and we can thus discard the legacy
     * state. Keeping the legacy state is causing issue because of its size
     * (https://github.com/airbytehq/oncall/issues/731)
     */
    stateMessage.setData(null);
    aggregatedState.put(stateMessage.getStream().getStreamDescriptor(), stateMessage);
  }

  @Override
  public State getAggregated() {

    return new State()
        .withState(
            Jsons.jsonNode(aggregatedState.values()));
  }

}
