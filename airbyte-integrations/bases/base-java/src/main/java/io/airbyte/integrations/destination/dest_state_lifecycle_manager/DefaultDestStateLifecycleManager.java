/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dest_state_lifecycle_manager;

import com.google.common.annotations.VisibleForTesting;
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
public class DefaultDestStateLifecycleManager implements DestStateLifecycleManager {

  private AirbyteStateType stateType;
  private final Supplier<DestStateLifecycleManager> internalStateManagerSupplier;

  public DefaultDestStateLifecycleManager() {
    this(new DestSingleStateLifecycleManager(), new DestStreamStateLifecycleManager());
  }

  @VisibleForTesting
  DefaultDestStateLifecycleManager(final DestStateLifecycleManager singleStateManager, final DestStateLifecycleManager streamStateManager) {
    stateType = null;
    internalStateManagerSupplier = () -> {
      if (stateType == AirbyteStateType.GLOBAL || stateType == AirbyteStateType.LEGACY || stateType == null) {
        return singleStateManager;
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
    Preconditions.checkArgument(isStateTypeCompatible(stateType, message.getState().getStateType()));
    if (stateType == null) {
      if (message.getState().getStateType() == null) {
        stateType = AirbyteStateType.LEGACY;
      } else {
        stateType = message.getState().getStateType();
      }
    }

    internalStateManagerSupplier.get().addState(message);
  }

  private static boolean isStateTypeCompatible(final AirbyteStateType previousStateType, final AirbyteStateType newStateType) {
    return previousStateType == null || previousStateType == AirbyteStateType.LEGACY && newStateType == null || previousStateType == newStateType;
  }

  @Override
  public void markPendingAsFlushed() {
    internalStateManagerSupplier.get().markPendingAsFlushed();
  }

  @Override
  public Queue<AirbyteMessage> listFlushed() {
    return internalStateManagerSupplier.get().listFlushed();
  }

  @Override
  public void markFlushedAsCommitted() {
    internalStateManagerSupplier.get().markFlushedAsCommitted();
  }

  @Override
  public Queue<AirbyteMessage> listCommitted() {
    return internalStateManagerSupplier.get().listCommitted();
  }

}
