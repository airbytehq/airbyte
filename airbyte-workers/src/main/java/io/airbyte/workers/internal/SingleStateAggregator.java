package io.airbyte.workers.internal;

import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import java.util.List;

public class SingleStateAggregator implements StateAggregator {

  AirbyteStateMessage state;

  @Override public void ingest(final AirbyteStateMessage stateMessage) {
    final AirbyteStateType stateType = stateMessage.getType();
    Preconditions.checkArgument(stateType == AirbyteStateType.GLOBAL || stateType == AirbyteStateType.LEGACY || stateType == null);

    state = stateMessage;
  }

  @Override public State getAggregated() {
    if (state.getType() == null || state.getType() == AirbyteStateType.LEGACY) {
      return new State().withState(state.getData());
    } else {
      return new State()
          .withState(Jsons.jsonNode(List.of(state)));
    }
  }
}
