/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Charsets;
import com.google.common.collect.BiMap;
import com.google.common.collect.HashBiMap;
import com.google.common.hash.HashFunction;
import com.google.common.hash.Hashing;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.FailureReason;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import io.airbyte.workers.helper.FailureHelper;
import io.airbyte.workers.internal.state_aggregator.DefaultStateAggregator;
import io.airbyte.workers.internal.state_aggregator.StateAggregator;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class AirbyteMessageTracker implements MessageTracker {

  private static final long STATE_DELTA_TRACKER_MEMORY_LIMIT_BYTES = 20L * 1024L * 1024L; // 20 MiB, ~10% of default cloud worker memory

  private final AtomicReference<State> sourceOutputState;
  private final AtomicReference<State> destinationOutputState;
  private final AtomicLong totalSourceEmittedStateMessages;
  private final AtomicLong totalDestinationEmittedStateMessages;
  private final Map<Short, Long> streamToRunningCount;
  private final HashFunction hashFunction;
  private final BiMap<String, Short> streamNameToIndex;
  private final Map<Short, Long> streamToTotalBytesEmitted;
  private final Map<Short, Long> streamToTotalRecordsEmitted;
  private final StateDeltaTracker stateDeltaTracker;
  private final List<AirbyteTraceMessage> destinationErrorTraceMessages;
  private final List<AirbyteTraceMessage> sourceErrorTraceMessages;
  private final StateAggregator stateAggregator;

  private short nextStreamIndex;

  /**
   * If the StateDeltaTracker throws an exception, this flag is set to true and committed counts are
   * not returned.
   */
  private boolean unreliableCommittedCounts;

  private enum ConnectorType {
    SOURCE,
    DESTINATION
  }

  public AirbyteMessageTracker() {
    this(new StateDeltaTracker(STATE_DELTA_TRACKER_MEMORY_LIMIT_BYTES),
        new DefaultStateAggregator(new EnvVariableFeatureFlags().useStreamCapableState()));
  }

  @VisibleForTesting
  protected AirbyteMessageTracker(final StateDeltaTracker stateDeltaTracker, final StateAggregator stateAggregator) {
    this.sourceOutputState = new AtomicReference<>();
    this.destinationOutputState = new AtomicReference<>();
    this.totalSourceEmittedStateMessages = new AtomicLong(0L);
    this.totalDestinationEmittedStateMessages = new AtomicLong(0L);
    this.streamToRunningCount = new HashMap<>();
    this.streamNameToIndex = HashBiMap.create();
    this.hashFunction = Hashing.murmur3_32_fixed();
    this.streamToTotalBytesEmitted = new HashMap<>();
    this.streamToTotalRecordsEmitted = new HashMap<>();
    this.stateDeltaTracker = stateDeltaTracker;
    this.nextStreamIndex = 0;
    this.unreliableCommittedCounts = false;
    this.destinationErrorTraceMessages = new ArrayList<>();
    this.sourceErrorTraceMessages = new ArrayList<>();
    this.stateAggregator = stateAggregator;
  }

  @Override
  public void acceptFromSource(final AirbyteMessage message) {
    switch (message.getType()) {
      case TRACE -> handleEmittedTrace(message.getTrace(), ConnectorType.SOURCE);
      case RECORD -> handleSourceEmittedRecord(message.getRecord());
      case STATE -> handleSourceEmittedState(message.getState());
      default -> log.warn("Invalid message type for message: {}", message);
    }
  }

  @Override
  public void acceptFromDestination(final AirbyteMessage message) {
    switch (message.getType()) {
      case TRACE -> handleEmittedTrace(message.getTrace(), ConnectorType.DESTINATION);
      case STATE -> handleDestinationEmittedState(message.getState());
      default -> log.warn("Invalid message type for message: {}", message);
    }
  }

  /**
   * When a source emits a record, increment the running record count, the total record count, and the
   * total byte count for the record's stream.
   */
  private void handleSourceEmittedRecord(final AirbyteRecordMessage recordMessage) {
    final short streamIndex = getStreamIndex(recordMessage.getStream());

    final long currentRunningCount = streamToRunningCount.getOrDefault(streamIndex, 0L);
    streamToRunningCount.put(streamIndex, currentRunningCount + 1);

    final long currentTotalCount = streamToTotalRecordsEmitted.getOrDefault(streamIndex, 0L);
    streamToTotalRecordsEmitted.put(streamIndex, currentTotalCount + 1);

    final int estimatedNumBytes = Jsons.getEstimatedByteSize(recordMessage.getData());
    final long currentTotalStreamBytes = streamToTotalBytesEmitted.getOrDefault(streamIndex, 0L);
    streamToTotalBytesEmitted.put(streamIndex, currentTotalStreamBytes + estimatedNumBytes);
  }

  /**
   * When a source emits a state, persist the current running count per stream to the
   * {@link StateDeltaTracker}. Then, reset the running count per stream so that new counts can start
   * recording for the next state. Also add the state to list so that state order is tracked
   * correctly.
   */
  private void handleSourceEmittedState(final AirbyteStateMessage stateMessage) {
    sourceOutputState.set(new State().withState(stateMessage.getData()));
    totalSourceEmittedStateMessages.incrementAndGet();
    final int stateHash = getStateHashCode(stateMessage);
    try {
      if (!unreliableCommittedCounts) {
        stateDeltaTracker.addState(stateHash, streamToRunningCount);
      }
    } catch (final StateDeltaTracker.StateDeltaTrackerException e) {
      log.warn("The message tracker encountered an issue that prevents committed record counts from being reliably computed.");
      log.warn("This only impacts metadata and does not indicate a problem with actual sync data.");
      log.warn(e.getMessage(), e);
      unreliableCommittedCounts = true;
    }
    streamToRunningCount.clear();
  }

  /**
   * When a destination emits a state, mark all uncommitted states up to and including this state as
   * committed in the {@link StateDeltaTracker}. Also record this state as the last committed state.
   */
  private void handleDestinationEmittedState(final AirbyteStateMessage stateMessage) {
    totalDestinationEmittedStateMessages.incrementAndGet();
    stateAggregator.ingest(stateMessage);
    destinationOutputState.set(stateAggregator.getAggregated());
    try {
      if (!unreliableCommittedCounts) {
        stateDeltaTracker.commitStateHash(getStateHashCode(stateMessage));
      }
    } catch (final StateDeltaTracker.StateDeltaTrackerException e) {
      log.warn("The message tracker encountered an issue that prevents committed record counts from being reliably computed.");
      log.warn("This only impacts metadata and does not indicate a problem with actual sync data.");
      log.warn(e.getMessage(), e);
      unreliableCommittedCounts = true;
    }
  }

  /**
   * When a connector emits a trace message, check the type and call the correct function. If it is an
   * error trace message, add it to the list of errorTraceMessages for the connector type
   */
  private void handleEmittedTrace(final AirbyteTraceMessage traceMessage, final ConnectorType connectorType) {
    switch (traceMessage.getType()) {
      case ERROR -> handleEmittedErrorTrace(traceMessage, connectorType);
      default -> log.warn("Invalid message type for trace message: {}", traceMessage);
    }
  }

  private void handleEmittedErrorTrace(final AirbyteTraceMessage errorTraceMessage, final ConnectorType connectorType) {
    if (connectorType.equals(ConnectorType.DESTINATION)) {
      destinationErrorTraceMessages.add(errorTraceMessage);
    } else if (connectorType.equals(ConnectorType.SOURCE)) {
      sourceErrorTraceMessages.add(errorTraceMessage);
    }
  }

  private short getStreamIndex(final String streamName) {
    if (!streamNameToIndex.containsKey(streamName)) {
      streamNameToIndex.put(streamName, nextStreamIndex);
      nextStreamIndex++;
    }
    return streamNameToIndex.get(streamName);
  }

  private int getStateHashCode(final AirbyteStateMessage stateMessage) {
    return hashFunction.hashBytes(Jsons.serialize(stateMessage.getData()).getBytes(Charsets.UTF_8)).hashCode();
  }

  @Override
  public AirbyteTraceMessage getFirstSourceErrorTraceMessage() {
    if (!sourceErrorTraceMessages.isEmpty()) {
      return sourceErrorTraceMessages.get(0);
    } else {
      return null;
    }
  }

  @Override
  public AirbyteTraceMessage getFirstDestinationErrorTraceMessage() {
    if (!destinationErrorTraceMessages.isEmpty()) {
      return destinationErrorTraceMessages.get(0);
    } else {
      return null;
    }
  }

  @Override
  public FailureReason errorTraceMessageFailure(final Long jobId, final Integer attempt) {
    final AirbyteTraceMessage sourceMessage = getFirstSourceErrorTraceMessage();
    final AirbyteTraceMessage destinationMessage = getFirstDestinationErrorTraceMessage();

    if (sourceMessage == null && destinationMessage == null) {
      return null;
    }

    if (destinationMessage == null) {
      return FailureHelper.sourceFailure(sourceMessage, jobId, attempt);
    }

    if (sourceMessage == null) {
      return FailureHelper.destinationFailure(destinationMessage, jobId, attempt);
    }

    if (sourceMessage.getEmittedAt() <= destinationMessage.getEmittedAt()) {
      return FailureHelper.sourceFailure(sourceMessage, jobId, attempt);
    } else {
      return FailureHelper.destinationFailure(destinationMessage, jobId, attempt);
    }

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
   * Fetch committed stream index to record count from the {@link StateDeltaTracker}. Then, swap out
   * stream indices for stream names. If the delta tracker has exceeded its capacity, return empty
   * because committed record counts cannot be reliably computed.
   */
  @Override
  public Optional<Map<String, Long>> getStreamToCommittedRecords() {
    if (unreliableCommittedCounts) {
      return Optional.empty();
    }
    final Map<Short, Long> streamIndexToCommittedRecordCount = stateDeltaTracker.getStreamToCommittedRecords();
    return Optional.of(
        streamIndexToCommittedRecordCount.entrySet().stream().collect(
            Collectors.toMap(
                entry -> streamNameToIndex.inverse().get(entry.getKey()),
                Map.Entry::getValue)));
  }

  /**
   * Swap out stream indices for stream names and return total records emitted by stream.
   */
  @Override
  public Map<String, Long> getStreamToEmittedRecords() {
    return streamToTotalRecordsEmitted.entrySet().stream().collect(Collectors.toMap(
        entry -> streamNameToIndex.inverse().get(entry.getKey()),
        Map.Entry::getValue));
  }

  /**
   * Swap out stream indices for stream names and return total bytes emitted by stream.
   */
  @Override
  public Map<String, Long> getStreamToEmittedBytes() {
    return streamToTotalBytesEmitted.entrySet().stream().collect(Collectors.toMap(
        entry -> streamNameToIndex.inverse().get(entry.getKey()),
        Map.Entry::getValue));
  }

  /**
   * Compute sum of emitted record counts across all streams.
   */
  @Override
  public long getTotalRecordsEmitted() {
    return streamToTotalRecordsEmitted.values().stream().reduce(0L, Long::sum);
  }

  /**
   * Compute sum of emitted bytes across all streams.
   */
  @Override
  public long getTotalBytesEmitted() {
    return streamToTotalBytesEmitted.values().stream().reduce(0L, Long::sum);
  }

  /**
   * Compute sum of committed record counts across all streams. If the delta tracker has exceeded its
   * capacity, return empty because committed record counts cannot be reliably computed.
   */
  @Override
  public Optional<Long> getTotalRecordsCommitted() {
    if (unreliableCommittedCounts) {
      return Optional.empty();
    }
    return Optional.of(stateDeltaTracker.getStreamToCommittedRecords().values().stream().reduce(0L, Long::sum));
  }

  @Override
  public Long getTotalSourceStateMessagesEmitted() {
    return totalSourceEmittedStateMessages.get();
  }

  @Override
  public Long getTotalDestinationStateMessagesEmitted() {
    return totalDestinationEmittedStateMessages.get();
  }

}
