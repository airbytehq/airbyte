/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.MongoCommandException;
import com.mongodb.ServerAddress;
import com.mongodb.client.ChangeStreamIterable;
import com.mongodb.client.MongoChangeStreamCursor;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Aggregates;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.changestream.ChangeStreamDocument;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.debezium.connector.mongodb.ResumeTokens;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.TimeUnit;
import org.bson.BsonDocument;
import org.bson.BsonTimestamp;
import org.bson.conversions.Bson;
import org.junit.jupiter.api.Test;

class MongoDbResumeTokenHelperTest {

  private static final String DATABASE = "test-database";

  @Test
  void testRetrievingResumeToken() {
    final String resumeToken = "8264BEB9F3000000012B0229296E04";
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(resumeToken);
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);

    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeTokenDocument);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);
    when(mongoClient.getDatabase(DATABASE)).thenReturn(mongoDatabase);

    final List<Bson> pipeline = Collections.singletonList(Aggregates.match(
        Filters.or(List.of(
            Filters.and(
                Filters.eq("ns.db", DATABASE),
                Filters.in("ns.coll", Collections.emptyList()))))));
    when(mongoClient.watch(pipeline, BsonDocument.class)).thenReturn(changeStreamIterable);
    when(mongoDatabase.watch(pipeline, BsonDocument.class)).thenReturn(changeStreamIterable);

    final BsonDocument actualResumeToken =
        MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(List.of()));
    assertEquals(resumeTokenDocument, actualResumeToken);
  }

  @Test
  void testUnauthorizedChangeStreamThrowsConfigErrorExceptionForSingleDatabase() {
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);

    final BsonDocument errorResponse = new BsonDocument()
        .append("ok", new org.bson.BsonDouble(0.0))
        .append("code", new org.bson.BsonInt32(13))
        .append("codeName", new org.bson.BsonString("Unauthorized"))
        .append("errmsg", new org.bson.BsonString("not authorized on " + DATABASE + " to execute command"));
    final MongoCommandException unauthorized = new MongoCommandException(errorResponse, new ServerAddress());
    when(changeStreamIterable.cursor()).thenThrow(unauthorized);
    when(mongoClient.getDatabase(DATABASE)).thenReturn(mongoDatabase);
    when(mongoDatabase.watch(any(List.class), eq(BsonDocument.class))).thenReturn(changeStreamIterable);

    final ConfigErrorException thrown = assertThrows(ConfigErrorException.class,
        () -> MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(List.of())));
    assertEquals(
        "MongoDB user is not authorized to open a change stream on database \"" + DATABASE + "\". "
            + "Grant the \"read\" role on this database (or equivalent privileges including \"find\" and \"changeStream\").",
        thrown.getMessage());
    assertSame(unauthorized, thrown.getCause());
  }

  @Test
  void testUnauthorizedChangeStreamThrowsConfigErrorExceptionForMultipleDatabases() {
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoClient mongoClient = mock(MongoClient.class);

    final BsonDocument errorResponse = new BsonDocument()
        .append("ok", new org.bson.BsonDouble(0.0))
        .append("code", new org.bson.BsonInt32(13))
        .append("codeName", new org.bson.BsonString("Unauthorized"))
        .append("errmsg", new org.bson.BsonString("not authorized on admin to execute command"));
    final MongoCommandException unauthorized = new MongoCommandException(errorResponse, new ServerAddress());
    when(changeStreamIterable.cursor()).thenThrow(unauthorized);
    when(mongoClient.watch(any(List.class), eq(BsonDocument.class))).thenReturn(changeStreamIterable);

    final List<String> databases = List.of("db-one", "db-two");
    final ConfigErrorException thrown = assertThrows(ConfigErrorException.class,
        () -> MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, databases, List.of(List.of(), List.of())));
    assertEquals(
        "MongoDB user is not authorized to open a change stream on databases \"db-one\", \"db-two\". "
            + "Grant the \"readAnyDatabase\" role (or equivalent privileges including \"find\" and \"changeStream\") on those databases.",
        thrown.getMessage());
    assertSame(unauthorized, thrown.getCause());
  }

  @Test
  void testNonAuthorizationMongoCommandExceptionIsNotWrapped() {
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);

    final BsonDocument errorResponse = new BsonDocument()
        .append("ok", new org.bson.BsonDouble(0.0))
        .append("code", new org.bson.BsonInt32(11601))
        .append("codeName", new org.bson.BsonString("Interrupted"))
        .append("errmsg", new org.bson.BsonString("operation was interrupted"));
    final MongoCommandException nonAuthError = new MongoCommandException(errorResponse, new ServerAddress());
    when(changeStreamIterable.cursor()).thenThrow(nonAuthError);
    when(mongoClient.getDatabase(DATABASE)).thenReturn(mongoDatabase);
    when(mongoDatabase.watch(any(List.class), eq(BsonDocument.class))).thenReturn(changeStreamIterable);

    final MongoCommandException thrown = assertThrows(MongoCommandException.class,
        () -> MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(List.of())));
    assertSame(nonAuthError, thrown);
  }

  @Test
  void testTimestampExtractionFromEvent() throws IOException {
    final int timestampSec = Long.valueOf(TimeUnit.MILLISECONDS.toSeconds(1692651270000L)).intValue();
    final BsonTimestamp expectedTimestamp = new BsonTimestamp(timestampSec, 2);
    final String changeEventJson = MoreResources.readResource("mongodb/change_event.json");
    final JsonNode changeEvent = Jsons.deserialize(changeEventJson);
    final BsonTimestamp timestamp = MongoDbResumeTokenHelper.extractTimestampFromEvent(changeEvent);
    assertNotNull(timestamp);
    assertEquals(expectedTimestamp, timestamp);
  }

  @Test
  void testTimestampExtractionFromEventSource() throws IOException {
    final int timestampSec = Long.valueOf(TimeUnit.MILLISECONDS.toSeconds(1692651270000L)).intValue();
    final BsonTimestamp expectedTimestamp = new BsonTimestamp(timestampSec, 2);
    final String changeEventJson = MoreResources.readResource("mongodb/change_event.json");
    final JsonNode changeEvent = Jsons.deserialize(changeEventJson);

    final BsonTimestamp timestamp = MongoDbResumeTokenHelper
        .extractTimestampFromSource(changeEvent.get(MongoDbDebeziumConstants.ChangeEvent.SOURCE));
    assertNotNull(timestamp);
    assertEquals(expectedTimestamp, timestamp);
  }

  @Test
  void testTimestampExtractionFromEventSourceNotPresent() {
    final JsonNode changeEvent = Jsons.deserialize("{}");
    assertThrows(IllegalStateException.class, () -> MongoDbResumeTokenHelper.extractTimestampFromEvent(changeEvent));
    assertThrows(IllegalStateException.class, () -> MongoDbResumeTokenHelper.extractTimestampFromSource(changeEvent));
  }

  @Test
  void testTimestampExtractionTimestampNotPresent() {
    final JsonNode changeEvent = Jsons.deserialize("{\"source\":{}}");
    assertThrows(IllegalStateException.class, () -> MongoDbResumeTokenHelper.extractTimestampFromEvent(changeEvent));
  }

}
