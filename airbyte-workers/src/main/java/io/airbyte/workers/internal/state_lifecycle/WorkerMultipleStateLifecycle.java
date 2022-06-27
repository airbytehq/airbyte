package io.airbyte.workers.internal.state_lifecycle;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.StreamDescriptor;
import java.util.HashMap;
import java.util.Map;

public class WorkerMultipleStateLifecycle implements WorkerStateLifecyle {

  private final Map<StreamDescriptor, JsonNode> pending = new HashMap<>();
  private final Map<StreamDescriptor, JsonNode> committed = new HashMap<>();

  @Override public void acceptSource(final AirbyteStateMessage stateMessage) {
    pending.put(stateMessage.getStream().getStreamDescriptor(), stateMessage.getStream().getStreamState());
  }

  @Override public void acceptDestination(final AirbyteStateMessage stateMessage) {

  }
}
