package io.airbyte.integrations.destination.rockset;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

import java.util.function.Consumer;

public class RocksetWriteApiConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  private final JsonNode config;
  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;

  public RocksetWriteApiConsumer(JsonNode config,
                                 ConfiguredAirbyteCatalog catalog,
                                 Consumer<AirbyteMessage> outputRecordCollector) {
    this.config = config;
    this.catalog = catalog;
    this.outputRecordCollector = outputRecordCollector;
  }

  @Override
  protected void startTracked() throws Exception {

  }

  @Override
  protected void acceptTracked(AirbyteMessage msg) throws Exception {

  }

  @Override
  protected void close(boolean hasFailed) throws Exception {
    // Nothing to do
  }
}
