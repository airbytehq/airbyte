/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.meilisearch;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.meilisearch.sdk.Client;
import com.meilisearch.sdk.Config;
import com.meilisearch.sdk.Index;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.text.Names;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer;
import io.airbyte.integrations.destination.buffered_stream_consumer.RecordWriter;
import io.airbyte.integrations.destination.record_buffer.InMemoryRecordBufferingStrategy;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * <p>
 * Since this is not a relational database, it therefore makes some slightly different choices. The
 * main difference that we need to reckon with is that this destination does not work without a
 * primary key for each stream. That primary key needs to be defined ahead of time. Only records for
 * which that primary key is present can be uploaded. There are also some rules around the allowed
 * formats of these primary keys.
 * </p>
 * <p>
 * The strategy is to inject an extra airbyte primary key field in each record. The value of that
 * field is a randomly generate UUID. This means that we have no ability to ever overwrite
 * individual records that we put in MeiliSearch.
 * </p>
 * <p>
 * Index names can only contain alphanumeric values, so we normalize stream names to meet these
 * constraints. This is why streamName and indexName are treated separately in this connector.
 * </p>
 * <p>
 * This destination can support full refresh and incremental. It does NOT support normalization. It
 * breaks from the paradigm of having a "raw" and "normalized" table. There is no DBT for
 * MeiliSearch so we write the data a single time in a way that makes it most likely to work well
 * within MeiliSearch.
 * </p>
 */
public class MeiliSearchDestination extends BaseConnector implements Destination {

  private static final Logger LOGGER = LoggerFactory.getLogger(MeiliSearchDestination.class);

  private static final int MAX_BATCH_SIZE_BYTES = 1024 * 1024 * 1024 / 4; // 256mib
  private static final DateTimeFormatter FORMATTER = DateTimeFormatter.ofPattern("uuuu-MM-dd'T'HH:mm:ss.SSSSSSSSS");

  public static final String AB_PK_COLUMN = "_ab_pk";
  public static final String AB_EMITTED_AT_COLUMN = "_ab_emitted_at";

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) {
    try {
      LOGGER.info("config in check {}", config);
      // create a fake index and add a record to it to make sure we can connect and have write access.
      final Client client = getClient(config);
      final Index index = client.index("_airbyte");
      index.addDocuments("[{\"id\": \"_airbyte\" }]");
      index.search("_airbyte");
      client.deleteIndex(index.getUid());
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.error("Check connection failed.", e);
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage("Check connection failed: " + e.getMessage());
    }
  }

  @Override
  public AirbyteMessageConsumer getConsumer(final JsonNode config,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Consumer<AirbyteMessage> outputRecordCollector)
      throws Exception {
    final Client client = getClient(config);
    final Map<String, Index> indexNameToIndex = createIndices(catalog, client);

    return new BufferedStreamConsumer(
        outputRecordCollector,
        () -> LOGGER.info("Starting write to MeiliSearch."),
        new InMemoryRecordBufferingStrategy(recordWriterFunction(indexNameToIndex), MAX_BATCH_SIZE_BYTES),
        (hasFailed) -> LOGGER.info("Completed writing to MeiliSearch. Status: {}", hasFailed ? "FAILED" : "SUCCEEDED"),
        catalog,
        (data) -> true);
  }

  private static Map<String, Index> createIndices(final ConfiguredAirbyteCatalog catalog, final Client client) throws Exception {
    final Map<String, Index> map = new HashMap<>();
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final String indexName = getIndexName(stream);
      final DestinationSyncMode syncMode = stream.getDestinationSyncMode();
      if (syncMode == null) {
        throw new IllegalStateException("Undefined destination sync mode");
      }
      if (syncMode == DestinationSyncMode.OVERWRITE && indexExists(client, indexName)) {
        client.deleteIndex(indexName);
      }

      final Index index = client.getOrCreateIndex(indexName, AB_PK_COLUMN);
      map.put(indexName, index);
    }
    return map;
  }

  private static boolean indexExists(final Client client, final String indexName) throws Exception {
    return Arrays.stream(client.getIndexList())
        .map(Index::getUid)
        .anyMatch(actualIndexName -> actualIndexName.equals(indexName));
  }

  private static RecordWriter<AirbyteRecordMessage> recordWriterFunction(final Map<String, Index> indexNameToWriteConfig) {
    return (namePair, records) -> {
      final String resolvedIndexName = getIndexName(namePair.getName());
      if (!indexNameToWriteConfig.containsKey(resolvedIndexName)) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream that was not in the catalog. \nexpected streams: %s",
                indexNameToWriteConfig.keySet()));
      }

      final Index index = indexNameToWriteConfig.get(resolvedIndexName);

      // Only writes the data, not the full AirbyteRecordMessage. This is different from how database
      // destinations work. There is not really a viable way to "transform" data after it is MeiliSearch.
      // Tools like DBT do not apply. Therefore, we need to try to write data in the most usable format
      // possible that does not require alteration.
      final String json = Jsons.serialize(records
          .stream()
          .map(AirbyteRecordMessage::getData)
          .peek(o -> ((ObjectNode) o).put(AB_PK_COLUMN, Names.toAlphanumericAndUnderscore(UUID.randomUUID().toString())))
          .peek(o -> ((ObjectNode) o).put(AB_EMITTED_AT_COLUMN, LocalDateTime.now().format(FORMATTER)))
          .collect(Collectors.toList()));
      final String s = index.addDocuments(json);
      LOGGER.info("add docs response {}", s);
      LOGGER.info("waiting for update to be applied started {}", Instant.now());
      try {
        index.waitForPendingUpdate(Jsons.deserialize(s).get("updateId").asInt());
      } catch (final Exception e) {
        LOGGER.error("waiting for update to be applied failed.", e);
        LOGGER.error("printing MeiliSearch update statuses: {}", Arrays.asList(index.getUpdates()));
        throw e;
      }
      LOGGER.info("waiting for update  to be applied completed {}", Instant.now());
    };
  }

  private static String getIndexName(final String streamName) {
    return Names.toAlphanumericAndUnderscore(streamName);
  }

  private static String getIndexName(final ConfiguredAirbyteStream stream) {
    return getIndexName(stream.getStream().getName());
  }

  static Client getClient(final JsonNode config) {
    return new Client(new Config(config.get("host").asText(), config.has("api_key") ? config.get("api_key").asText() : null));
  }

  public static void main(final String[] args) throws Exception {
    final Destination destination = new MeiliSearchDestination();
    LOGGER.info("starting destination: {}", MeiliSearchDestination.class);
    new IntegrationRunner(destination).run(args);
    LOGGER.info("completed destination: {}", MeiliSearchDestination.class);
  }

}
