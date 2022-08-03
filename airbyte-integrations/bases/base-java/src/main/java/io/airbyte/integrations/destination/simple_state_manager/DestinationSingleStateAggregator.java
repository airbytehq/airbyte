package io.airbyte.integrations.destination.simple_state_manager;

import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import java.util.LinkedHashSet;
import java.util.Set;

class DestinationSingleStateAggregator implements DestinationStateAggregator {

  AirbyteStateMessage state;

  @Override public void ingest(final AirbyteStateMessage stateMessage) {
    this.state = stateMessage;
  }

  @Override public LinkedHashSet<AirbyteMessage> getStateMessages() {
    return new LinkedHashSet(Set.of(state));
  }
}
