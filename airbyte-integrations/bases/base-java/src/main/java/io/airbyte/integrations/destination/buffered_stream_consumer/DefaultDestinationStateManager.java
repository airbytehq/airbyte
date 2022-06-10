/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import com.google.common.base.Preconditions;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import java.util.Queue;
import java.util.function.Supplier;

/**
 * Detects the type of the state being received by anchoring on the first state type it sees. Fail
 * if receives states of multiple types. Handles states of each type in an inefficient way by
 * delegating to a StateManager that is specific to that state type.
 *
 * Per the protocol, if state type is not set, assumes the LEGACY state type.
 */
public class DefaultDestinationStateManager implements DestinationStateManager {

  private AirbyteStateType stateType;
  private final DestinationSingleStateManager legacyStateManager;
  private final DestinationStreamLevelStateManager streamStateManager;
  private final Supplier<DestinationStateManager> internalStateManagerSupplier;

  public DefaultDestinationStateManager() {
    stateType = null;
    legacyStateManager = new DestinationSingleStateManager();
    streamStateManager = new DestinationStreamLevelStateManager();
    internalStateManagerSupplier = () -> {
      if (stateType == AirbyteStateType.GLOBAL || stateType == AirbyteStateType.LEGACY) {
        return legacyStateManager;
      } else if (stateType == AirbyteStateType.STREAM) {
        return streamStateManager;
      } else {
        throw new IllegalArgumentException("unrecognized state type");
      }
    };
  }

  @Override
  public void addState(final AirbyteMessage message) {
    Preconditions.checkArgument(message.getType() == Type.STATE, "Messages passed to State Manager must be of type STATE.");
    Preconditions.checkArgument(stateType == null || stateType == message.getState().getStateType());
    if (stateType == null) {
      if (message.getState().getStateType() == null) {
        stateType = AirbyteStateType.LEGACY;
      } else {
        stateType = message.getState().getStateType();
      }
    }

    internalStateManagerSupplier.get().addState(message);
  }

  @Override
  public Queue<AirbyteMessage> listAllPendingState() {
    internalStateManagerSupplier.get().listAllPendingState();
  }

  @Override
  public void markAllReceivedMessagesAsFlushedToTmpDestination() {
    internalStateManagerSupplier.get().markAllReceivedMessagesAsFlushedToTmpDestination();
  }

  @Override
  public Queue<AirbyteMessage> listAllFlushedButNotCommittedState() {
    return internalStateManagerSupplier.get().listAllFlushedButNotCommittedState();
  }

  @Override
  public void markAllFlushedMessageAsCommitted() {
    internalStateManagerSupplier.get().markAllFlushedMessageAsCommitted();
  }

  @Override
  public Queue<AirbyteMessage> listAllCommittedState() {
    return internalStateManagerSupplier.get().listAllCommittedState();
  }

}
