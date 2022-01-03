/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols.airbyte;

import com.google.common.base.Charsets;
import com.google.common.hash.HashFunction;
import com.google.common.hash.Hashing;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AirbyteMessageTracker implements MessageTracker { // TODO the MessageTracker interface used to extend Consumer<>, is it bad that I no
  // longer do this?

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteMessageTracker.class);

  private final AtomicLong recordCount;
  private final AtomicLong numBytes;
  private final AtomicReference<State> sourceOutputState;
  private final AtomicReference<State> destinationOutputState;
  private final HashFunction hashFunction;
  private final Map<String, Short> streamIndexByName;
  private final Map<Short, String> streamNameByIndex;
  private short nextStreamIndex;

  /**
   * Track the running count of source-emitted records since the last source-emitted state record,
   * indexed by stream. When the tracker receives a source-emitted state record, these running counts
   * are persisted to {@link AirbyteMessageTracker#runningCountByStreamByState} and this map is reset
   * to an empty state.
   */
  private final Map<Short, Long> runningCountByStream;

  /**
   * Tracks the running count of source-emitted records by stream, indexed by the state hashcode
   * pertaining to those records. When the tracker receives a DESTINATION-emitted state record, the
   * running counts for that state are persisted to
   * {@link AirbyteMessageTracker#committedCountByStream} and cleared from this map. TODO handle state
   * hash collisions. TODO handle concurrent access? do we actually need ConcurrentHashMap?
   */
  private final ConcurrentHashMap<Integer, Map<Short, Long>> runningCountByStreamByState;

  /**
   * Tracks the last state hash that was emitted by the destination.
   */
  private Integer lastCommittedStateIndex;

  /**
   * Tracks a list of state hashes in the order that they were emitted by the source.
   */
  private final List<Integer> orderedStateHashes;

  /**
   * Tracks the committed count of records per stream. This map is only updated when the tracker
   * receives a destination-emitted state message. During such an update, the running counts by stream
   * are added to the committed counts by stream. There should be one such update for every
   * destination-emitted state message.
   */
  private final Map<Short, Long> committedCountByStream;

  public AirbyteMessageTracker() {
    this.recordCount = new AtomicLong();
    this.numBytes = new AtomicLong();
    this.sourceOutputState = new AtomicReference<>();
    this.destinationOutputState = new AtomicReference<>();
    this.runningCountByStream = new HashMap<>();
    this.runningCountByStreamByState = new ConcurrentHashMap<>();
    this.lastCommittedStateIndex = null;
    this.orderedStateHashes = new ArrayList<>();
    this.committedCountByStream = new HashMap<>();
    this.streamIndexByName = new HashMap<>();
    this.streamNameByIndex = new HashMap<>();
    this.nextStreamIndex = 0;
    this.hashFunction = Hashing.murmur3_32_fixed(); // TODO seed with currTime so that if a hash collision occurs, a retry might work due to different
                                                    // seed? More digging needed
  }

  // TODO note to self: Added private methods at the bottom to handle the new stuff. Now need to call
  // those methods where appropriate.
  // TODO also need to add in EMITTED counts per stream, because right now it just tracks total
  // records emitted overall.
  // TODO also need to think about concurrency questions, and adding escape hatch/failure scenario so
  // that we can try to report as much information as we can.

  @Override
  public void acceptFromSource(final AirbyteMessage message) {
    if (message.getType() == AirbyteMessage.Type.RECORD) {
      recordCount.incrementAndGet();
      // todo (cgardens) - pretty wasteful to do an extra serialization just to get size.
      numBytes.addAndGet(Jsons.serialize(message.getRecord().getData()).getBytes(Charsets.UTF_8).length);
      LOGGER.info("Source got a record message! record: {}", message.getRecord());

      // new code: increment running count for message's stream
      final short streamIndex = getStreamIndex(message.getRecord().getStream());
      final Long currentCount = runningCountByStream.getOrDefault(streamIndex, 0L);
      runningCountByStream.put(streamIndex, currentCount + 1);
    }

    if (message.getType() == AirbyteMessage.Type.STATE) {
      LOGGER.info("Source got a state message! state: {}", message.getState());
      sourceOutputState.set(new State().withState(message.getState().getData()));

      // new code: commit running count to per-stream count
      final int stateHashCode = getStateHashCode(message.getState());
      if (runningCountByStreamByState.containsKey(stateHashCode)) {
        throw new RuntimeException("Already saw this state hash!"); // TODO handle in more depth
      } else {
        runningCountByStreamByState.put(stateHashCode, new HashMap<>(runningCountByStream));
        runningCountByStream.clear();
      }
    }
  }

  @Override
  public void acceptFromDestination(final AirbyteMessage message) {
    if (message.getType() == AirbyteMessage.Type.STATE) {
      LOGGER.info("Destination got a state message! state: {}", message.getState());
      destinationOutputState.set(new State().withState(message.getState().getData()));

      // new code: persist this state's running count to committed count, then delete from running count
      // map
      final int stateHashCode = getStateHashCode(message.getState());
      runningCountByStreamByState.get(stateHashCode).forEach((stream, runningCount) -> {
        final Long currentCount = committedCountByStream.getOrDefault(stream, 0L);
        committedCountByStream.put(stream, currentCount + runningCount);
      });
      runningCountByStreamByState.remove(stateHashCode);
    }
  }

  @Override
  public long getRecordCount() { // TODO make sure to track emitted records per stream
    return recordCount.get();
  }

  @Override
  public long getBytesCount() {
    return numBytes.get();
  }

  @Override
  public Optional<State> getSourceOutputState() {
    return Optional.ofNullable(sourceOutputState.get());
  }

  @Override
  public Optional<State> getDestinationOutputState() {
    return Optional.ofNullable(destinationOutputState.get());
  }

  @Override
  public Map<String, Long> getCommittedRecordsByStream() {
    final Map<String, Long> committedRecordsByStreamName = new HashMap<>();

    committedCountByStream.forEach((streamIndex, count) -> {
      committedRecordsByStreamName.put(streamNameByIndex.get(streamIndex), count);
    });

    return committedRecordsByStreamName;
  }

  private short getStreamIndex(final String streamName) {
    if (!streamIndexByName.containsKey(streamName)) {
      streamIndexByName.put(streamName, nextStreamIndex);
      streamNameByIndex.put(nextStreamIndex, streamName);
      nextStreamIndex++;
    }
    return streamIndexByName.get(streamName);
  }

  private int getStateHashCode(final AirbyteStateMessage stateMessage) {
    return hashFunction.hashBytes(Jsons.serialize(stateMessage.getData()).getBytes(Charsets.UTF_8)).hashCode();
  }

  /**
   * When a source emits a record, increment the count for that record's stream.
   */
  private void handleSourceEmittedRecord(final AirbyteRecordMessage recordMessage) {
    final short streamIndex = getStreamIndex(recordMessage.getStream());
    final long currentCount = runningCountByStream.getOrDefault(streamIndex, 0L);
    this.runningCountByStream.put(streamIndex, currentCount + 1);
  }

  /**
   * When a source emits a state, persist the current running count per stream to the map that is
   * tracking counts per state. Then, reset the running count per stream so that new counts can start
   * recording for the next state. Also add the state to list so that state order is tracked
   * correctly.
   */
  private void handleSourceEmittedState(final AirbyteStateMessage stateMessage) {
    final int stateHash = getStateHashCode(stateMessage);
    if (runningCountByStreamByState.containsKey(stateHash)) {
      throw new IllegalStateException(String.format("State hash collision detected for stateMessage %s", stateMessage.getData().toString()));
    }
    runningCountByStreamByState.put(stateHash, new HashMap<>(runningCountByStream));
    runningCountByStream.clear();
    orderedStateHashes.add(stateHash);
  }

  /**
   * When a destination emits a state, update the committed count per stream by adding up the running
   * count deltas for all states since the last committed state. Also record the state as the last
   * committed state.
   */
  private void handleDestinationEmittedState(final AirbyteStateMessage stateMessage) {
    final int committedStateHash = getStateHashCode(stateMessage);
    int currStateHash;

    do {
      currStateHash = orderedStateHashes.get(lastCommittedStateIndex);

      runningCountByStreamByState.get(currStateHash).forEach((streamIndex, runningCount) -> {
        final Long committedCount = committedCountByStream.getOrDefault(streamIndex, 0L);
        committedCountByStream.put(streamIndex, committedCount + runningCount);
      });

      lastCommittedStateIndex++;
    } while (currStateHash != committedStateHash);
  }

}
