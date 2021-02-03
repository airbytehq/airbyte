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

package io.airbyte.integrations.destination.meilisearch;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.text.Names;
import io.airbyte.integrations.DefaultSpecConnector;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.DestinationConsumer;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.WriteConfig;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer;
import io.airbyte.integrations.destination.jdbc.JdbcBufferedConsumerFactory;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.meilisearch.sdk.Client;
import com.meilisearch.sdk.Config;
import com.meilisearch.sdk.Index;

public class MeiliSearchDestination extends DefaultSpecConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MeiliSearchDestination.class);

  // todo (cgardens) - why is this in the Destination interface as opposed to in the JdbcDestination?
  @Override
  public NamingConventionTransformer getNamingTransformer() {
    return null;
  }

  @Override
  public DestinationConsumer<AirbyteMessage> write(JsonNode config, ConfiguredAirbyteCatalog catalog) throws Exception {
    final Client client = getClient(config);
    createIndices(catalog, client);

    return new BufferedStreamConsumer(
        () -> LOGGER.info("Starting write to MeiliSearch."),
        recordWriterFunction(database, sqlOperations, writeConfigs, catalog),
        () -> LOGGER.info("Completed writing to MeiliSearch."),
        catalog,
        getStreamNames(catalog);
  }

  private static List<Index> createIndices(ConfiguredAirbyteCatalog catalog, Client client) throws Exception {
    List<Index> list = new ArrayList<>();
    for (String streamName : getStreamNames(catalog)) {
      Index index = client.index(streamName);
      list.add(index);
    }
    return list;
  }

  private static Set<String> getStreamNames(ConfiguredAirbyteCatalog catalog) {
    return catalog.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .map(AirbyteStream::getName)
        .map(Names::toAlphanumericAndUnderscore)
        .collect(Collectors.toSet());
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) throws Exception {
    try {
      final Client client = getClient(config);
      final Index index = client.index("_airbyte");
      index.addDocuments("[{\"id\": \"_airbyte\" }]");
      index.search("_airbyte");
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (Exception e) {
      LOGGER.error("Check connection failed.", e);
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage("Check connection failed: "+ e.getMessage());
    }
  }

  private static Client getClient(JsonNode config) {
    return new Client(new Config("http://localhost:7700", null));
//    return new Client(new Config(config.get("host").asText(), config.has("api_key") ? config.get("api_key").asText() : null));
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new MeiliSearchDestination();
    LOGGER.info("spec result {}", Jsons.serialize(destination.check(Jsons.emptyObject())));
//    LOGGER.info("starting destination: {}", MeiliSearchDestination.class);
//    new IntegrationRunner(destination).run(args);
//    LOGGER.info("completed destination: {}", MeiliSearchDestination.class);
  }

//  public static void main(String[] args) throws Exception {
//    final String documents = "["
//        + "{\"book_id\": 123, \"title\": \"Pride and Prejudice\"},"
//        + "{\"book_id\": 456, \"title\": \"Le Petit Prince\"},"
//        + "{\"book_id\": 1, \"title\": \"Alice In Wonderland\"},"
//        + "{\"book_id\": 1344, \"title\": \"The Hobbit\"},"
//        + "{\"book_id\": 4, \"title\": \"Harry Potter and the Half-Blood Prince\"},"
//        + "{\"book_id\": 2, \"title\": \"The Hitchhiker\'s Guide to the Galaxy\"}"
//        + "]";
//
//    Client client = new Client(new Config("http://localhost:7700", "masterKey"));
//
//    // An index is where the documents are stored.
//    Index index = client.index("books");
//
//    // If the index 'books' does not exist, MeiliSearch creates it when you first add the documents.
////    index.addDocuments(documents); // => { "updateId": 0 }
//
//    System.out.println(index.search("petit"));
//    System.out.println(index.search("pett"));
//    System.out.println(index.search("halfblood"));
//    System.out.println(index.search("halfblood"));
//    System.out.println(index.search("1344"));
//  }

}
