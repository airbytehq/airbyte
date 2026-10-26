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
import io.debezium.connector.mongodb.ResumeTokens;
import java.util.*;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.util.regex.Pattern;
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

  private static final Pattern HEX_RESUME_TOKEN_DATA = Pattern.compile("^[0-9A-Fa-f]+$");

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
   * Parses a resume token as stored by Debezium in an offset. Debezium 2.x stored the hex
   * {@code _data} string of the token, while Debezium 3.x stores the base64-encoded BSON document of
   * the token (and still reads the old form). Accept both so that offsets and saved state written by
   * either version can be read.
   *
   * @param value The resume token value as found in an offset.
   * @return The resume token document.
   */
  public static BsonDocument resumeTokenFromOffsetValue(final String value) {
    return HEX_RESUME_TOKEN_DATA.matcher(value).matches() ? ResumeTokens.fromData(value) : ResumeTokens.fromBase64(value);
  }

  /**
   * Returns the hex {@code _data} string of a resume token, which is the form in which this connector
   * persists resume tokens in its state.
   *
   * @param resumeToken The resume token document.
   * @return The hex {@code _data} value of the token.
   */
  public static String resumeTokenData(final BsonDocument resumeToken) {
    return ResumeTokens.getData(resumeToken).asString().getValue();
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
