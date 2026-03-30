/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.client.ChangeStreamIterable;
import com.mongodb.client.MongoChangeStreamCursor;
import com.mongodb.client.MongoClient;
import com.mongodb.client.model.Aggregates;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.changestream.ChangeStreamDocument;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.debezium.config.Configuration;
import io.debezium.connector.mongodb.MongoDbTaskContext;
import io.debezium.connector.mongodb.MongoUtils;
import java.util.*;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.Properties;
import java.util.concurrent.TimeUnit;
import org.bson.BsonDocument;
import org.bson.BsonTimestamp;
import org.bson.conversions.Bson;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Collection of utility helper methods for dealing with MongoDB resume tokens.
 */
public class MongoDbResumeTokenHelper {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbResumeTokenHelper.class);

  /**
   * Retrieves the most recent resume token for the specified databases and collections from the
   * MongoDB server.
   *
   * This method constructs a change stream pipeline that matches events for the provided list of
   * databases and their corresponding collections. It then opens a change stream and retrieves the
   * latest available resume token, which can be used to resume reading from the change stream at a
   * later time.
   *
   * @param mongoClient The {@link MongoClient} used to query the MongoDB server.
   * @param databaseNames A list of database names to monitor.
   * @param streamsByDatabase A list of lists, where each inner list contains
   *        {@link ConfiguredAirbyteStream} objects representing the collections to monitor for each
   *        database.
   * @return The most recent resume token value as a {@link BsonDocument}, or null if no token is
   *         available.
   */
  public static BsonDocument getMostRecentResumeTokenForDatabases(final MongoClient mongoClient,
                                                                  final List<String> databaseNames,
                                                                  final List<List<ConfiguredAirbyteStream>> streamsByDatabase) {

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
    final ChangeStreamIterable<BsonDocument> eventStream;
    if (databaseNames.size() == 1) {
      LOGGER.info("Most recent CDC token for a single database.");
      eventStream = mongoClient.getDatabase(databaseNames.getFirst()).watch(pipeline, BsonDocument.class);
    } else {
      LOGGER.info("Most recent CDC token for multiple databases.");
      eventStream = mongoClient.watch(pipeline, BsonDocument.class);
    }

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
   * Retrieves the most recent resume token using Debezium's change stream pipeline.
   * This ensures consistency between the resume token used as the CDC target position
   * and the pipeline used by Debezium during actual CDC streaming.
   * <p>
   * Using the same pipeline as Debezium prevents potential discrepancies that can occur
   * when the initial resume token is obtained with a different change stream configuration
   * than what Debezium uses for CDC. Such discrepancies have been observed to contribute
   * to the "101-record" pattern where incremental syncs return only metadata records.
   *
   * @param mongoClient The {@link MongoClient} used to query the MongoDB server.
   * @param debeziumProperties The Debezium properties used to configure the change stream pipeline.
   * @return The most recent resume token value as a {@link BsonDocument}.
   */
  public static BsonDocument getMostRecentResumeToken(final MongoClient mongoClient,
                                                       final Properties debeziumProperties) {
    LOGGER.info("Retrieving most recent resume token using Debezium's change stream pipeline.");
    final Configuration config = Configuration.from(debeziumProperties);
    final MongoDbTaskContext taskContext = new MongoDbTaskContext(config);
    final ChangeStreamIterable<BsonDocument> changeStream = MongoUtils.openChangeStream(mongoClient, taskContext);

    try (final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> cursor = changeStream.cursor()) {
      /*
       * Must call tryNext before attempting to get the resume token from the cursor directly.
       * Otherwise, the call to getResumeToken() will return null!
       */
      cursor.tryNext();
      return cursor.getResumeToken();
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
