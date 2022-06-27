package io.airbyte.workers.internal.state_lifecycle;

import io.airbyte.protocol.models.AirbyteStateMessage;

public class DefaultWorkerStateLifecycle implements WorkerStateLifecyle {

  @Override public void acceptSource(final AirbyteStateMessage stateMessage) {

  }

  @Override public void acceptDestination(final AirbyteStateMessage stateMessage) {

  }
}
