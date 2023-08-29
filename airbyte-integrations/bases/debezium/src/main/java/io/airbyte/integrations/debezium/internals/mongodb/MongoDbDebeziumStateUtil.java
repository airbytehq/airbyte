/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.mongodb;

import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.OffsetState.VALUE_SECONDS;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.mongodb.client.MongoClient;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.debezium.internals.AirbyteFileOffsetBackingStore;
import io.airbyte.integrations.debezium.internals.DebeziumPropertiesManager;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.debezium.config.Configuration;
import io.debezium.connector.mongodb.MongoDbConnectorConfig;
import io.debezium.connector.mongodb.MongoDbOffsetContext;
import io.debezium.connector.mongodb.ReplicaSets;
import io.debezium.connector.mongodb.ResumeTokens;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.Properties;
import org.apache.kafka.connect.json.JsonConverter;
import org.apache.kafka.connect.json.JsonConverterConfig;
import org.apache.kafka.connect.runtime.WorkerConfig;
import org.apache.kafka.connect.runtime.standalone.StandaloneConfig;
import org.apache.kafka.connect.storage.FileOffsetBackingStore;
import org.apache.kafka.connect.storage.OffsetStorageReaderImpl;
import org.bson.BsonDocument;
import org.bson.BsonString;
import org.bson.BsonTimestamp;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Collection of utility methods related to the Debezium offset state.
 */
public class MongoDbDebeziumStateUtil {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbDebeziumStateUtil.class);

  /**
   * Constructs the initial Debezium offset state that will be used by the incremental CDC snapshot
   * after an initial snapshot sync.
   *
   * @param mongoClient The {@link MongoClient} used to query the MongoDB server.
   * @param database The database associated with the sync.
   * @param replicaSet The replication set associated with the sync.
   * @return The initial Debezium offset state storage document as a {@link JsonNode}.
   */
  public JsonNode constructInitialDebeziumState(final MongoClient mongoClient, final String database, final String replicaSet) {
    final BsonDocument resumeToken = MongoDbResumeTokenHelper.getResumeToken(mongoClient);

    final JsonNode state = formatState(database, replicaSet, ((BsonString) ResumeTokens.getData(resumeToken)).getValue());
    LOGGER.info("Initial Debezium state constructed: {}", state);
    return state;
  }

  /**
   * Formats the Debezium initial state into a format suitable for storage in the offset data file.
   *
   * @param database The name of the target MongoDB database.
   * @param replicaSet The name of the target MongoDB replica set.
   * @param resumeTokenData The MongoDB resume token that represents the offset state.
   * @return The offset state as a {@link JsonNode}.
   */
  @VisibleForTesting
  public static JsonNode formatState(final String database, final String replicaSet, final String resumeTokenData) {
    final BsonTimestamp timestamp = ResumeTokens.getTimestamp(ResumeTokens.fromData(resumeTokenData));

    final List<Object> key = List.of(
        database,
        Map.of(MongoDbDebeziumConstants.OffsetState.KEY_REPLICA_SET, replicaSet,
            MongoDbDebeziumConstants.OffsetState.KEY_SERVER_ID, database));

    final Map<String, Object> value = new HashMap<>();
    value.put(VALUE_SECONDS, timestamp.getTime());
    value.put(MongoDbDebeziumConstants.OffsetState.VALUE_INCREMENT, timestamp.getInc());
    value.put(MongoDbDebeziumConstants.OffsetState.VALUE_TRANSACTION_ID, null);
    value.put(MongoDbDebeziumConstants.OffsetState.VALUE_RESUME_TOKEN, resumeTokenData);

    return Jsons.jsonNode(Map.of(Jsons.serialize(key), Jsons.serialize(value)));
  }

  public boolean isSavedOffsetAfterResumeToken(final MongoClient mongoClient, final OptionalLong savedOffset) {
    if (Objects.isNull(savedOffset) || savedOffset.isEmpty()) {
      return true;
    }

    final BsonDocument resumeToken = MongoDbResumeTokenHelper.getResumeToken(mongoClient);
    final BsonTimestamp currentTimestamp = ResumeTokens.getTimestamp(resumeToken);

    return savedOffset.getAsLong() >= currentTimestamp.getValue();
  }

  public OptionalLong savedOffset(final Properties baseProperties,
                                  final ConfiguredAirbyteCatalog catalog,
                                  final JsonNode cdcState,
                                  final JsonNode config) {
    final DebeziumPropertiesManager debeziumPropertiesManager = new MongoDbDebeziumPropertiesManager(baseProperties,
        config, catalog,
        AirbyteFileOffsetBackingStore.initializeState(cdcState, Optional.empty()), Optional.empty());
    final Properties debeziumProperties = debeziumPropertiesManager.getDebeziumProperties();
    return parseSavedOffset(debeziumProperties);
  }

  /**
   *
   * @param properties Properties should contain the relevant properties like path to the debezium
   *        state file, etc. It's assumed that the state file is already initialised with the saved
   *        state
   * @return Returns the LSN that Airbyte has acknowledged in the source database server
   */
  private OptionalLong parseSavedOffset(final Properties properties) {

    FileOffsetBackingStore fileOffsetBackingStore = null;
    OffsetStorageReaderImpl offsetStorageReader = null;
    try {
      fileOffsetBackingStore = new FileOffsetBackingStore();
      final Map<String, String> propertiesMap = Configuration.from(properties).asMap();
      propertiesMap.put(WorkerConfig.KEY_CONVERTER_CLASS_CONFIG, JsonConverter.class.getName());
      propertiesMap.put(WorkerConfig.VALUE_CONVERTER_CLASS_CONFIG, JsonConverter.class.getName());
      fileOffsetBackingStore.configure(new StandaloneConfig(propertiesMap));
      fileOffsetBackingStore.start();

      final Map<String, String> internalConverterConfig = Collections.singletonMap(JsonConverterConfig.SCHEMAS_ENABLE_CONFIG, "false");
      final JsonConverter keyConverter = new JsonConverter();
      keyConverter.configure(internalConverterConfig, true);
      final JsonConverter valueConverter = new JsonConverter();
      valueConverter.configure(internalConverterConfig, false);

      final MongoDbConnectorConfig mongoDbConnectorConfig = new MongoDbConnectorConfig(Configuration.from(properties));
      final ReplicaSets replicaSets = mongoDbConnectorConfig.getReplicaSets();

      offsetStorageReader = new OffsetStorageReaderImpl(fileOffsetBackingStore, properties.getProperty("name"), keyConverter, valueConverter);

      final MongoDbOffsetContext.Loader loader = new MongoDbCustomLoader(mongoDbConnectorConfig, replicaSets);
      final Collection<Map<String, String>> partitions = loader.getPartitions();
      final Map<Map<String, String>, Map<String, Object>> offsets = offsetStorageReader.offsets(partitions);

      if (offsets != null && offsets.values().stream().anyMatch(Objects::nonNull)) {
        final MongoDbOffsetContext offsetContext = loader.loadOffsets(offsets);
        final Map<String, ?> offset = offsetContext.getReplicaSetOffsetContext(replicaSets.all().get(0)).getOffset();
        final BsonTimestamp timestamp = new BsonTimestamp((Integer) offset.get(MongoDbDebeziumConstants.OffsetState.VALUE_SECONDS),
            (Integer) offset.get(MongoDbDebeziumConstants.OffsetState.VALUE_INCREMENT));
        return OptionalLong.of(timestamp.getValue());
      } else {
        return OptionalLong.empty();
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

}
