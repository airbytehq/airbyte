/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
  public State getAggregated() {
    return getStateAggregator().getAggregated();
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
