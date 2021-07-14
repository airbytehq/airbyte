package io.airbyte.integrations.destination.rockset;

import com.fasterxml.jackson.databind.JsonNode;
import com.rockset.client.RocksetClient;
import com.rockset.client.model.AddDocumentsRequest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;

import java.util.UUID;
import java.util.function.Consumer;
import static io.airbyte.integrations.destination.rockset.RocksetUtils.APISERVER_URL;
import static io.airbyte.integrations.destination.rockset.RocksetUtils.API_KEY_ID;

public class RocksetWriteApiConsumer implements AirbyteMessageConsumer {

  private final String apiKey;
  private final String workspace;

  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;

  private RocksetClient client;

  public RocksetWriteApiConsumer(JsonNode config,
                                 ConfiguredAirbyteCatalog catalog,
                                 Consumer<AirbyteMessage> outputRecordCollector) {
    this.apiKey = config.get(API_KEY_ID).asText();
    this.workspace = config.get(API_KEY_ID).asText();

    this.catalog = catalog;
    this.outputRecordCollector = outputRecordCollector;
  }

  @Override
  public void start() throws Exception {
    this.client = new RocksetClient(apiKey, APISERVER_URL);

    RocksetUtils.createWorkspaceIfNotExists(client, workspace);
  }

  @Override
  public void accept(AirbyteMessage message) throws Exception {
    AddDocumentsRequest req = new AddDocumentsRequest();
    req.addDataItem(message);

    // TODO Get desired collection name from somewhere inside AirbyteMessage
    this.client.addDocuments(workspace, "TODO-real-collection", req);
  }

  @Override
  public void close() throws Exception {
    // Nothing to do
  }
}
