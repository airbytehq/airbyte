/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal.book_keeping;

import static io.airbyte.metrics.lib.ApmTraceConstants.WORKER_OPERATION_NAME;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Charsets;
import com.google.common.base.Preconditions;
import com.google.common.collect.BiMap;
import com.google.common.collect.HashBiMap;
import com.google.common.hash.HashFunction;
import com.google.common.hash.Hashing;
import datadog.trace.api.Trace;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.FailureReason;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteControlConnectorConfigMessage;
import io.airbyte.protocol.models.AirbyteControlMessage;
import io.airbyte.protocol.models.AirbyteEstimateTraceMessage;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import io.airbyte.workers.helper.FailureHelper;
import io.airbyte.workers.internal.book_keeping.StateMetricsTracker.StateMetricsTrackerNoStateMatchException;
import io.airbyte.workers.internal.state_aggregator.DefaultStateAggregator;
import io.airbyte.workers.internal.state_aggregator.StateAggregator;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;

/**
 * This class is responsible for stats and metadata tracking surrounding
 * {@link AirbyteRecordMessage}.
 * <p>
 * It is not intended to perform meaningful operations - transforming, mutating, triggering
 * downstream actions etc. - on specific messages.
 */
@Slf4j
public class AirbyteMessageTracker implements MessageTracker {

  private static final long STATE_DELTA_TRACKER_MEMORY_LIMIT_BYTES = 10L * 1024L * 1024L; // 10 MiB, ~5% of default cloud worker memory
  private static final long STATE_METRICS_TRACKER_MESSAGE_LIMIT = 873813L; // 12 bytes per message tracked, maximum of 10MiB of memory

  private final AtomicReference<State> sourceOutputState;
  private final AtomicReference<State> destinationOutputState;
  private final Map<Short, Long> streamToRunningCount;
  private final HashFunction hashFunction;
  private final BiMap<AirbyteStreamNameNamespacePair, Short> nameNamespacePairToIndex;
  private final Map<AirbyteStreamNameNamespacePair, StreamStats> nameNamespacePairToStreamStats;
  private final StateDeltaTracker stateDeltaTracker;
  private final StateMetricsTracker stateMetricsTracker;
  private final List<AirbyteTraceMessage> destinationErrorTraceMessages;
  private final List<AirbyteTraceMessage> sourceErrorTraceMessages;
  private final StateAggregator stateAggregator;
  private final FeatureFlags featureFlags;
  private final boolean featureFlagLogConnectorMsgs;

  // These variables support SYNC level estimates and are meant for sources where stream level
  // estimates are not possible e.g. CDC sources.
  private Long totalRecordsEstimatedSync;
  private Long totalBytesEstimatedSync;

  private short nextStreamIndex;

  /**
   * If the StateDeltaTracker throws an exception, this flag is set to true and committed counts are
   * not returned.
   */
  private boolean unreliableCommittedCounts;
  /**
   * If the StateMetricsTracker throws an exception, this flag is set to true and the metrics around
   * max and mean time between state message emitted and committed are unreliable
   */
  private boolean unreliableStateTimingMetrics;

  private enum ConnectorType {
    SOURCE,
    DESTINATION
  }

  public AirbyteMessageTracker(final FeatureFlags featureFlags) {
    this(new StateDeltaTracker(STATE_DELTA_TRACKER_MEMORY_LIMIT_BYTES),
        new DefaultStateAggregator(featureFlags.useStreamCapableState()),
        new StateMetricsTracker(STATE_METRICS_TRACKER_MESSAGE_LIMIT),
        featureFlags);
  }

