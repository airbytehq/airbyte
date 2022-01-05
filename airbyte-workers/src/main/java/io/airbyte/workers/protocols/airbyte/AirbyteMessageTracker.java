/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols.airbyte;

import com.google.common.base.Charsets;
import com.google.common.collect.BiMap;
import com.google.common.collect.HashBiMap;
import com.google.common.hash.HashFunction;
import com.google.common.hash.Hashing;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.workers.protocols.airbyte.StateDeltaTracker.CapacityExceededException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class AirbyteMessageTracker implements MessageTracker {

  private final AtomicReference<State> sourceOutputState;
  private final AtomicReference<State> destinationOutputState;
  private final Map<Short, Long> runningCountByStream;
  private final List<Integer> orderedStateHashes;
  private final HashFunction hashFunction;
  private final BiMap<String, Short> streamIndexByName;
  private final Map<Short, Long> totalBytesEmittedByStream;
  private final Map<Short, Long> totalRecordsEmittedByStream;
  private final StateDeltaTracker stateDeltaTracker;

  private short nextStreamIndex;
  private short nextStateIndexToCommit;
  private boolean exceededDeltaTrackerCapacity;

  public AirbyteMessageTracker() {
    this.sourceOutputState = new AtomicReference<>();
    this.destinationOutputState = new AtomicReference<>();
    this.runningCountByStream = new HashMap<>();
    this.orderedStateHashes = new ArrayList<>();
    this.streamIndexByName = HashBiMap.create();
    this.hashFunction = Hashing.murmur3_32_fixed();
    this.totalBytesEmittedByStream = new HashMap<>();
    this.totalRecordsEmittedByStream = new HashMap<>();
    this.stateDeltaTracker = new StateDeltaTracker(10 * 1024 * 1024 * 1024); // 10 GiB memory limit, arbitrary TODO what should be set here?
    this.nextStreamIndex = 0;
    this.nextStateIndexToCommit = 0;
    this.exceededDeltaTrackerCapacity = false;
  }

  @Override
  public void acceptFromSource(final AirbyteMessage message) {
    switch (message.getType()) {
      case RECORD -> handleSourceEmittedRecord(message.getRecord());
      case STATE -> handleSourceEmittedState(message.getState());
      default -> log.warn("Invalid message type for message: {}", message);
    }
  }

  @Override
  public void acceptFromDestination(final AirbyteMessage message) {
    switch (message.getType()) {
      case STATE -> handleDestinationEmittedState(message.getState());
      default -> log.warn("Invalid message type for message: {}", message);
    }
  }

  /**
   * When a source emits a record, increment the running record count, the total record count, and the total byte count for the record's stream.
   */
  private void handleSourceEmittedRecord(final AirbyteRecordMessage recordMessage) {
    final short streamIndex = getStreamIndex(recordMessage.getStream());

    final long currentRunningCount = runningCountByStream.getOrDefault(streamIndex, 0L);
    this.runningCountByStream.put(streamIndex, currentRunningCount + 1);

    final long currentTotalCount = totalRecordsEmittedByStream.getOrDefault(streamIndex, 0L);
    this.totalRecordsEmittedByStream.put(streamIndex, currentTotalCount + 1);

    // todo (cgardens) - pretty wasteful to do an extra serialization just to get size.
    final int numBytes = Jsons.serialize(recordMessage.getData()).getBytes(Charsets.UTF_8).length;
    final long currentTotalStreamBytes = totalBytesEmittedByStream.getOrDefault(streamIndex, 0L);
    this.totalBytesEmittedByStream.put(streamIndex, currentTotalStreamBytes + numBytes);
  }

  /**
   * When a source emits a state, persist the current running count per stream to the {@link StateDeltaTracker}. Then, reset the running count per
   * stream so that new counts can start recording for the next state. Also add the state to list so that state order is tracked correctly.
   */
  private void handleSourceEmittedState(final AirbyteStateMessage stateMessage) {
    sourceOutputState.set(new State().withState(stateMessage.getData()));
    final int stateHash = getStateHashCode(stateMessage);
    try {
      if (!exceededDeltaTrackerCapacity) {
        stateDeltaTracker.addState(stateHash, runningCountByStream);
      }
    } catch (final CapacityExceededException e) {
      log.warn("Exceeded stateDeltaTracker capacity, no longer able to compute committed record counts");
      exceededDeltaTrackerCapacity = true;
    }
    runningCountByStream.clear();
    orderedStateHashes.add(stateHash);
  }

  /**
   * When a destination emits a state, mark all uncommitted states up to and including this state as committed in the {@link StateDeltaTracker}. Also
   * record this state as the last committed state.
   */
  private void handleDestinationEmittedState(final AirbyteStateMessage stateMessage) {
    destinationOutputState.set(new State().withState(stateMessage.getData()));

    final int emittedStateHash = getStateHashCode(stateMessage);
    int nextStateHash;

    // do-while because we want to execute the loop body exactly once in cases where the next state hash
    // to commit is the emitted state hash.
    do {
      nextStateHash = orderedStateHashes.get(nextStateIndexToCommit);
      stateDeltaTracker.commitStateHash(nextStateHash);
      nextStateIndexToCommit++;
    } while (nextStateHash != emittedStateHash);
  }

  private short getStreamIndex(final String streamName) {
    if (!streamIndexByName.containsKey(streamName)) {
      streamIndexByName.put(streamName, nextStreamIndex);
      nextStreamIndex++;
    }
    return streamIndexByName.get(streamName);
  }

  private int getStateHashCode(final AirbyteStateMessage stateMessage) {
    return hashFunction.hashBytes(Jsons.serialize(stateMessage.getData()).getBytes(Charsets.UTF_8)).hashCode();
  }

  @Override
  public Optional<State> getSourceOutputState() {
    return Optional.ofNullable(sourceOutputState.get());
  }

  @Override
  public Optional<State> getDestinationOutputState() {
    return Optional.ofNullable(destinationOutputState.get());
  }

  /**
   * Fetch committed stream index to record count from the {@link StateDeltaTracker}. Then, swap out stream indices for stream names.
   * If the delta tracker has exceeded its capacity, return empty because committed record counts cannot be reliably computed.
   */
  @Override
  public Optional<Map<String, Long>> getCommittedRecordsByStream() {
    if (exceededDeltaTrackerCapacity) {
      return Optional.empty();
    }
    final Map<Short, Long> streamIndexToCommittedRecordCount = this.stateDeltaTracker.getStreamIndexToTotalRecordCount(true);
    return Optional.of(
        streamIndexToCommittedRecordCount.entrySet().stream().collect(
            Collectors.toMap(
                entry -> streamIndexByName.inverse().get(entry.getKey()),
                Map.Entry::getValue
            ))
    );
  }

  /**
   * Swap out stream indices for stream names and return total records emitted by stream.
   */
  @Override
  public Map<String, Long> getEmittedRecordsByStream() {
    return totalRecordsEmittedByStream.entrySet().stream().collect(Collectors.toMap(
        entry -> streamIndexByName.inverse().get(entry.getKey()),
        Map.Entry::getValue
    ));
  }

  /**
   * Compute sum of emitted record counts across all streams.
   */
  @Override
  public Long getTotalRecordsEmitted() {
    return totalRecordsEmittedByStream.values().stream().reduce(0L, Long::sum);
  }

  /**
   * Compute sum of emitted bytes across all streams.
   */
  @Override
  public Long getTotalBytesEmitted() {
    return totalBytesEmittedByStream.values().stream().reduce(0L, Long::sum);
  }

  /**
   * Compute sum of committed record counts across all streams.
   * If the delta tracker has exceeded its capacity, return empty because committed record counts cannot be reliably computed.
   */
  @Override
  public Optional<Long> getTotalRecordsCommitted() {
    if (exceededDeltaTrackerCapacity) {
      return Optional.empty();
    }
    return Optional.of(stateDeltaTracker.getStreamIndexToTotalRecordCount(true).values().stream().reduce(0L, Long::sum));
  }
}
