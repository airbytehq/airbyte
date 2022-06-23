package io.airbyte.workers.internal.state_lifecycle;

import io.airbyte.config.StateWrapper;
import io.airbyte.protocol.models.AirbyteStateMessage;

public interface StateLifecycle {
  StateWrapper acceptStateFromSource(AirbyteStateMessage) {
    StateWr
  };
  StateWrapper acceptStateFromDestination(AirbyteStateMessage);
}
