package io.airbyte.workers.internal;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.StreamDescriptor;
import java.util.Map;

public class StreamStateAggregator implements StateAggregator {

  Map<StreamDescriptor, AirbyteStateMessage> aggregatedState;

  @Override public void ingest(AirbyteStateMessage stateMessage) {
    Preconditions.checkArgument(stateMessage.getType() == AirbyteStateType.STREAM);

    aggregatedState.put(stateMessage.getStream().getStreamDescriptor(), stateMessage);
  }

  @Override public State getAggregated() {

    return new State()
        .withState(
            Jsons.jsonNode(aggregatedState.values())
        );
  }
}
