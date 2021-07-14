package io.airbyte.integrations.destination.rockset;

import com.fasterxml.jackson.databind.JsonNode;
import com.rockset.client.RocksetClient;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

import java.util.UUID;
import java.util.function.Consumer;

import static io.airbyte.integrations.destination.rockset.RocksetDestination.APISERVER_URL;
import static io.airbyte.integrations.destination.rockset.RocksetDestination.API_KEY_ID;

public class RocksetWriteApiConsumer implements AirbyteMessageConsumer {

  private final JsonNode config;
  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;

  private RocksetClient client;

  public RocksetWriteApiConsumer(JsonNode config,
                                 ConfiguredAirbyteCatalog catalog,
                                 Consumer<AirbyteMessage> outputRecordCollector) {
    this.config = config;
    this.catalog = catalog;
    this.outputRecordCollector = outputRecordCollector;
  }

  @Override
  public void start() throws Exception {
    String apiKey = config.get(API_KEY_ID).asText();
    this.client = new RocksetClient(apiKey, APISERVER_URL);
  }

  @Override
  public void accept(AirbyteMessage message) throws Exception {
    // TODO
  }

  @Override
  public void close() throws Exception {
    // Nothing to do
  }
}
