package io.airbyte.integrations.base.destination.typing_deduping;

import static io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest.convertProtocolObject;

import io.airbyte.commons.lang.Exceptions;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.workers.internal.AirbyteDestination;

public class DestinationProcess implements AutoCloseable {

  private final AirbyteDestination destination;

  public DestinationProcess(AirbyteDestination destination) {
    this.destination = destination;
  }

  public void accept(AirbyteMessage message) {
    Exceptions.toRuntime(() -> destination.accept(convertProtocolObject(message, io.airbyte.protocol.models.AirbyteMessage.class)));
  }

  @Override
  public void close() throws Exception {
    destination.notifyEndOfInput();
    while (!destination.isFinished()) {
      destination.attemptRead();
    }

    destination.close();
  }
}
