/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants.OffsetState.KEY_SERVER_ID;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumPropertiesManager.DATABASE_INCLUDE_LIST_KEY;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumPropertiesManager.normalizeName;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.MongoChangeStreamException;
import com.mongodb.MongoCommandException;
import com.mongodb.client.ChangeStreamIterable;
import com.mongodb.client.MongoClient;
import com.mongodb.client.model.Aggregates;
import com.mongodb.client.model.Filters;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteFileOffsetBackingStore;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumPropertiesManager;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumStateUtil;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.debezium.config.Configuration;
import io.debezium.connector.common.OffsetReader;
import io.debezium.connector.mongodb.MongoDbConnectorConfig;
import io.debezium.connector.mongodb.MongoDbOffsetContext;
import io.debezium.connector.mongodb.MongoDbPartition;
import io.debezium.connector.mongodb.ResumeTokens;
import io.debezium.pipeline.spi.Partition;
import java.util.*;
import org.apache.kafka.connect.storage.FileOffsetBackingStore;
import org.apache.kafka.connect.storage.OffsetStorageReaderImpl;
import org.bson.BsonDocument;
import org.bson.BsonString;
import org.bson.BsonTimestamp;
import org.bson.conversions.Bson;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Collection of utility methods related to the Debezium offset state.
 */
