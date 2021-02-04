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
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.base.Preconditions;
import com.meilisearch.sdk.Client;
import com.meilisearch.sdk.Config;
import com.meilisearch.sdk.Index;
import io.airbyte.commons.functional.CheckedBiConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.text.Names;
import io.airbyte.integrations.DefaultSpecConnector;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.DestinationConsumer;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.SyncMode;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MeiliSearchDestination extends DefaultSpecConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MeiliSearchDestination.class);

  private static final String AB_PK_PREFIX = "_ab_pk_";

  // todo (cgardens) - why is this in the Destination interface as opposed to in the JdbcDestination?
  @Override
  public NamingConventionTransformer getNamingTransformer() {
    return null;
  }

  @Override
  public DestinationConsumer<AirbyteMessage> write(JsonNode config, ConfiguredAirbyteCatalog catalog) throws Exception {
    final Client client = getClient(config);
    final Map<String, WriteConfig> indexNameToIndex = createIndices(catalog, client);

    return new BufferedStreamConsumer(
        () -> LOGGER.info("Starting write to MeiliSearch."),
        recordWriterFunction(indexNameToIndex),
        (hasFailed) -> LOGGER.info("Completed writing to MeiliSearch. Status: {}", hasFailed ? "FAILED" : "SUCCEEDED"),
        catalog,
        CatalogHelpers.getStreamNames(catalog));
  }

  private static Map<String, WriteConfig> createIndices(ConfiguredAirbyteCatalog catalog, Client client) throws Exception {
    final Map<String, WriteConfig> map = new HashMap<>();
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final String indexName = getIndexName(stream);

      if (stream.getSyncMode() == SyncMode.FULL_REFRESH && indexExists(client, indexName)) {
        client.deleteIndex(indexName);
      }

      final PrimaryKey primaryKey = getPrimaryKey(stream);
      final Index index = client.getOrCreateIndex(indexName, primaryKey.getArtificialKey());
      map.put(indexName, new WriteConfig(index, primaryKey));
    }
    return map;
  }

  private static class WriteConfig {

    private final Index index;
    private final PrimaryKey primaryKey;

    public WriteConfig(Index index, PrimaryKey primaryKey) {
      this.index = index;
      this.primaryKey = primaryKey;
    }

    public Index getIndex() {
      return index;
    }

    public PrimaryKey getPrimaryKey() {
      return primaryKey;
    }

  }

  private static boolean indexExists(Client client, String indexName) throws Exception {
    return Arrays.stream(client.getIndexList())
        .map(Index::getUid)
        .anyMatch(actualIndexName -> actualIndexName.equals(indexName));
  }

  private static CheckedBiConsumer<String, Stream<AirbyteRecordMessage>, Exception> recordWriterFunction(final Map<String, WriteConfig> indexNameToWriteConfig) {
    return (streamName, recordStream) -> {
      final String resolvedIndexName = getIndexName(streamName);
      if (!indexNameToWriteConfig.containsKey(resolvedIndexName)) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \nexpected streams: %s",
                indexNameToWriteConfig.keySet()));
      }

      final Index index = indexNameToWriteConfig.get(resolvedIndexName).getIndex();
      final PrimaryKey primaryKey = indexNameToWriteConfig.get(resolvedIndexName).getPrimaryKey();

      // Only writes the data, not the full AirbyteRecordMessage. This is different from how database
      // destinations work. There is not really a viable way to "transform" data after it is Meilisearch.
      // Tools like DBT do not apply. Therefore, we need to try to write data in the most usable format
      // possible that does not require alteration.
      final String json = Jsons.serialize(recordStream
          .map(AirbyteRecordMessage::getData)
          // meilisearch document ids can only have alphanumeric characters and _ (docs:
          // https://docs.meilisearch.com/learn/core_concepts/documents.html#primary-field). thus, we create
          // an "artificial" field where we take the contents of the field being used as the primary key and
          // make it compatible with the meilisearch document id format.
          .filter(o -> {
            if (o.has(primaryKey.getOriginalKey())) {
              return true;
            } else {
              LOGGER.warn("filtering record because it does not contain a primary key. stream: {} primary key: {} record: {}", streamName,
                  primaryKey.getOriginalKey(), o);
              return false;
            }
          })
          .peek(o -> {
            LOGGER.info("key:value, {}:{}", primaryKey.getOriginalKey(), o.get(primaryKey.getOriginalKey()).asText());
            ((ObjectNode) o).put(primaryKey.getArtificialKey(), Names.toAlphanumericAndUnderscore(o.get(primaryKey.getOriginalKey()).asText()));
          })
          .collect(Collectors.toList()));
      LOGGER.info("records to write {}:", json);
      final String s = index.addDocuments(json);
      LOGGER.info("add docs response {}", s);
      LOGGER.info("waiting for update started{}", Instant.now());
      try {
        index.waitForPendingUpdate(Jsons.deserialize(s).get("updateId").asInt());
      } catch (Exception e) {
        LOGGER.error("waiting for update failed.", e);
        LOGGER.error("printing meilisearch update statuses: {}", Arrays.asList(index.getUpdates()));
        throw e;
      }
      LOGGER.info("waiting for update completed {}", Instant.now());
    };
  }

  private static class PrimaryKey {

    private final String originalKey;
    private final String artificialKey;

    public PrimaryKey(String originalKey, String artificialKey) {
      this.originalKey = originalKey;
      this.artificialKey = artificialKey;
    }

    public String getOriginalKey() {
      return originalKey;
    }

    public String getArtificialKey() {
      return artificialKey;
    }

  }

  private static PrimaryKey getPrimaryKey(ConfiguredAirbyteStream stream) {
    final ArrayList<String> fieldNames = new ArrayList<>(CatalogHelpers.getTopLevelFieldNames(stream));

    Preconditions.checkState(!fieldNames.isEmpty(), "Cannot infer a primary key from a stream with no fields.");

    // emulating the logic that meilisearch uses to infer ids:
    // https://github.com/meilisearch/MeiliSearch/blob/master/meilisearch-http/src/routes/document.rs#L199-L206
    for (String fieldName : fieldNames) {
      if (fieldName.toLowerCase().contains("id")) {
        LOGGER.info(
            "For stream {}, inferred {} as the primary key. Any record for which this field is not present will not be uploaded into MeiliSearch.",
            stream.getStream().getName(), fieldName);
        return new PrimaryKey(fieldName, fieldNameToPkFieldName(fieldName));
      }
    }

    // if cannot "intelligently" infer the id, just pick the first field.
    final String fallbackPrimaryKey = fieldNames.get(0);
    LOGGER.warn(
        "Could not infer an id field for stream {}. Falling back on {}. Any record for which this field is not present will not be uploaded into MeiliSearch.",
        stream.getStream().getName(), fallbackPrimaryKey);
    return new PrimaryKey(fallbackPrimaryKey, fieldNameToPkFieldName(fallbackPrimaryKey));
  }

  private static String fieldNameToPkFieldName(String fieldName) {
    return AB_PK_PREFIX + fieldName;
  }

  private static String getIndexName(String streamName) {
    return Names.toAlphanumericAndUnderscore(streamName);
  }

  private static String getIndexName(ConfiguredAirbyteStream stream) {
    return getIndexName(stream.getStream().getName());
  }

  private static Set<String> getIndexNames(ConfiguredAirbyteCatalog catalog) {
    return catalog.getStreams()
        .stream()
        .map(MeiliSearchDestination::getIndexName)
        .collect(Collectors.toSet());
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) throws Exception {
    try {
      LOGGER.info("config in check {}", config);
      final Client client = getClient(config);
      final Index index = client.index("_airbyte");
      index.addDocuments("[{\"id\": \"_airbyte\" }]");
      index.search("_airbyte");
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (Exception e) {
      LOGGER.error("Check connection failed.", e);
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage("Check connection failed: " + e.getMessage());
    }
  }

  static Client getClient(JsonNode config) {
    // return new Client(new Config("http://localhost:7700", null));
    return new Client(new Config(config.get("host").asText(), config.has("api_key") ? config.get("api_key").asText() : null));
  }

  public static void main(String[] args) throws Exception {
    final Destination destination = new MeiliSearchDestination();
    // LOGGER.info("spec result {}", Jsons.serialize(destination.check(Jsons.emptyObject())));
    LOGGER.info("starting destination: {}", MeiliSearchDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", MeiliSearchDestination.class);
  }
}
