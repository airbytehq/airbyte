/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.rockset;

import static io.airbyte.integrations.destination.rockset.RocksetUtils.*;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.rockset.client.RocksetClient;
import com.rockset.client.model.AddDocumentsRequest;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.DestinationSyncMode;

import java.util.List;
import java.util.function.Consumer;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RocksetWriteApiConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(RocksetWriteApiConsumer.class);
  private static final ObjectMapper mapper = new ObjectMapper();
  private static final String DEFAULT_COLLECTION_NAME = "default_collection_name";

  private final String apiKey;
  private final String workspace;

  private final ConfiguredAirbyteCatalog catalog;
  private final Consumer<AirbyteMessage> outputRecordCollector;

  private RocksetClient client;

  public RocksetWriteApiConsumer(
      JsonNode config,
      ConfiguredAirbyteCatalog catalog,
      Consumer<AirbyteMessage> outputRecordCollector) {
    this.apiKey = config.get(API_KEY_ID).asText();
    this.workspace = config.get(WORKSPACE_ID).asText();

    this.catalog = catalog;
    this.outputRecordCollector = outputRecordCollector;
  }

  @Override
  public void start() throws Exception {
    this.client = new RocksetClient(apiKey, APISERVER_URL);

    RocksetUtils.createWorkspaceIfNotExists(client, workspace);
    catalog.getStreams()
        .stream()
        .filter(s -> s.getDestinationSyncMode() == DestinationSyncMode.OVERWRITE)
        .forEach(s -> {
          try {
            String cname = cleanCollectionName(s.getStream().getName());
            RocksetUtils.deleteCollectionIfExists(client, workspace, cname);
            RocksetUtils.waitUntilCollectionDeleted(client, workspace, cname);
          } catch (Exception e) {
            throw new RuntimeException(e);
          }
        });

    List<String> collectionNames = catalog.getStreams()
        .stream()
        .map(s -> cleanCollectionName(s.getStream().getName()))
        .collect(Collectors.toList());

    for (String cname : collectionNames) {
      RocksetUtils.createCollectionIfNotExists(client, workspace, cname);
      RocksetUtils.waitUntilCollectionReady(client, workspace, cname);
    }
  }

  private static String cleanCollectionName(String cname) {
    cname = cname.replaceAll("[^a-zA-Z0-9_-]", "");
    if (cname.length() == 0) {
      return DEFAULT_COLLECTION_NAME;
    }

    while (!Character.isDigit(cname.charAt(0)) && !Character.isLetter(cname.charAt(0))) {
      cname = cname.substring(1);

      if (cname.length() == 0) {
        return DEFAULT_COLLECTION_NAME;
      }
    }

    return cname;
  }

  @Override
  public void accept(AirbyteMessage message) throws Exception {
    if (message.getType() == AirbyteMessage.Type.RECORD) {
      String cname = message.getRecord().getStream();

      AddDocumentsRequest req = new AddDocumentsRequest();
      req.addDataItem(mapper.convertValue(message.getRecord().getData(), new TypeReference<>() {

      }));

      this.client.addDocuments(workspace, cname, req);
    } else if (message.getType() == AirbyteMessage.Type.STATE) {
      this.outputRecordCollector.accept(message);
    }
  }

  @Override
  public void close() throws Exception {
    // Nothing to do
  }

}
