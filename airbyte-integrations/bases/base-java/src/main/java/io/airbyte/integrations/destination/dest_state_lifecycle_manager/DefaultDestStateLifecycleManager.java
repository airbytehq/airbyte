/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dest_state_lifecycle_manager;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import java.util.Queue;
import java.util.function.Supplier;

/**
 * Detects the type of the state being received by anchoring on the first state type it sees. Fail
 * if receives states of multiple types--each instance of this class can only support state messages
 * of one type. The protocol specifies that a source should emit state messages of a single type
 * during a sync, so a single instance of this manager is sufficient for a destination to track
 * state during a sync.
 *
 * <p>
 * Strategy: Delegates state messages of each type to a StateManager that is appropriate to that
 * state type.
 * </p>
 *
 * <p>
 * Per the protocol, if state type is not set, assumes the LEGACY state type.
 * </p>
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
    // allows us to delegate calls to the appropriate underlying state manager.
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
    Preconditions.checkArgument(isStateTypeCompatible(stateType, message.getState().getType()));

    setManagerStateTypeIfNotSet(message);

    internalStateManagerSupplier.get().addState(message);
  }

  /**
   * Given the type of previously recorded state by the state manager, determines if a newly added
   * state message's type is compatible. Based on the previously set state type, determines if a new
   * one is compatible. If the previous state is null, any new state is compatible. If new state type
   * is null, it should be treated as LEGACY. Thus, previousStateType == LEGACY and newStateType ==
   * null IS compatible. All other state types are compatible based on equality.
   *
   * @param previousStateType - state type previously recorded by the state manager
   * @param newStateType - state message of a newly added message
   * @return true if compatible, otherwise false
   */
  private static boolean isStateTypeCompatible(final AirbyteStateType previousStateType, final AirbyteStateType newStateType) {
    return previousStateType == null || previousStateType == AirbyteStateType.LEGACY && newStateType == null || previousStateType == newStateType;
  }

  /**
   * If the state type for the manager is not set, sets it using the state type from the message. If
   * the type on the message is null, we assume it is LEGACY. After the first, state message is added
   * to the manager, the state type is set and is immutable.
   *
   * @param message - state message whose state will be used if internal state type is not set
   */
  private void setManagerStateTypeIfNotSet(final AirbyteMessage message) {
    // detect and set state type.
    if (stateType == null) {
      if (message.getState().getType() == null) {
        stateType = AirbyteStateType.LEGACY;
      } else {
        stateType = message.getState().getType();
      }
    }
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
  public void markPendingAsCommitted() {
    internalStateManagerSupplier.get().markPendingAsCommitted();
  }

  @Override
  public void clearCommitted() {
    internalStateManagerSupplier.get().clearCommitted();
  }

  @Override
  public Queue<AirbyteMessage> listCommitted() {
    return internalStateManagerSupplier.get().listCommitted();
  }

  @Override
  public boolean supportsPerStreamFlush() {
    return internalStateManagerSupplier.get().supportsPerStreamFlush();
  }

}
