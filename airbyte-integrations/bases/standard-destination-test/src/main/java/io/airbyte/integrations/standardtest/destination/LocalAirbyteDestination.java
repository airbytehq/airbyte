/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.WorkerDestinationConfig;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.internal.AirbyteDestination;
import java.nio.file.Path;
import java.util.Optional;

/**
 * Simple class to host a Destination in-memory rather than spinning up a container for it. For
 * debugging and testing purposes only; not recommended to use this for real code
 */
public class LocalAirbyteDestination implements AirbyteDestination {

  private final Destination dest;
  private AirbyteMessageConsumer consumer;
  private boolean isClosed = false;

  public LocalAirbyteDestination(final Destination dest) {
    this.dest = dest;
  }

  @Override
  public void start(final WorkerDestinationConfig destinationConfig, final Path jobRoot) throws Exception {
    consumer =
        dest.getConsumer(destinationConfig.getDestinationConnectionConfiguration(),
            Jsons.object(Jsons.jsonNode(destinationConfig.getCatalog()), io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog.class),
            Destination::defaultOutputRecordCollector);
    consumer.start();
  }

  @Override
  public void accept(final AirbyteMessage message) throws Exception {
    consumer.accept(Jsons.object(Jsons.jsonNode(message), io.airbyte.protocol.models.v0.AirbyteMessage.class));
  }

  @Override
  public void notifyEndOfInput() {
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
  public int getExitValue() {
    return 0;
  }

  @Override
  public Optional<AirbyteMessage> attemptRead() {
    return Optional.empty();
  }

}
