/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
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
import org.bson.BsonInt32;
import org.bson.BsonString;
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
  void testRetrievingResumeTokenWrapsUnauthorizedAsConfigError() {
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);

    when(mongoClient.getDatabase(DATABASE)).thenReturn(mongoDatabase);

    final BsonDocument errorResponse = new BsonDocument()
        .append("ok", new BsonInt32(0))
        .append("code", new BsonInt32(MongoDbResumeTokenHelper.MONGODB_UNAUTHORIZED_ERROR_CODE))
        .append("codeName", new BsonString("Unauthorized"))
        .append("errmsg", new BsonString("not authorized on " + DATABASE + " to execute command"));
    final MongoCommandException unauthorizedException =
        new MongoCommandException(errorResponse, new ServerAddress());

    when(mongoDatabase.watch(any(List.class), eq(BsonDocument.class))).thenReturn(changeStreamIterable);
    when(changeStreamIterable.cursor()).thenThrow(unauthorizedException);

    final ConfigErrorException thrown = assertThrows(ConfigErrorException.class,
        () -> MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(List.of())));
    assertEquals(
        "MongoDB user is not authorized to open a change stream on database \"" + DATABASE
            + "\". Grant the user the \"read\" role on that database, or the \"readAnyDatabase\" role for cluster-wide CDC.",
        thrown.getMessage());
    assertEquals(unauthorizedException, thrown.getCause());
  }

  @Test
  void testRetrievingResumeTokenPassesThroughOtherMongoCommandExceptions() {
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);

    when(mongoClient.getDatabase(DATABASE)).thenReturn(mongoDatabase);

    // An arbitrary non-13 MongoDB error code (e.g., 11600 InterruptedAtShutdown).
    final BsonDocument errorResponse = new BsonDocument()
        .append("ok", new BsonInt32(0))
        .append("code", new BsonInt32(11600))
        .append("codeName", new BsonString("InterruptedAtShutdown"))
        .append("errmsg", new BsonString("interrupted at shutdown"));
    final MongoCommandException otherException = new MongoCommandException(errorResponse, new ServerAddress());

    when(mongoDatabase.watch(any(List.class), eq(BsonDocument.class))).thenReturn(changeStreamIterable);
    when(changeStreamIterable.cursor()).thenThrow(otherException);

    final MongoCommandException thrown = assertThrows(MongoCommandException.class,
        () -> MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(List.of())));
    assertEquals(otherException, thrown);
  }

  @Test
  void testRetrievingResumeTokenWrapsUnauthorizedForMultipleDatabases() {
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoClient mongoClient = mock(MongoClient.class);

    final BsonDocument errorResponse = new BsonDocument()
        .append("ok", new BsonInt32(0))
        .append("code", new BsonInt32(MongoDbResumeTokenHelper.MONGODB_UNAUTHORIZED_ERROR_CODE))
        .append("codeName", new BsonString("Unauthorized"))
        .append("errmsg", new BsonString("not authorized to execute command"));
    final MongoCommandException unauthorizedException =
        new MongoCommandException(errorResponse, new ServerAddress());

    when(mongoClient.watch(any(List.class), eq(BsonDocument.class))).thenReturn(changeStreamIterable);
    when(changeStreamIterable.cursor()).thenThrow(unauthorizedException);

    final ConfigErrorException thrown = assertThrows(ConfigErrorException.class,
        () -> MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(
            mongoClient, List.of(DATABASE, "other-database"), List.of(List.of(), List.of())));
    assertEquals(
        "MongoDB user is not authorized to open a change stream on the configured databases. "
            + "Grant the user the \"read\" role on that database, or the \"readAnyDatabase\" role for cluster-wide CDC.",
        thrown.getMessage());
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
