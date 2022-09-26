/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.config.FailureReason;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import java.util.Map;
import java.util.Optional;

/**
 * Interface to handle extracting metadata from the stream of data flowing from a Source to a
 * Destination.
 */
public interface MessageTracker {

  /**
   * Accepts an AirbyteMessage emitted from a source and tracks any metadata about it that is required
   * by the Platform.
   *
   * @param message message to derive metadata from.
   */
  void acceptFromSource(AirbyteMessage message);

  /**
   * Accepts an AirbyteMessage emitted from a destination and tracks any metadata about it that is
   * required by the Platform.
   *
   * @param message message to derive metadata from.
   */
  void acceptFromDestination(AirbyteMessage message);

  /**
   * Get the current source state of the stream.
   *
   * @return returns the last StateMessage that was accepted from the source. If no StateMessage was
   *         accepted, empty.
   */
  Optional<State> getSourceOutputState();

  /**
   * Get the current destination state of the stream.
   *
   * @return returns the last StateMessage that was accepted from the destination. If no StateMessage
   *         was accepted, empty.
   */
  Optional<State> getDestinationOutputState();

  /**
   * Get the per-stream committed record count.
   *
   * @return returns a map of committed record count by stream name. If committed record counts cannot
   *         be computed, empty.
   */
  Optional<Map<String, Long>> getStreamToCommittedRecords();

  /**
   * Get the per-stream emitted record count. This includes messages that were emitted by the source,
   * but never committed by the destination.
   *
   * @return returns a map of emitted record count by stream name.
   */
  Map<String, Long> getStreamToEmittedRecords();

  /**
   * Get the per-stream emitted byte count. This includes messages that were emitted by the source,
   * but never committed by the destination.
   *
   * @return returns a map of emitted record count by stream name.
   */
  Map<String, Long> getStreamToEmittedBytes();

  /**
   * Get the overall emitted record count. This includes messages that were emitted by the source, but
   * never committed by the destination.
   *
   * @return returns the total count of emitted records across all streams.
   */
  long getTotalRecordsEmitted();

  /**
   * Get the overall emitted bytes. This includes messages that were emitted by the source, but never
   * committed by the destination.
   *
   * @return returns the total emitted bytes across all streams.
   */
  long getTotalBytesEmitted();

  /**
   * Get the overall committed record count.
   *
   * @return returns the total count of committed records across all streams. If total committed
   *         record count cannot be computed, empty.
   */
  Optional<Long> getTotalRecordsCommitted();

  /**
   * Get the count of state messages emitted from the source connector.
   *
   * @return returns the total count of state messages emitted from the source.
   */
  Long getTotalSourceStateMessagesEmitted();

  Long getTotalDestinationStateMessagesEmitted();

  Long getMaxSecondsToReceiveSourceStateMessage();

  Long getMeanSecondsToReceiveSourceStateMessage();

  Optional<Long> getMaxSecondsBetweenStateMessageEmittedAndCommitted();

  Optional<Long> getMeanSecondsBetweenStateMessageEmittedAndCommitted();

  AirbyteTraceMessage getFirstDestinationErrorTraceMessage();

  AirbyteTraceMessage getFirstSourceErrorTraceMessage();

  FailureReason errorTraceMessageFailure(Long jobId, Integer attempt);

  Boolean getUnreliableStateTimingMetrics();

}
