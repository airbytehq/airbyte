/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal.book_keeping;

import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.StreamDescriptor;
import java.nio.ByteBuffer;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;

public class StateMetricsTracker {

  private static final int STATE_HASH_SIZE = Integer.BYTES;
  private static final int EPOCH_TIME_SIZE = Long.BYTES;
  private static final int BYTE_ARRAY_SIZE = STATE_HASH_SIZE + EPOCH_TIME_SIZE;

  private final List<byte[]> stateHashesAndTimestamps;
  private final Map<String, List<byte[]>> streamStateHashesAndTimestamps;
  private LocalDateTime firstRecordReceivedAt;
  private LocalDateTime lastStateMessageReceivedAt;
  private Long maxSecondsToReceiveSourceStateMessage;
  private Long meanSecondsToReceiveSourceStateMessage;
  private Long maxSecondsBetweenStateMessageEmittedandCommitted;
  private Long meanSecondsBetweenStateMessageEmittedandCommitted;
  private final AtomicLong totalSourceEmittedStateMessages;
  private final AtomicLong totalDestinationEmittedStateMessages;
  private long remainingCapacity;
  private Boolean capacityExceeded;

  public StateMetricsTracker(final Long messageLimit) {
    this.stateHashesAndTimestamps = new ArrayList<>();
    this.streamStateHashesAndTimestamps = new HashMap<>();
    this.firstRecordReceivedAt = null;
    this.lastStateMessageReceivedAt = null;
    this.maxSecondsToReceiveSourceStateMessage = 0L;
    this.meanSecondsToReceiveSourceStateMessage = 0L;
    this.maxSecondsBetweenStateMessageEmittedandCommitted = 0L;
    this.meanSecondsBetweenStateMessageEmittedandCommitted = 0L;
    this.totalSourceEmittedStateMessages = new AtomicLong(0L);
    this.totalDestinationEmittedStateMessages = new AtomicLong(0L);
    this.remainingCapacity = messageLimit;
    this.capacityExceeded = false;
  }

  public synchronized void addState(final AirbyteStateMessage stateMessage, final int stateHash, final LocalDateTime timeEmitted)
      throws StateMetricsTrackerOomException {
    final long epochTime = timeEmitted.toEpochSecond(ZoneOffset.UTC);

    if (capacityExceeded || remainingCapacity < 1) {
      capacityExceeded = true;
      throw new StateMetricsTrackerOomException("Memory capacity is exceeded for StateMetricsTracker.");
    }

    if (AirbyteStateType.STREAM == stateMessage.getType()) {
      addStateMessageToStreamToStateHashTimestampTracker(stateMessage, stateHash, epochTime);
    } else {
      // do not track state message timestamps per stream for GLOBAL or LEGACY state
      final byte[] stateTimestampByteArray = populateStateTimestampByteArray(stateHash, epochTime);
      stateHashesAndTimestamps.add(stateTimestampByteArray);
      remainingCapacity -= 1;
    }
  }

  public synchronized void updateStates(final AirbyteStateMessage stateMessage, final int stateHash, final LocalDateTime timeCommitted)
      throws StateMetricsTrackerNoStateMatchException {
    final LocalDateTime startingTime;
    if (AirbyteStateType.STREAM == stateMessage.getType()) {
      final String streamDescriptorKey = getStreamDescriptorKey(stateMessage.getStream().getStreamDescriptor());
      final List<byte[]> stateMessagesForStream = streamStateHashesAndTimestamps.get(streamDescriptorKey);
      startingTime = findStartingTimeStampAndRemoveOlderEntries(stateMessagesForStream, stateHash);
    } else {
      startingTime = findStartingTimeStampAndRemoveOlderEntries(stateHashesAndTimestamps, stateHash);
    }
    updateMaxAndMeanSeconds(startingTime, timeCommitted);
  }

