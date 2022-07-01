/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import com.google.common.base.Preconditions;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;

public class DefaultStateAggregator implements StateAggregator {

  private AirbyteStateType stateType = null;
  private final StateAggregator streamStateAggregator = new StreamStateAggregator();
  private final StateAggregator singleStateAggregator = new SingleStateAggregator();

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
    return switch (stateType) {
      case STREAM -> streamStateAggregator;
      case GLOBAL, LEGACY -> singleStateAggregator;
    };
  }

  /**
   * We can not have 2 different state types given to the same instance of this class. This method set
   * the type if it is not. If the state type doesn't exist in the message, it is set to LEGACY
   */
  private void checkTypeOrSetType(AirbyteStateType stateType) {
    if (stateType == null) {
      stateType = AirbyteStateType.LEGACY;
    }
    if (this.stateType == null) {
      this.stateType = stateType;
    }
    Preconditions.checkArgument(this.stateType == stateType);
  }

}
