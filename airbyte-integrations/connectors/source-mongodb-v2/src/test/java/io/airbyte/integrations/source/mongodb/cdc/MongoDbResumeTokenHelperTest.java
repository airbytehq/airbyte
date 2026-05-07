/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.MongoCommandException;
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
import org.mockito.Mockito;

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
  void testUnauthorizedChangeStreamThrowsConfigErrorException() {
    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);

    final BsonDocument errorResponse = new BsonDocument()
        .append("ok", new org.bson.BsonDouble(0.0))
        .append("code", new org.bson.BsonInt32(13))
        .append("codeName", new org.bson.BsonString("Unauthorized"))
        .append("errmsg", new org.bson.BsonString("not authorized on " + DATABASE + " to execute command"));
    final MongoCommandException unauthorizedException =
        new MongoCommandException(errorResponse, new com.mongodb.ServerAddress("localhost", 27017));

    when(mongoClient.getDatabase(DATABASE)).thenReturn(mongoDatabase);
    when(mongoDatabase.watch(Mockito.<List<Bson>>any(), Mockito.eq(BsonDocument.class))).thenReturn(changeStreamIterable);
    when(changeStreamIterable.cursor()).thenThrow(unauthorizedException);

    final ConfigErrorException thrown = assertThrows(ConfigErrorException.class,
        () -> MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(List.of())));

    assertEquals("Insufficient MongoDB privileges to open a change stream on the configured database.", thrown.getDisplayMessage());
  }

  @Test
  void testNonUnauthorizedMongoCommandExceptionIsRethrown() {
    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);

    final BsonDocument errorResponse = new BsonDocument()
        .append("ok", new org.bson.BsonDouble(0.0))
        .append("code", new org.bson.BsonInt32(40573))
        .append("codeName", new org.bson.BsonString("Location40573"))
        .append("errmsg", new org.bson.BsonString("The $changeStream stage is only supported on replica sets"));
    final MongoCommandException otherException =
        new MongoCommandException(errorResponse, new com.mongodb.ServerAddress("localhost", 27017));

    when(mongoClient.getDatabase(DATABASE)).thenReturn(mongoDatabase);
    when(mongoDatabase.watch(Mockito.<List<Bson>>any(), Mockito.eq(BsonDocument.class))).thenReturn(changeStreamIterable);
    when(changeStreamIterable.cursor()).thenThrow(otherException);

    assertThrows(MongoCommandException.class,
        () -> MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(List.of())));
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
