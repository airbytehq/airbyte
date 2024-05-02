/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

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
import io.debezium.config.Configuration;
import io.debezium.connector.mongodb.MongoDbConnectorConfig;
import io.debezium.connector.mongodb.MongoDbOffsetContext;
import io.debezium.connector.mongodb.MongoDbTaskContext;
import io.debezium.connector.mongodb.MongoUtil;
import io.debezium.connector.mongodb.ReplicaSetDiscovery;
import io.debezium.connector.mongodb.ReplicaSets;
import io.debezium.connector.mongodb.ResumeTokens;
import java.util.Collection;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Properties;
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
   * @param mongoClient The {@link MongoClient} used to query the MongoDB server.
   * @param serverId The ID of the target server.
   * @return The initial Debezium offset state storage document as a {@link JsonNode}.
   * @throws IllegalStateException if unable to determine the replica set.
   */
  public JsonNode constructInitialDebeziumState(final BsonDocument resumeToken, final MongoClient mongoClient, final String serverId) {
    final String replicaSet = getReplicaSetName(mongoClient);
    LOGGER.info("Initial resume token '{}' constructed, corresponding to timestamp (seconds after epoch) {}",
        ResumeTokens.getData(resumeToken).asString().getValue(), ResumeTokens.getTimestamp(resumeToken).getTime());
    final JsonNode state = formatState(serverId, replicaSet, ((BsonString) ResumeTokens.getData(resumeToken)).getValue());
    LOGGER.info("Initial Debezium state constructed: {}", state);
    return state;
  }

  /**
   * Formats the Debezium initial state into a format suitable for storage in the offset data file.
   *
   * @param serverId The ID target MongoDB database.
   * @param replicaSet The name of the target MongoDB replica set.
   * @param resumeTokenData The MongoDB resume token that represents the offset state.
   * @return The offset state as a {@link JsonNode}.
   */
  public static JsonNode formatState(final String serverId, final String replicaSet, final String resumeTokenData) {
    final BsonTimestamp timestamp = ResumeTokens.getTimestamp(ResumeTokens.fromData(resumeTokenData));

    final List<Object> key = generateOffsetKey(serverId, replicaSet);

    final Map<String, Object> value = new LinkedHashMap<>();
    value.put(MongoDbDebeziumConstants.OffsetState.VALUE_SECONDS, timestamp.getTime());
    value.put(MongoDbDebeziumConstants.OffsetState.VALUE_INCREMENT, timestamp.getInc());
    value.put(MongoDbDebeziumConstants.OffsetState.VALUE_TRANSACTION_ID, null);
    value.put(MongoDbDebeziumConstants.OffsetState.VALUE_RESUME_TOKEN, resumeTokenData);

    return Jsons.jsonNode(Map.of(Jsons.serialize(key), Jsons.serialize(value)));
  }

  /**
   * Retrieves the replica set name for the current connection.
   *
   * @param mongoClient The {@link MongoClient} used to retrieve the replica set name.
   * @return The replica set name.
   * @throws IllegalStateException if unable to determine the replica set.
   */
  public static String getReplicaSetName(final MongoClient mongoClient) {
    final Optional<String> replicaSetName = MongoUtil.replicaSetName(mongoClient.getClusterDescription());
    return replicaSetName.orElseThrow(() -> new IllegalStateException("Unable to determine replica set."));
  }

  /**
   * Test whether the retrieved saved offset resume token value is valid. A valid resume token is one
   * that can be used to resume a change event stream in MongoDB.
   *
   * @param savedOffset The resume token from the saved offset.
   * @param mongoClient The {@link MongoClient} used to validate the saved offset.
   *
   * @return {@code true} if the saved offset value is valid Otherwise, {@code false} is returned to
   *         indicate that an initial snapshot should be performed.
   */
  public boolean isValidResumeToken(final BsonDocument savedOffset,
                                    final MongoClient mongoClient,
                                    final String databaseName,
                                    final ConfiguredAirbyteCatalog catalog) {
    if (Objects.isNull(savedOffset) || savedOffset.isEmpty()) {
      return true;
    }

    // Scope the change stream to the collections & database of interest - this mirrors the logic while
    // getting the most recent resume token.
    final List<String> collectionsList = catalog.getStreams().stream()
        .map(s -> s.getStream().getName())
        .toList();
    final List<Bson> pipeline = Collections.singletonList(Aggregates.match(
        Filters.in("ns.coll", collectionsList)));
    final ChangeStreamIterable<BsonDocument> eventStream = mongoClient.getDatabase(databaseName).watch(pipeline, BsonDocument.class);

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
                                            final JsonNode config,
                                            final MongoClient mongoClient) {
    LOGGER.debug("Initializing file offset backing store with state '{}'...", cdcState);
    final var offsetManager = AirbyteFileOffsetBackingStore.initializeState(cdcState, Optional.empty());
    final DebeziumPropertiesManager debeziumPropertiesManager = new MongoDbDebeziumPropertiesManager(baseProperties, config, catalog);
    final Properties debeziumProperties = debeziumPropertiesManager.getDebeziumProperties(offsetManager);
    return parseSavedOffset(debeziumProperties, mongoClient);
  }

  /**
   * Loads the offset data from the saved Debezium offset file.
   *
   * @param properties Properties should contain the relevant properties like path to the Debezium
   *        state file, etc. It's assumed that the state file is already initialised with the saved
   *        state
   * @return Returns the resume token that Airbyte has acknowledged in the source database server.
   */
  private Optional<BsonDocument> parseSavedOffset(final Properties properties, final MongoClient mongoClient) {
    FileOffsetBackingStore fileOffsetBackingStore = null;
    OffsetStorageReaderImpl offsetStorageReader = null;

    try {
      fileOffsetBackingStore = getFileOffsetBackingStore(properties);
      offsetStorageReader = getOffsetStorageReader(fileOffsetBackingStore, properties);

      final Configuration config = Configuration.from(properties);
      final MongoDbTaskContext taskContext = new MongoDbTaskContext(config);
      final MongoDbConnectorConfig mongoDbConnectorConfig = new MongoDbConnectorConfig(config);
      final ReplicaSets replicaSets = new ReplicaSetDiscovery(taskContext).getReplicaSets(mongoClient);

      LOGGER.debug("Parsing saved offset state for replica set '{}' and server ID '{}'...", replicaSets.all().get(0), properties.getProperty("name"));

      final MongoDbOffsetContext.Loader loader = new MongoDbCustomLoader(mongoDbConnectorConfig, replicaSets);
      final Collection<Map<String, String>> partitions = loader.getPartitions();
      final Map<Map<String, String>, Map<String, Object>> offsets = offsetStorageReader.offsets(partitions);

      if (offsets != null && offsets.values().stream().anyMatch(Objects::nonNull)) {
        final MongoDbOffsetContext offsetContext = loader.loadOffsets(offsets);
        final Map<String, ?> offset = offsetContext.getReplicaSetOffsetContext(replicaSets.all().get(0)).getOffset();
        final Object resumeTokenData = offset.get(MongoDbDebeziumConstants.OffsetState.VALUE_RESUME_TOKEN);
        if (resumeTokenData != null) {
          final BsonDocument resumeToken = ResumeTokens.fromData(resumeTokenData.toString());
          return Optional.of(resumeToken);
        } else {
          LOGGER.warn("Offset data does not contain a resume token: {}", offset);
          return Optional.empty();
        }
      } else {
        LOGGER.warn("Loaded offset data is null or empty: {}", offsets);
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

  private static List<Object> generateOffsetKey(final String serverId, final String replicaSet) {
    /*
     * N.B. The order of the keys in the sourceInfoMap and key list matters! DO NOT CHANGE the order
     * unless you have verified that Debezium has changed its order of the key it builds when retrieving
     * data from the offset file. See the "partition(String replicaSetName)" method of the
     * io.debezium.connector.mongodb.SourceInfo class for the ordering of keys in the list/map.
     */
    final Map<String, String> sourceInfoMap = new LinkedHashMap<>();
    final String normalizedServerId = MongoDbDebeziumPropertiesManager.normalizeName(serverId);
    sourceInfoMap.put(MongoDbDebeziumConstants.OffsetState.KEY_REPLICA_SET, replicaSet);
    sourceInfoMap.put(MongoDbDebeziumConstants.OffsetState.KEY_SERVER_ID, normalizedServerId);

    final List<Object> key = new LinkedList<>();
    key.add(normalizedServerId);
    key.add(sourceInfoMap);
    return key;
  }

}
