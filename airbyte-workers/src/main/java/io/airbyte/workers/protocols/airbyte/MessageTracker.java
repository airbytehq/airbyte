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

  @Override
  void accept(AirbyteMessage message);

  long getRecordCount();

  long getBytesCount();

  Optional<State> getOutputState();

}
