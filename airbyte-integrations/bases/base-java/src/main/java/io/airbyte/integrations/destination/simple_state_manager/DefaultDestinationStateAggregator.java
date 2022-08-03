package io.airbyte.integrations.destination.simple_state_manager;

import com.google.common.base.Preconditions;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import java.util.LinkedHashSet;
import lombok.RequiredArgsConstructor;

@RequiredArgsConstructor
public class DefaultDestinationStateAggregator implements DestinationStateAggregator {

  private AirbyteStateType stateType = null;
  private final DestinationStateAggregator streamStateAggregator = new DestinationStreamStateAggregator();
  private final DestinationStateAggregator singleStateAggregator = new DestinationSingleStateAggregator();
  private final boolean useStreamCapableState;

  @Override public void ingest(final AirbyteStateMessage stateMessage) {
    checkTypeOrSetType(stateMessage.getType());

    getStateAggregator().ingest(stateMessage);
  }

  @Override public LinkedHashSet<AirbyteMessage> getStateMessages() {
    return getStateAggregator().getStateMessages();
  }

  /**
   * Return the state aggregator that match the state type.
   */
  private DestinationStateAggregator getStateAggregator() {
    if (!useStreamCapableState) {
      return singleStateAggregator;
    } else {
      return switch (stateType) {
        case STREAM -> streamStateAggregator;
        case GLOBAL, LEGACY -> singleStateAggregator;
      };
    }
  }

  /**
   * We can not have 2 different state types given to the same instance of this class. This method set
   * the type if it is not. If the state type doesn't exist in the message, it is set to LEGACY
   */
  private void checkTypeOrSetType(final AirbyteStateType inputStateType) {
    final AirbyteStateType validatedStateType;
    if (inputStateType == null) {
      validatedStateType = AirbyteStateType.LEGACY;
    } else {
      validatedStateType = inputStateType;
    }
    if (this.stateType == null) {
      this.stateType = validatedStateType;
    }
    Preconditions.checkArgument(this.stateType == validatedStateType,
        "Input state type " + validatedStateType + " does not match the aggregator's current state type " + this.stateType);
  }
}
