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
import io.airbyte.integrations.source.mongodb.MongoConstants;
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

  @Test
  void testGetMostRecentResumeTokenRethrowsUnauthorizedAsConfigError() {
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);

    final BsonDocument response = new BsonDocument()
        .append("ok", new BsonInt32(0))
        .append("code", new BsonInt32(MongoConstants.MONGO_UNAUTHORIZED_ERROR_CODE))
        .append("errmsg", new BsonString("not authorized on " + DATABASE + " to execute command { aggregate: 1, pipeline: [...] }"));
    final MongoCommandException unauthorized = new MongoCommandException(response, new ServerAddress());

    when(mongoClient.getDatabase(DATABASE)).thenReturn(mongoDatabase);

    final List<Bson> pipeline = Collections.singletonList(Aggregates.match(
        Filters.or(List.of(
            Filters.and(
                Filters.eq("ns.db", DATABASE),
                Filters.in("ns.coll", Collections.emptyList()))))));
    when(mongoClient.watch(pipeline, BsonDocument.class)).thenReturn(changeStreamIterable);
    when(mongoDatabase.watch(pipeline, BsonDocument.class)).thenReturn(changeStreamIterable);
    when(changeStreamIterable.cursor()).thenThrow(unauthorized);

    final ConfigErrorException thrown = assertThrows(ConfigErrorException.class,
        () -> MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(List.of())));

    assertEquals(
        "MongoDB user is not authorized to open a change stream on database \"" + DATABASE + "\". "
            + "Grant a role with the `find` and `changeStream` privileges (the built-in `readAnyDatabase` role is sufficient).",
        thrown.getMessage());
    assertEquals(unauthorized, thrown.getCause());
  }

  @Test
  void testGetMostRecentResumeTokenRethrowsUnauthorizedFromTryNext() {
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> cursor = mock(MongoChangeStreamCursor.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);

    final BsonDocument response = new BsonDocument()
        .append("ok", new BsonInt32(0))
        .append("code", new BsonInt32(MongoConstants.MONGO_UNAUTHORIZED_ERROR_CODE))
        .append("errmsg", new BsonString("not authorized"));
    final MongoCommandException unauthorized = new MongoCommandException(response, new ServerAddress());

    when(mongoClient.getDatabase(DATABASE)).thenReturn(mongoDatabase);
    when(mongoDatabase.watch(Collections.singletonList(Aggregates.match(
        Filters.or(List.of(
            Filters.and(
                Filters.eq("ns.db", DATABASE),
                Filters.in("ns.coll", Collections.emptyList())))))),
        BsonDocument.class))
            .thenReturn(changeStreamIterable);
    when(changeStreamIterable.cursor()).thenReturn(cursor);
    when(cursor.tryNext()).thenThrow(unauthorized);

    final ConfigErrorException thrown = assertThrows(ConfigErrorException.class,
        () -> MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(List.of())));
    assertEquals(unauthorized, thrown.getCause());
  }

  @Test
  void testGetMostRecentResumeTokenRethrowsNonUnauthorizedAsIs() {
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);

    final BsonDocument response = new BsonDocument()
        .append("ok", new BsonInt32(0))
        .append("code", new BsonInt32(MongoConstants.BSON_OBJECT_TOO_LARGE_ERROR_CODE))
        .append("errmsg", new BsonString("BSONObjectTooLarge"));
    final MongoCommandException bsonTooLarge = new MongoCommandException(response, new ServerAddress());

    when(mongoClient.getDatabase(DATABASE)).thenReturn(mongoDatabase);
    when(mongoDatabase.watch(Collections.singletonList(Aggregates.match(
        Filters.or(List.of(
            Filters.and(
                Filters.eq("ns.db", DATABASE),
                Filters.in("ns.coll", Collections.emptyList())))))),
        BsonDocument.class))
            .thenReturn(changeStreamIterable);
    when(changeStreamIterable.cursor()).thenThrow(bsonTooLarge);

    assertThrows(MongoCommandException.class,
        () -> MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(List.of())));
  }

}