  void addStateMessageToStreamToStateHashTimestampTracker(final AirbyteStateMessage stateMessage,
                                                          final int stateHash,
                                                          final Long epochTimeEmitted) {
    final String streamDescriptorKey = getStreamDescriptorKey(stateMessage.getStream().getStreamDescriptor());
    final byte[] stateHashAndTimestamp = populateStateTimestampByteArray(stateHash, epochTimeEmitted);

    if (streamStateHashesAndTimestamps.get(streamDescriptorKey) == null) {
      final List stateHashesAndTimestamps = new ArrayList<>();
      stateHashesAndTimestamps.add(stateHashAndTimestamp);
      streamStateHashesAndTimestamps.put(streamDescriptorKey, stateHashesAndTimestamps);
    } else {
      final List<byte[]> streamDescriptorValue = streamStateHashesAndTimestamps.get(streamDescriptorKey);
      streamDescriptorValue.add(stateHashAndTimestamp);
    }
    remainingCapacity -= 1;
  }

  @SuppressWarnings("PMD.AvoidLiteralsInIfCondition")
  void updateMaxAndMeanSeconds(final LocalDateTime startingTime, final LocalDateTime timeCommitted) {
    final Long secondsUntilCommit = calculateSecondsBetweenStateEmittedAndCommitted(startingTime, timeCommitted);
    if (maxSecondsBetweenStateMessageEmittedandCommitted < secondsUntilCommit) {
      maxSecondsBetweenStateMessageEmittedandCommitted = secondsUntilCommit;
    }

    if (totalDestinationEmittedStateMessages.get() == 1) {
      meanSecondsBetweenStateMessageEmittedandCommitted = secondsUntilCommit;
    } else {
      final Long newMeanSeconds =
          calculateMean(meanSecondsBetweenStateMessageEmittedandCommitted, totalDestinationEmittedStateMessages.get(), secondsUntilCommit);
      meanSecondsBetweenStateMessageEmittedandCommitted = newMeanSeconds;
    }
  }

  private LocalDateTime findStartingTimeStampAndRemoveOlderEntries(final List<byte[]> stateList, final int stateHash)
      throws StateMetricsTrackerNoStateMatchException {
    // iterate through each [state_hash, timestamp] in the list
    // update the first timestamp to equal min_timestamp
    // and remove all items from the list as we iterate through
    // break once we reach the state hash equal to the input(destination) state hash
    Boolean foundStateHash = false;
    Long minTime = null;
    final Iterator<byte[]> iterator = stateList.iterator();
    while (iterator.hasNext()) {
      final byte[] stateMessageTime = iterator.next();
      final ByteBuffer current = ByteBuffer.wrap(stateMessageTime);
      remainingCapacity += 1;
      final int currentStateHash = current.getInt();
      final Long epochTime = current.getLong();
      if (minTime == null) {
        minTime = epochTime;
      }
      iterator.remove();

      if (stateHash == currentStateHash) {
        foundStateHash = true;
        break;
      }
    }

    if (!foundStateHash || minTime == null) {
      throw new StateMetricsTrackerNoStateMatchException("Destination state message cannot be matched to corresponding Source state message.");
    }
    return LocalDateTime.ofEpochSecond(minTime, 0, ZoneOffset.UTC);
  }

  Long calculateSecondsBetweenStateEmittedAndCommitted(final LocalDateTime stateMessageEmittedAt, final LocalDateTime stateMessageCommittedAt) {
    return stateMessageEmittedAt.until(stateMessageCommittedAt, ChronoUnit.SECONDS);
  }

  protected Long calculateMean(final Long currentMean, final Long totalCount, final Long newDataPoint) {
    final Long previousCount = totalCount - 1;
    final double result = (Double.valueOf(currentMean * previousCount) / totalCount) + (Double.valueOf(newDataPoint) / totalCount);
    return (long) result;
  }

