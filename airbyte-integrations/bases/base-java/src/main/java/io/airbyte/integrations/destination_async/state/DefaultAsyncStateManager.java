/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.state;

import io.airbyte.integrations.destination_async.state.PreStateAsyncStateManager.PreStateOutput;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Collections;
import java.util.List;

// todo (cgardens) - hook it up to the memory manager.
public class DefaultAsyncStateManager {

  boolean preState;
  private final PreStateAsyncStateManager preStateAsyncStateManager;
  private PostStateAsyncStateManager postStateAsyncStateManager;

  public DefaultAsyncStateManager() {
    preStateAsyncStateManager = new PreStateAsyncStateManager();
  }

  public long getStateIdAndIncrement(final StreamDescriptor streamDescriptor) {
    if (preState) {
      return preStateAsyncStateManager.getStateId(streamDescriptor);
    } else {
      return postStateAsyncStateManager.getStateId(streamDescriptor);
    }
  }

  public void decrement(final long stateId) {
    if (preState) {
      preStateAsyncStateManager.decrement(stateId);
    } else {
      postStateAsyncStateManager.decrement(stateId);
    }
  }

  public void trackState(final AirbyteMessage message) {
    if (preState) {
      final PreStateOutput preStateOutput = preStateAsyncStateManager.convert();
      postStateAsyncStateManager = new PostStateAsyncStateManager(
          extractStateType(message),
          preStateOutput.streamToStateId(),
          preStateOutput.stateIdToCounter(),
          preStateOutput.lastStateId(),
          message);
    } else {
      postStateAsyncStateManager.trackState(message);
    }
  }

  public List<AirbyteMessage> flushStates() {
    if (preState) {
      return Collections.emptyList();
    } else {
      return postStateAsyncStateManager.flushStates();
    }
  }

  private AirbyteStateType extractStateType(final AirbyteMessage message) {
    if (message.getState().getType() == null) {
      return AirbyteStateType.LEGACY;
    } else {
      return message.getState().getType();
    }
  }

}
