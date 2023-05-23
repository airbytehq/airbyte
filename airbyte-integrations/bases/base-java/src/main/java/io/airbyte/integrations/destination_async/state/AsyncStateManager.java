/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.state;

import io.airbyte.integrations.destination_async.buffers.StreamAwareQueue;
import io.airbyte.integrations.destination_async.buffers.StreamAwareQueue.Meta;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.ConcurrentMap;
import java.util.stream.Collectors;

// todo (cgardens) - hook it up to the memory manager.
public class AsyncStateManager {

  private final Map<StreamDescriptor, StreamContract> streamToContract;
  private final Map<StreamDescriptor, StateLifecycle> streamToLifecycle;
  private final ConcurrentMap<StreamDescriptor, StreamAwareQueue> buffers;
  private AirbyteStateType stateType;

  public AsyncStateManager(final ConcurrentMap<StreamDescriptor, StreamAwareQueue> buffers) {
    this.buffers = buffers;
    // todo (cgardens) - eager instantiate?
    streamToContract = new HashMap<>();
    streamToLifecycle = new HashMap<>();
    stateType = null;
  }

  private StreamContract getOrCreateContract(final StreamDescriptor streamDescriptor) {
    if (!streamToContract.containsKey(streamDescriptor)) {
      streamToContract.put(streamDescriptor, new StreamContract());
    }
    return streamToContract.get(streamDescriptor);
  }

  private Optional<StreamContract> getContract(final StreamDescriptor streamDescriptor) {
    if (streamToContract.containsKey(streamDescriptor)) {
      return Optional.ofNullable(streamToContract.get(streamDescriptor));
    } else {
      return Optional.empty();
    }
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

  public synchronized void claim(final StreamDescriptor streamDescriptor, final long maxMessageNum) {
    getOrCreateContract(streamDescriptor).claim(maxMessageNum);
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
   * @param maxMessageNum max number that was emitted by batch
   * @return highest state for which itself and all previous states have been flushed.
   */
  public Optional<AirbyteMessage> fulfill(final StreamDescriptor streamDescriptor, final long maxMessageNum) {
    getContract(streamDescriptor)
        .orElseThrow(() -> new IllegalStateException(
            String.format("Attempting to fulfill a contract that was never created. stream desc: %s", streamDescriptor)))
        .fulfill(maxMessageNum);

    if (stateType == AirbyteStateType.STREAM) {
      return completeFor(Set.of(streamDescriptor), getLifecycle(streamDescriptor));
    } else {
      return completeFor(buffers.keySet(), getLifecycle(null));
    }
  }

  public List<AirbyteMessage> flush() {
    if (stateType == AirbyteStateType.STREAM) {
      return buffers
          .keySet()
          .stream()
          .map(streamDescriptor -> completeFor(Set.of(streamDescriptor), getLifecycle(streamDescriptor)))
          .filter(Optional::isPresent)
          .map(Optional::get)
          .collect(Collectors.toList());
    } else {
      return completeFor(buffers.keySet(), getLifecycle(null))
          .map(List::of)
          .orElse(Collections.emptyList());
    }
  }

  private Optional<AirbyteMessage> completeFor(final Set<StreamDescriptor> relevantStreams,
                                               final Optional<StateLifecycle> lifecycle) {

    long conservativeMax = Long.MAX_VALUE;
    for (final StreamDescriptor streamDesc : relevantStreams) {
      conservativeMax = Math.min(conservativeMax, getMaxSafeNumber(buffers.get(streamDesc), getContract(streamDesc)));
    }

    final long conservativeMaxFinal = conservativeMax;
    return lifecycle.flatMap(l -> l.getBestStateAndPurge(Math.max(0, conservativeMaxFinal)));
  }

  private long getMaxSafeNumber(final StreamAwareQueue buffer, final Optional<StreamContract> contractOptional) {
    final Optional<Meta> peeked = buffer.peek();

    /*
     * if no contract was ever started, if the queue is empty then any state is safe to emit. otherwise
     * one less than the peeked is safe.
     */
    if (contractOptional.isEmpty()) {
      return peeked.map(meta -> meta.messageNum() - 1).orElse(Long.MAX_VALUE);
    }

    final StreamContract contract = contractOptional.get();

    final long max = contract.getClaimedMax().orElse(0L);
    final long maxFlushed = contract.getFulfilledMax().orElse(0L);

    // all contracts are done
    if (maxFlushed == max) {
      // in this case the next record minus 1 is safe. if no record infinity!
      return peeked.map(meta -> Math.max(meta.messageNum() - 1, 0)).orElse(Long.MAX_VALUE);
    } else {
      return maxFlushed;
    }
  }

  private Optional<StreamDescriptor> extractStream(final AirbyteMessage message) {
    return Optional.ofNullable(message.getState().getStream()).map(AirbyteStreamState::getStreamDescriptor);
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
