/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.state;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

// todo (cgardens) - hook it up to the memory manager.
public class AsyncDestinationStateManager {

  private final Map<StreamDescriptor, StateLifecycle> streamToLifecycle;
  private AirbyteStateType stateType;

  public AsyncDestinationStateManager() {
    // todo (cgardens) - eager instantiate?
    streamToLifecycle = new HashMap<>();
    stateType = null;
  }

  private StateLifecycle getOrCreateLifecycle(final StreamDescriptor streamDescriptor) {
    if (!streamToLifecycle.containsKey(streamDescriptor)) {
      streamToLifecycle.put(streamDescriptor, new StateLifecycle());
    }
    return streamToLifecycle.get(streamDescriptor);
  }

  private Optional<StateLifecycle> getLifecycle(final StreamDescriptor streamDescriptor) {
    final StreamDescriptor key = stateType == AirbyteStateType.STREAM ? streamDescriptor : null;

    if (streamToLifecycle.containsKey(key)) {
      return Optional.ofNullable(streamToLifecycle.get(key));
    } else {
      return Optional.empty();
    }
  }

  /**
   *
   * @param streamDescriptor stream descriptor for the state. null if global state.
   * @param message state message to track
   */
  public void trackState(final AirbyteMessage message, final long messageNum) {
    setManagerStateTypeIfNotSet(message);
    getOrCreateLifecycle(extractStream(message).orElse(null)).trackState(message, messageNum);
  }

  /**
   * Marks the provided state as completed. It then returns the highest state possible. This
   * calculated as the highest state for which itself and all the previous states have been flushed.
   * <p>
   * For example, if BEFORE this message was called S1: not flushed S2: flushed, S3: not flushed, and
   * then this method is called with S3, it will return an empty optional, because even though S3 is
   * flushed, S1 hasn't, so it's not safe to emit any states.
   * <p>
   * Now let's say after that method call our states now look like this. S1: not flushed S2: flushed,
   * S3: flushed. Now, we call this method with S1 and then this method is called with S1. This method
   * would return S3, because all the states through S3 have now been flushed.
   *
   * @param minMessageNum min number that was emitted by batch
   * @param maxMessageNum max number that was emitted by batch
   * @return highest state for which itself and all previous states have been flushed.
   */
  public Optional<AirbyteMessage> completeState(final StreamDescriptor streamDescriptor, final long minMessageNum, final long maxMessageNum) {
    return getLifecycle(streamDescriptor).flatMap(lifecycle -> lifecycle.completeState(minMessageNum, maxMessageNum));
  }

  private Optional<StreamDescriptor> extractStream(final AirbyteMessage message) {
    return Optional.of(message.getState().getStream().getStreamDescriptor());
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

}
