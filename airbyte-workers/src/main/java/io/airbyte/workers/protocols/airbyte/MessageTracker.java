/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols.airbyte;

import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteMessage;
import java.util.Optional;
import java.util.function.Consumer;

/**
 * Interface to handle extracting metadata from the stream of data flowing from a Source to a
 * Destination.
 */
public interface MessageTracker extends Consumer<AirbyteMessage> {

  /**
   * Accepts an AirbyteMessage and tracks any metadata about it that is required by the Platform.
   *
   * @param message message to derive metadata from.
   */
  @Override
  void accept(AirbyteMessage message);

  /**
   * Gets the records replicated.
   *
   * @return total records that passed from Source to Destination.
   */
  long getRecordCount();

  /**
   * Gets the bytes replicated.
   *
   * @return total bytes that passed from Source to Destination.
   */
  long getBytesCount();

  /**
   * Get the current state of the stream.
   *
   * @return returns the last StateMessage that was accepted. If no StateMessage was accepted, empty.
   */
  Optional<State> getOutputState();

}