  @VisibleForTesting
  protected AirbyteMessageTracker(final StateDeltaTracker stateDeltaTracker,
                                  final StateAggregator stateAggregator,
                                  final StateMetricsTracker stateMetricsTracker,
                                  final FeatureFlags featureFlags) {
    this.sourceOutputState = new AtomicReference<>();
    this.destinationOutputState = new AtomicReference<>();
    this.streamToRunningCount = new HashMap<>();
    this.nameNamespacePairToIndex = HashBiMap.create();
    this.hashFunction = Hashing.murmur3_32_fixed();
    this.nameNamespacePairToStreamStats = new HashMap<>();
    this.stateDeltaTracker = stateDeltaTracker;
    this.stateMetricsTracker = stateMetricsTracker;
    this.nextStreamIndex = 0;
    this.unreliableCommittedCounts = false;
    this.unreliableStateTimingMetrics = false;
    this.destinationErrorTraceMessages = new ArrayList<>();
    this.sourceErrorTraceMessages = new ArrayList<>();
    this.stateAggregator = stateAggregator;
    this.featureFlags = featureFlags;
    this.featureFlagLogConnectorMsgs = featureFlags.logConnectorMessages();
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public void acceptFromSource(final AirbyteMessage message) {
    logMessageAsJSON("source", message);

    switch (message.getType()) {
      case TRACE -> handleEmittedTrace(message.getTrace(), ConnectorType.SOURCE);
      case RECORD -> handleSourceEmittedRecord(message.getRecord());
      case STATE -> handleSourceEmittedState(message.getState());
      case CONTROL -> handleEmittedOrchestratorMessage(message.getControl(), ConnectorType.SOURCE);
      default -> log.warn("Invalid message type for message: {}", message);
    }
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public void acceptFromDestination(final AirbyteMessage message) {
    logMessageAsJSON("destination", message);

    switch (message.getType()) {
      case TRACE -> handleEmittedTrace(message.getTrace(), ConnectorType.DESTINATION);
      case STATE -> handleDestinationEmittedState(message.getState());
      case CONTROL -> handleEmittedOrchestratorMessage(message.getControl(), ConnectorType.DESTINATION);
      default -> log.warn("Invalid message type for message: {}", message);
    }
  }

  /**
   * When a source emits a record, increment the running record count, the total record count, and the
   * total byte count for the record's stream.
   */
  private void handleSourceEmittedRecord(final AirbyteRecordMessage recordMessage) {
    if (stateMetricsTracker.getFirstRecordReceivedAt() == null) {
      stateMetricsTracker.setFirstRecordReceivedAt(LocalDateTime.now());
    }

    final var nameNamespace = AirbyteStreamNameNamespacePair.fromRecordMessage(recordMessage);
    final short streamIndex = getStreamIndex(nameNamespace);

    final long currentRunningCount = streamToRunningCount.getOrDefault(streamIndex, 0L);
    streamToRunningCount.put(streamIndex, currentRunningCount + 1);

    final var currStats = nameNamespacePairToStreamStats.getOrDefault(nameNamespace, new StreamStats());
    currStats.emittedRecords++;

    final int estimatedNumBytes = Jsons.getEstimatedByteSize(recordMessage.getData());
    currStats.emittedBytes += estimatedNumBytes;

    nameNamespacePairToStreamStats.put(nameNamespace, currStats);
  }

  /**
   * When a source emits a state, persist the current running count per stream to the
   * {@link StateDeltaTracker}. Then, reset the running count per stream so that new counts can start
   * recording for the next state. Also add the state to list so that state order is tracked
   * correctly.
   */
  private void handleSourceEmittedState(final AirbyteStateMessage stateMessage) {
    final LocalDateTime timeEmittedStateMessage = LocalDateTime.now();
    stateMetricsTracker.incrementTotalSourceEmittedStateMessages();
    stateMetricsTracker.updateMaxAndMeanSecondsToReceiveStateMessage(timeEmittedStateMessage);
    stateMetricsTracker.setLastStateMessageReceivedAt(timeEmittedStateMessage);
    sourceOutputState.set(new State().withState(stateMessage.getData()));
    final int stateHash = getStateHashCode(stateMessage);

    try {
      if (!unreliableCommittedCounts) {
        stateDeltaTracker.addState(stateHash, streamToRunningCount);
      }
      if (!unreliableStateTimingMetrics) {
        stateMetricsTracker.addState(stateMessage, stateHash, timeEmittedStateMessage);
      }
    } catch (final StateDeltaTracker.StateDeltaTrackerException e) {
      log.warn("The message tracker encountered an issue that prevents committed record counts from being reliably computed.");
      log.warn("This only impacts metadata and does not indicate a problem with actual sync data.");
      log.warn(e.getMessage(), e);
      unreliableCommittedCounts = true;
    } catch (final StateMetricsTracker.StateMetricsTrackerOomException e) {
      log.warn("The StateMetricsTracker encountered an out of memory error that prevents new state metrics from being recorded");
      log.warn("This only affects metrics and does not indicate a problem with actual sync data.");
      unreliableStateTimingMetrics = true;
    }
    streamToRunningCount.clear();
  }

  /**
   * When a destination emits a state, mark all uncommitted states up to and including this state as
   * committed in the {@link StateDeltaTracker}. Also record this state as the last committed state.
   */
  private void handleDestinationEmittedState(final AirbyteStateMessage stateMessage) {
    final LocalDateTime timeCommitted = LocalDateTime.now();
    stateMetricsTracker.incrementTotalDestinationEmittedStateMessages();
    stateAggregator.ingest(stateMessage);
    destinationOutputState.set(stateAggregator.getAggregated());
    final int stateHash = getStateHashCode(stateMessage);

    try {
      if (!unreliableCommittedCounts) {
        stateDeltaTracker.commitStateHash(stateHash);
      }
    } catch (final StateDeltaTracker.StateDeltaTrackerException e) {
      log.warn("The message tracker encountered an issue that prevents committed record counts from being reliably computed.");
      log.warn("This only impacts metadata and does not indicate a problem with actual sync data.");
      log.warn(e.getMessage(), e);
      unreliableCommittedCounts = true;
    }

    try {
      if (!unreliableStateTimingMetrics) {
        stateMetricsTracker.updateStates(stateMessage, stateHash, timeCommitted);
      }
    } catch (final StateMetricsTrackerNoStateMatchException e) {
      log.warn("The state message tracker was unable to match the destination state message to a corresponding source state message.");
      log.warn("This only impacts metrics and does not indicate a problem with actual sync data.");
      log.warn(e.getMessage(), e);
      unreliableStateTimingMetrics = true;
    }
  }

  /**
   * When a connector signals that the platform should update persist an update
   */
  private void handleEmittedOrchestratorMessage(final AirbyteControlMessage controlMessage, final ConnectorType connectorType) {
    switch (controlMessage.getType()) {
      case CONNECTOR_CONFIG -> handleEmittedOrchestratorConnectorConfig(controlMessage.getConnectorConfig(), connectorType);
      default -> log.warn("Invalid orchestrator message type for message: {}", controlMessage);
    }
  }

  /**
   * When a connector needs to update its configuration
   */
  @SuppressWarnings("PMD") // until method is implemented
  private void handleEmittedOrchestratorConnectorConfig(final AirbyteControlConnectorConfigMessage configMessage,
                                                        final ConnectorType connectorType) {
    // Config updates are being persisted as part of the DefaultReplicationWorker.
    // In the future, we could add tracking of these kinds of messages here. Nothing to do for now.
  }

  /**
   * When a connector emits a trace message, check the type and call the correct function. If it is an
   * error trace message, add it to the list of errorTraceMessages for the connector type
   */
  private void handleEmittedTrace(final AirbyteTraceMessage traceMessage, final ConnectorType connectorType) {
    switch (traceMessage.getType()) {
      case ESTIMATE -> handleEmittedEstimateTrace(traceMessage.getEstimate());
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

  /**
   * There are several assumptions here:
   * <p>
   * - Assume the estimate is a whole number and not a sum i.e. each estimate replaces the previous
   * estimate.
   * <p>
   * - Sources cannot emit both STREAM and SYNC estimates in a same sync. Error out if this happens.
   */
  @SuppressWarnings("PMD.AvoidDuplicateLiterals")
  private void handleEmittedEstimateTrace(final AirbyteEstimateTraceMessage estimate) {
    switch (estimate.getType()) {
      case STREAM -> {
        Preconditions.checkArgument(totalBytesEstimatedSync == null, "STREAM and SYNC estimates should not be emitted in the same sync.");
        Preconditions.checkArgument(totalRecordsEstimatedSync == null, "STREAM and SYNC estimates should not be emitted in the same sync.");

        log.debug("Saving stream estimates for namespace: {}, stream: {}", estimate.getNamespace(), estimate.getName());
        final var nameNamespace = new AirbyteStreamNameNamespacePair(estimate.getName(), estimate.getNamespace());
        final var currStats = nameNamespacePairToStreamStats.getOrDefault(nameNamespace, new StreamStats());
        currStats.estimatedRecords = estimate.getRowEstimate();
        currStats.estimatedBytes = estimate.getByteEstimate();
        nameNamespacePairToStreamStats.put(nameNamespace, currStats);
      }
      case SYNC -> {
        Preconditions.checkArgument(nameNamespacePairToStreamStats.isEmpty(), "STREAM and SYNC estimates should not be emitted in the same sync.");

        log.debug("Saving sync estimates");
        totalBytesEstimatedSync = estimate.getByteEstimate();
        totalRecordsEstimatedSync = estimate.getRowEstimate();
      }
    }

  }

  private short getStreamIndex(final AirbyteStreamNameNamespacePair pair) {
    if (!nameNamespacePairToIndex.containsKey(pair)) {
      nameNamespacePairToIndex.put(pair, nextStreamIndex);
      nextStreamIndex++;
    }
    return nameNamespacePairToIndex.get(pair);
  }

  private int getStateHashCode(final AirbyteStateMessage stateMessage) {
    if (AirbyteStateType.GLOBAL == stateMessage.getType()) {
      return hashFunction.hashBytes(Jsons.serialize(stateMessage.getGlobal()).getBytes(Charsets.UTF_8)).hashCode();
    } else if (AirbyteStateType.STREAM == stateMessage.getType()) {
      return hashFunction.hashBytes(Jsons.serialize(stateMessage.getStream().getStreamState()).getBytes(Charsets.UTF_8)).hashCode();
    } else {
      // state type is LEGACY
      return hashFunction.hashBytes(Jsons.serialize(stateMessage.getData()).getBytes(Charsets.UTF_8)).hashCode();
    }
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
  public Optional<Map<AirbyteStreamNameNamespacePair, Long>> getStreamToCommittedRecords() {
    if (unreliableCommittedCounts) {
      return Optional.empty();
    }
    final Map<Short, Long> streamIndexToCommittedRecordCount = stateDeltaTracker.getStreamToCommittedRecords();
    return Optional.of(
        streamIndexToCommittedRecordCount.entrySet().stream().collect(
            Collectors.toMap(entry -> nameNamespacePairToIndex.inverse().get(entry.getKey()), Entry::getValue)));
  }

  /**
   * Swap out stream indices for stream names and return total records emitted by stream.
   */
  @Override
  public Map<AirbyteStreamNameNamespacePair, Long> getStreamToEmittedRecords() {
    return nameNamespacePairToStreamStats.entrySet().stream().collect(Collectors.toMap(
        Entry::getKey, entry -> entry.getValue().emittedRecords));
  }

  /**
   * Swap out stream indices for stream names and return total records estimated by stream.
   */
  @Override
  public Map<AirbyteStreamNameNamespacePair, Long> getStreamToEstimatedRecords() {
    return nameNamespacePairToStreamStats.entrySet().stream().collect(
        Collectors.toMap(
            Entry::getKey,
            entry -> entry.getValue().estimatedRecords));
  }

  /**
   * Swap out stream indices for stream names and return total bytes emitted by stream.
   */
  @Override
  public Map<AirbyteStreamNameNamespacePair, Long> getStreamToEmittedBytes() {
    return nameNamespacePairToStreamStats.entrySet().stream().collect(Collectors.toMap(
        Entry::getKey,
        entry -> entry.getValue().emittedBytes));
  }

  /**
   * Swap out stream indices for stream names and return total bytes estimated by stream.
   */
  @Override
  public Map<AirbyteStreamNameNamespacePair, Long> getStreamToEstimatedBytes() {
    return nameNamespacePairToStreamStats.entrySet().stream().collect(
        Collectors.toMap(
            Entry::getKey,
            entry -> entry.getValue().estimatedBytes));
  }

  /**
   * Compute sum of emitted record counts across all streams.
   */
  @Override
  public long getTotalRecordsEmitted() {
    return nameNamespacePairToStreamStats.values().stream()
        .map(stats -> stats.emittedRecords)
        .reduce(0L, Long::sum);
  }

  /**
   * Compute sum of estimated record counts across all streams.
   */
  @Override
  public long getTotalRecordsEstimated() {
    if (!nameNamespacePairToStreamStats.isEmpty()) {
      return nameNamespacePairToStreamStats.values().stream()
          .map(e -> e.estimatedRecords)
          .reduce(0L, Long::sum);
    }

    return totalRecordsEstimatedSync;
  }

  /**
   * Compute sum of emitted bytes across all streams.
   */
  @Override
  public long getTotalBytesEmitted() {
    return nameNamespacePairToStreamStats.values().stream()
        .map(e -> e.emittedBytes)
        .reduce(0L, Long::sum);
  }

  /**
   * Compute sum of estimated bytes across all streams.
   */
  @Override
  public long getTotalBytesEstimated() {
    if (!nameNamespacePairToStreamStats.isEmpty()) {
      return nameNamespacePairToStreamStats.values().stream()
          .map(e -> e.estimatedBytes)
          .reduce(0L, Long::sum);
    }

    return totalBytesEstimatedSync;
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
    return stateMetricsTracker.getTotalSourceStateMessageEmitted();
  }

  @Override
  public Long getTotalDestinationStateMessagesEmitted() {
    return stateMetricsTracker.getTotalDestinationStateMessageEmitted();
  }

  @Override
  public Long getMaxSecondsToReceiveSourceStateMessage() {
    return stateMetricsTracker.getMaxSecondsToReceiveSourceStateMessage();
  }

  @Override
  public Long getMeanSecondsToReceiveSourceStateMessage() {
    return stateMetricsTracker.getMeanSecondsToReceiveSourceStateMessage();
  }

  @Override
  public Optional<Long> getMaxSecondsBetweenStateMessageEmittedAndCommitted() {
    if (unreliableStateTimingMetrics) {
      return Optional.empty();
    }

    return Optional.of(stateMetricsTracker.getMaxSecondsBetweenStateMessageEmittedAndCommitted());
  }

  @Override
  public Optional<Long> getMeanSecondsBetweenStateMessageEmittedAndCommitted() {
    if (unreliableStateTimingMetrics) {
      return Optional.empty();
    }

    return Optional.of(stateMetricsTracker.getMeanSecondsBetweenStateMessageEmittedAndCommitted());
  }

  @Override
  public Boolean getUnreliableStateTimingMetrics() {
    return unreliableStateTimingMetrics;
  }

  private void logMessageAsJSON(final String caller, final AirbyteMessage message) {
    if (!featureFlagLogConnectorMsgs) {
      return;
    }

    log.info(caller + " message | " + Jsons.serialize(message));
  }

}