public class MongoDbDebeziumStateUtil implements DebeziumStateUtil {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbDebeziumStateUtil.class);

  /**
   * Constructs the initial Debezium offset state that will be used by the incremental CDC snapshot
   * after an initial snapshot sync.
   *
   * @param serverId The ID of the target server.
   * @return The initial Debezium offset state storage document as a {@link JsonNode}.
   * @throws IllegalStateException if unable to determine the replica set.
   */
  public JsonNode constructInitialDebeziumState(final BsonDocument resumeToken, final String serverId) {
    LOGGER.info("Initial resume token '{}' constructed, corresponding to timestamp (seconds after epoch) {}",
        ResumeTokens.getData(resumeToken).asString().getValue(), ResumeTokens.getTimestamp(resumeToken).getTime());
    final JsonNode state = formatState(serverId, ((BsonString) ResumeTokens.getData(resumeToken)).getValue());
    LOGGER.info("Initial Debezium state constructed: {}", state);
    return state;
  }

  /**
   * Formats the Debezium initial state into a format suitable for storage in the offset data file.
   *
   * @param serverId The ID target MongoDB database.
   * @param resumeTokenData The MongoDB resume token that represents the offset state.
   * @return The offset state as a {@link JsonNode}.
   */
  public static JsonNode formatState(final String serverId, final String resumeTokenData) {
    final BsonTimestamp timestamp = ResumeTokens.getTimestamp(ResumeTokens.fromData(resumeTokenData));

    final List<Object> key = generateOffsetKey(serverId);

    final Map<String, Object> value = new LinkedHashMap<>();
    value.put(MongoDbDebeziumConstants.OffsetState.VALUE_SECONDS, timestamp.getTime());
    value.put(MongoDbDebeziumConstants.OffsetState.VALUE_INCREMENT, timestamp.getInc());
    value.put(MongoDbDebeziumConstants.OffsetState.VALUE_RESUME_TOKEN, resumeTokenData);

    return Jsons.jsonNode(Map.of(Jsons.serialize(key), Jsons.serialize(value)));
  }

  /**
   * Tests whether the provided saved offset resume token is valid for resuming a MongoDB change event
   * stream.
   *
   * @param savedOffset The resume token from the saved offset.
   * @param mongoClient The MongoClient used to validate the saved offset.
   * @param databaseNames The list of database names to check.
   * @param streamsByDatabase The list of lists of ConfiguredAirbyteStream objects, grouped by
   *        database.
   * @return {@code true} if the saved offset value is valid; otherwise, {@code false} to indicate
   *         that an initial snapshot should be performed.
   */
  public boolean isValidResumeToken(final BsonDocument savedOffset,
                                    final MongoClient mongoClient,
                                    final List<String> databaseNames,
                                    final List<List<ConfiguredAirbyteStream>> streamsByDatabase) {
    if (Objects.isNull(savedOffset) || savedOffset.isEmpty()) {
      return true;
    }

    // databaseNames and streamsByDatabase must be the same length
    List<Bson> orFilters = new ArrayList<>();
    for (int i = 0; i < databaseNames.size(); i++) {
      String dbName = databaseNames.get(i);
      List<ConfiguredAirbyteStream> streams = streamsByDatabase.get(i);
      List<String> collectionNames = streams.stream()
          .map(s -> s.getStream().getName())
          .toList();
      // Match documents where ns.db == dbName and ns.coll in collectionNames
      orFilters.add(Filters.and(
          Filters.eq("ns.db", dbName),
          Filters.in("ns.coll", collectionNames)));
    }

    final List<Bson> pipeline = Collections.singletonList(Aggregates.match(Filters.or(orFilters)));
    final ChangeStreamIterable<BsonDocument> eventStream = mongoClient.watch(pipeline, BsonDocument.class);

    // Attempt to start the stream after the saved offset.
    eventStream.resumeAfter(savedOffset);
    try (final var ignored = eventStream.cursor()) {
      LOGGER.info("Valid resume token '{}' present, corresponding to timestamp (seconds after epoch) : {}.  Incremental sync will be performed for "
          + "up-to-date streams.",
          ResumeTokens.getData(savedOffset).asString().getValue(), ResumeTokens.getTimestamp(savedOffset).getTime());
      return true;
    } catch (final MongoCommandException | MongoChangeStreamException e) {
      LOGGER.info("Exception : {}", e.getMessage());
      LOGGER.info("Invalid resume token '{}' present, corresponding to timestamp (seconds after epoch) : {}, due to reason {}",
          ResumeTokens.getData(savedOffset).asString().getValue(), ResumeTokens.getTimestamp(savedOffset).getTime(), e.getMessage());
      return false;
    }
  }

  /**
   * Saves and retrieves the Debezium offset data. This method writes the provided CDC state to the
   * offset file and then uses Debezium's code to retrieve the state from the offset file in order to
   * verify that Debezium will be able to read the offset data itself when invoked.
   *
   * @param baseProperties The base Debezium properties.
   * @param catalog The configured Airbyte catalog.
   * @param cdcState The current CDC state that contains the offset data.
   * @param config The source configuration.
   * @return The offset value (the timestamp extracted from the resume token) retrieved from the CDC
   *         state/offset data.
   */
  public Optional<BsonDocument> savedOffset(final Properties baseProperties,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final JsonNode cdcState,
                                            final JsonNode config) {
    LOGGER.debug("Initializing file offset backing store with state '{}'...", cdcState);
    final var offsetManager = AirbyteFileOffsetBackingStore.initializeState(cdcState, Optional.empty());
    final DebeziumPropertiesManager debeziumPropertiesManager =
        new MongoDbDebeziumPropertiesManager(baseProperties, config, catalog, Collections.emptyList());
    final Properties debeziumProperties = debeziumPropertiesManager.getDebeziumProperties(offsetManager);
    HashMap<Object, Object> safeProps = new HashMap<>(debeziumProperties);
    safeProps.put("mongodb.password", "****");
    LOGGER.info("properties: " + safeProps);
    Optional<BsonDocument> offset = parseSavedOffset(debeziumProperties);
    if (offset.isEmpty()) {
      LOGGER
          .info(
              "This connector is using the old offset format where server_id is set to database name, migrating to the new offset format where save_id is now connection string.");
      for (String databaseName : debeziumProperties.getProperty(DATABASE_INCLUDE_LIST_KEY).split(",")) {
        debeziumProperties.setProperty("name", normalizeName(databaseName));
        offset = parseSavedOffset(debeziumProperties);
        if (!offset.isEmpty())
          break;
      }
    }
    return offset;
  }

  /**
   * Loads the offset data from the saved Debezium offset file.
   *
   * @param properties Properties should contain the relevant properties like path to the Debezium
   *        state file, etc. It's assumed that the state file is already initialised with the saved
   *        state
   * @return Returns the resume token that Airbyte has acknowledged in the source database server.
   */
  private Optional<BsonDocument> parseSavedOffset(final Properties properties) {
    FileOffsetBackingStore fileOffsetBackingStore = null;
    OffsetStorageReaderImpl offsetStorageReader = null;

    try {
      fileOffsetBackingStore = getFileOffsetBackingStore(properties);
      offsetStorageReader = getOffsetStorageReader(fileOffsetBackingStore, properties);

      final Configuration config = Configuration.from(properties);
      final MongoDbConnectorConfig mongoDbConnectorConfig = new MongoDbConnectorConfig(config);

      final MongoDbOffsetContext.Loader loader = new MongoDbOffsetContext.Loader(mongoDbConnectorConfig);
      final Partition mongoDbPartition = new MongoDbPartition(properties.getProperty(CONNECTOR_NAME_PROPERTY));

      final Set<Partition> partitions =
          Collections.singleton(mongoDbPartition);
      final OffsetReader<Partition, MongoDbOffsetContext, MongoDbOffsetContext.Loader> offsetReader = new OffsetReader<>(offsetStorageReader, loader);
      final Map<Partition, MongoDbOffsetContext> offsets = offsetReader.offsets(partitions);
      if (offsets == null || offsets.values().stream().noneMatch(Objects::nonNull)) {
        return Optional.empty();
      }
      final MongoDbOffsetContext context = offsets.get(mongoDbPartition);
      final var offset = context.getOffset();
      final Object resumeTokenData = offset.get(MongoDbDebeziumConstants.OffsetState.VALUE_RESUME_TOKEN);

      if (resumeTokenData != null) {
        LOGGER.info("Resume token is not null");
        final BsonDocument resumeToken = ResumeTokens.fromData(resumeTokenData.toString());
        return Optional.of(resumeToken);
      } else {
        return Optional.empty();
      }
    } finally {
      LOGGER.info("Closing offsetStorageReader and fileOffsetBackingStore");
      if (offsetStorageReader != null) {
        offsetStorageReader.close();
      }
      if (fileOffsetBackingStore != null) {
        fileOffsetBackingStore.stop();
      }
    }
  }

  private static List<Object> generateOffsetKey(final String serverId) {
    /*
     * N.B. The order of the keys in the sourceInfoMap and key list matters! DO NOT CHANGE the order
     * unless you have verified that Debezium has changed its order of the key it builds when retrieving
     * data from the offset file. See the "partition(String replicaSetName)" method of the
     * io.debezium.connector.mongodb.SourceInfo class for the ordering of keys in the list/map.
     */
    final Map<String, String> sourceInfoMap = new LinkedHashMap<>();
    final String normalizedServerId = MongoDbDebeziumPropertiesManager.normalizeName(serverId);
    sourceInfoMap.put(KEY_SERVER_ID, normalizedServerId);

    final List<Object> key = new LinkedList<>();
    key.add(normalizedServerId);
    key.add(sourceInfoMap);
    return key;
  }

}
