/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium.internals.mongodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.client.ChangeStreamIterable;
import com.mongodb.client.MongoChangeStreamCursor;
import com.mongodb.client.MongoClient;
import com.mongodb.client.model.changestream.ChangeStreamDocument;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import org.bson.BsonDocument;
import org.bson.BsonTimestamp;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Collection of utility helper methods for dealing with MongoDB resume tokens.
 */
public class MongoDbResumeTokenHelper {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbResumeTokenHelper.class);

  /**
   * Retrieves the most recent resume token from MongoDB server.
   *
   * @param mongoClient The {@link MongoClient} used to query the MongoDB server.
   * @return The most recent resume token value.
   */
  public static BsonDocument getMostRecentResumeToken(final MongoClient mongoClient) {
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

  /**
   * Extracts the timestamp from a Debezium MongoDB change event.
   *
   * @param event The Debezium MongoDB change event as JSON.
   * @return The extracted timestamp
   * @throws IllegalStateException if the timestamp could not be extracted from the change event.
   */
  public static BsonTimestamp extractTimestampFromEvent(final JsonNode event) {
    return extractTimestampFromSource(event.get(MongoDbDebeziumConstants.ChangeEvent.SOURCE));
  }

  /**
   * Extracts the timestamp from a Debezium MongoDB change event source object.
   *
   * @param source The Debezium MongoDB change event source object as JSON.
   * @return The extracted timestamp
   * @throws IllegalStateException if the timestamp could not be extracted from the change event.
   */
  public static BsonTimestamp extractTimestampFromSource(final JsonNode source) {
    return Optional.ofNullable(source)
        .flatMap(MongoDbResumeTokenHelper::createTimestampFromSource)
        .orElseThrow(() -> new IllegalStateException("Could not find timestamp"));
  }

  private static Optional<BsonTimestamp> createTimestampFromSource(final JsonNode source) {
    try {
      return Optional.of(
          new BsonTimestamp(
              Long.valueOf(TimeUnit.MILLISECONDS.toSeconds(
                  source.get(MongoDbDebeziumConstants.ChangeEvent.SOURCE_TIMESTAMP_MS)
                      .asLong()))
                  .intValue(),
              source.get(MongoDbDebeziumConstants.ChangeEvent.SOURCE_ORDER).asInt()));
    } catch (final Exception e) {
      LOGGER.warn("Unable to extract timestamp data from event source.", e);
      return Optional.empty();
    }
  }

}