  public void updateMaxAndMeanSecondsToReceiveStateMessage(final LocalDateTime stateMessageReceivedAt) {
    final Long secondsSinceLastStateMessage = calculateSecondsSinceLastStateEmitted(stateMessageReceivedAt);
    if (maxSecondsToReceiveSourceStateMessage < secondsSinceLastStateMessage) {
      maxSecondsToReceiveSourceStateMessage = secondsSinceLastStateMessage;
    }

    if (meanSecondsToReceiveSourceStateMessage == 0) {
      meanSecondsToReceiveSourceStateMessage = secondsSinceLastStateMessage;
    } else {
      final Long newMeanSeconds =
          calculateMean(meanSecondsToReceiveSourceStateMessage, totalSourceEmittedStateMessages.get(), secondsSinceLastStateMessage);
      meanSecondsToReceiveSourceStateMessage = newMeanSeconds;
    }
  }

  private Long calculateSecondsSinceLastStateEmitted(final LocalDateTime stateMessageReceivedAt) {
    if (lastStateMessageReceivedAt != null) {
      return lastStateMessageReceivedAt.until(stateMessageReceivedAt, ChronoUnit.SECONDS);
    } else if (firstRecordReceivedAt != null) {
      return firstRecordReceivedAt.until(stateMessageReceivedAt, ChronoUnit.SECONDS);
    } else {
      // If we receive a State Message before a Record Message there is no previous timestamp to use for a
      // calculation
      return 0L;
    }
  }

  public LocalDateTime getFirstRecordReceivedAt() {
    return firstRecordReceivedAt;
  }

  public void setFirstRecordReceivedAt(final LocalDateTime receivedAt) {
    firstRecordReceivedAt = receivedAt;
  }

  public void setLastStateMessageReceivedAt(final LocalDateTime receivedAt) {
    lastStateMessageReceivedAt = receivedAt;
  }

  public void incrementTotalSourceEmittedStateMessages() {
    totalSourceEmittedStateMessages.incrementAndGet();
  }

  public Long getTotalSourceStateMessageEmitted() {
    return totalSourceEmittedStateMessages.get();
  }

  public Long getTotalDestinationStateMessageEmitted() {
    return totalDestinationEmittedStateMessages.get();
  }

  public Long getMaxSecondsToReceiveSourceStateMessage() {
    return maxSecondsToReceiveSourceStateMessage;
  }

  public Long getMeanSecondsToReceiveSourceStateMessage() {
    return meanSecondsToReceiveSourceStateMessage;
  }

  public Long getMaxSecondsBetweenStateMessageEmittedAndCommitted() {
    return maxSecondsBetweenStateMessageEmittedandCommitted;
  }

  public Long getMeanSecondsBetweenStateMessageEmittedAndCommitted() {
    return meanSecondsBetweenStateMessageEmittedandCommitted;
  }

  protected void incrementTotalDestinationEmittedStateMessages() {
    totalDestinationEmittedStateMessages.incrementAndGet();
  }

  private byte[] populateStateTimestampByteArray(final int stateHash, final Long epochTime) {
    // allocate num of bytes of state hash + num bytes of epoch time long
    final ByteBuffer delta = ByteBuffer.allocate(BYTE_ARRAY_SIZE);
    delta.putInt(stateHash);
    delta.putLong(epochTime);
    return delta.array();
  }

  private String getStreamDescriptorKey(final StreamDescriptor streamDescriptor) {
    return streamDescriptor.getName() + "-" + streamDescriptor.getNamespace();
  }

  /**
   * Thrown when the StateMetricsTracker exceeds its allotted memory
   */
  public static class StateMetricsTrackerOomException extends Exception {

    public StateMetricsTrackerOomException(final String message) {
      super(message);
    }

  }

  /**
   * Thrown when the destination state message is not able to be matched to a source state message
   */
  public static class StateMetricsTrackerNoStateMatchException extends Exception {

    public StateMetricsTrackerNoStateMatchException(final String message) {
      super(message);
    }

  }

}
