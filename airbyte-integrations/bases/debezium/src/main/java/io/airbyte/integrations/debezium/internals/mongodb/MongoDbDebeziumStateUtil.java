/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.mongodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.client.ChangeStreamIterable;
import com.mongodb.client.MongoChangeStreamCursor;
import com.mongodb.client.MongoClient;
import com.mongodb.client.model.changestream.ChangeStreamDocument;
import io.airbyte.commons.json.Jsons;
import io.debezium.connector.mongodb.ResumeTokens;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
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
    final BsonDocument resumeToken = getResumeToken(mongoClient);
    final String resumeTokenData = ((BsonString) ResumeTokens.getData(resumeToken)).getValue();
    final BsonTimestamp timestamp = ResumeTokens.getTimestamp(resumeToken);

    final List<Map<String, Object>> key = List.of(
        Map.of(MongoDbDebeziumConstants.OffsetState.KEY_REPLICA_SET, replicaSet,
            MongoDbDebeziumConstants.OffsetState.KEY_SERVER_ID, database));

    final Map<String, Object> value = new HashMap<>();
    value.put(MongoDbDebeziumConstants.OffsetState.VALUE_SECONDS, timestamp.getTime());
    value.put(MongoDbDebeziumConstants.OffsetState.VALUE_INCREMENT, timestamp.getInc());
    value.put(MongoDbDebeziumConstants.OffsetState.VALUE_TRANSACTION_ID, null);
    value.put(MongoDbDebeziumConstants.OffsetState.VALUE_RESUME_TOKEN, resumeTokenData);

    final JsonNode state = Jsons.jsonNode(Map.of(key, value));
    LOGGER.info("Initial Debezium state constructed: {}", state);
    return state;
  }

  /**
   * Retrieves the most recent resume token from MongoDB server.
   *
   * @param mongoClient The {@link MongoClient} used to query the MongoDB server.
   * @return The most recent resume token value.
   */
  private BsonDocument getResumeToken(final MongoClient mongoClient) {
    final ChangeStreamIterable<BsonDocument> eventStream = mongoClient.watch(BsonDocument.class);
    try (final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> eventStreamCursor = eventStream.cursor()) {
      /*
       * Must call tryNext before attempting to get the resume token from the cursor directly. Otherwise,
       * the call to getResumeToken() will return null!
       */
      eventStreamCursor.tryNext();
      return eventStreamCursor.getResumeToken();
    }
  }

}
