package io.airbyte.workers.internal.state_lifecycle;

import io.airbyte.protocol.models.AirbyteStateMessage;

public interface WorkerStateLifecyle {

  void acceptSource(AirbyteStateMessage stateMessage);
  void acceptDestination(AirbyteStateMessage stateMessage);
}
