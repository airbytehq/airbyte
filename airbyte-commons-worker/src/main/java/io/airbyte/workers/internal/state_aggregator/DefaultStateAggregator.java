/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal.state_aggregator;

import com.google.common.base.Preconditions;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;

public class DefaultStateAggregator implements StateAggregator {

  private AirbyteStateType stateType = null;
  private final StateAggregator streamStateAggregator = new StreamStateAggregator();
  private final StateAggregator singleStateAggregator = new SingleStateAggregator();
  private final boolean useStreamCapableState;

  public DefaultStateAggregator(final boolean useStreamCapableState) {
    this.useStreamCapableState = useStreamCapableState;
  }

  @Override
  public void ingest(final AirbyteStateMessage stateMessage) {
    checkTypeOrSetType(stateMessage.getType());

    getStateAggregator().ingest(stateMessage);
  }

  @Override
  public void ingest(final StateAggregator stateAggregator) {
    // We fail to ingest if the state aggregators have different types
    // If this.stateType is null, we copy the content from the other state
    if (stateAggregator instanceof DefaultStateAggregator &&
        (stateType == null ||
            ((DefaultStateAggregator) stateAggregator).stateType == null ||
            stateType == ((DefaultStateAggregator) stateAggregator).stateType)) {
      singleStateAggregator.ingest(((DefaultStateAggregator) stateAggregator).singleStateAggregator);
      streamStateAggregator.ingest(((DefaultStateAggregator) stateAggregator).streamStateAggregator);

      // Since we allowed stateType to be null, make sure it is set to a value correct value
      if (stateType == null) {
        stateType = ((DefaultStateAggregator) stateAggregator).stateType;
      }
    } else {
      throw new IllegalArgumentException(
          "Got an incompatible StateAggregator: " + prettyPrintStateAggregator(stateAggregator) +
              ", expected " + prettyPrintStateAggregator(this));
    }
  }

  private String prettyPrintStateAggregator(final StateAggregator aggregator) {
    if (aggregator instanceof DefaultStateAggregator) {
      return "DefaultStateAggregator<" + ((DefaultStateAggregator) aggregator).stateType + ">";
    } else {
      return aggregator.getClass().getName();
    }
  }

  @Override
  public State getAggregated() {
    return getStateAggregator().getAggregated();
  }

  @Override
  public boolean isEmpty() {
    return stateType == null || getStateAggregator().isEmpty();
  }

  /**
   * Return the state aggregator that match the state type.
   */
  private StateAggregator getStateAggregator() {
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
