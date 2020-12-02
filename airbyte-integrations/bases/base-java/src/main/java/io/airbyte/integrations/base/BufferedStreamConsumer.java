package io.airbyte.integrations.base;

import io.airbyte.protocol.models.AirbyteMessage;
import java.util.Map;

public class BufferedStreamConsumer extends FailureTrackingConsumer<AirbyteMessage> implements DestinationConsumerStrategy {

  private final DestinationDialect destinationConsumer;

  public BufferedStreamConsumer(DestinationDialect destinationConsumer) {
    this.destinationConsumer = destinationConsumer;
  }

  @Override
  public void setContext(Map<String, DestinationWriteContext> configs) {
    destinationConsumer.setContext(configs);
  }

  @Override
  protected void acceptTracked(AirbyteMessage airbyteMessage) throws Exception {

  }

  @Override
  protected void close(boolean hasFailed) throws Exception {

  }
}
