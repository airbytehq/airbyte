package io.airbyte.integrations.destination.simple_state_manager;

import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import java.util.LinkedHashSet;

public interface DestinationStateAggregator {

  /**
   * Aggregate a state message
   * @param stateMessage -- the state message to aggregate
   */
  void ingest(AirbyteStateMessage stateMessage);

  /**
   * Return a sorted set of state message ordered by emission date
   * @return the sorted list of state message to edit
   */
  LinkedHashSet<AirbyteMessage> getStateMessages();
}
