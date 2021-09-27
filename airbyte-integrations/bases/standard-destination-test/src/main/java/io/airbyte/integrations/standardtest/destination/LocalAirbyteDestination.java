/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination;

import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.protocols.airbyte.AirbyteDestination;
import java.nio.file.Path;
import java.util.Optional;

// Simple class to host a Destination in-memory rather than spinning up a container for it.
// For debugging and testing purposes only; not recommended to use this for real code
public class LocalAirbyteDestination implements AirbyteDestination {

  private Destination dest;
  private AirbyteMessageConsumer consumer;
  private boolean isClosed = false;

  public LocalAirbyteDestination(Destination dest) {
    this.dest = dest;
  }

  @Override
  public void start(WorkerDestinationConfig destinationConfig, Path jobRoot) throws Exception {
    consumer =
        dest.getConsumer(destinationConfig.getDestinationConnectionConfiguration(), destinationConfig.getCatalog(),
            Destination::defaultOutputRecordCollector);
    consumer.start();
  }

  @Override
  public void accept(AirbyteMessage message) throws Exception {
    consumer.accept(message);
  }

  @Override
  public void notifyEndOfStream() {
    // nothing to do here
  }

  @Override
  public void close() throws Exception {
    consumer.close();
    isClosed = true;
  }

  @Override
  public void cancel() {
    // nothing to do here
  }

  @Override
  public boolean isFinished() {
    return isClosed;
  }

  @Override
  public Optional<AirbyteMessage> attemptRead() {
    return Optional.empty();
  }

}
