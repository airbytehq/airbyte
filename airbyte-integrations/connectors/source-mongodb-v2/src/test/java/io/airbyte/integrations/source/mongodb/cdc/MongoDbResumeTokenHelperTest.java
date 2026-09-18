/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.mockStatic;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.client.ChangeStreamIterable;
import com.mongodb.client.MongoChangeStreamCursor;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Aggregates;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.changestream.ChangeStreamDocument;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.debezium.connector.mongodb.MongoUtils;
import io.debezium.connector.mongodb.ResumeTokens;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.Properties;
import java.util.concurrent.TimeUnit;
import org.bson.BsonDocument;
import org.bson.BsonTimestamp;
import org.bson.conversions.Bson;
import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;

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

  /**
   * Tests the new getMostRecentResumeToken method that uses Debezium's change stream pipeline (via
   * MongoUtils.openChangeStream) instead of a custom pipeline. This method is the fix for the
   * "101-record" pattern where incremental syncs return only metadata records due to a pipeline
   * mismatch between initial resume token retrieval and Debezium's CDC streaming.
   */
  @Test
  void testRetrievingResumeTokenWithDebeziumPipeline() {
    final String resumeToken = "8264BEB9F3000000012B0229296E04";
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(resumeToken);
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);
    final MongoClient mongoClient = mock(MongoClient.class);

    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeTokenDocument);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);

    final Properties debeziumProperties = new Properties();
    debeziumProperties.setProperty("mongodb.connection.string", "mongodb://localhost:27017/");
    debeziumProperties.setProperty("collection.include.list", DATABASE + ".test-collection");
    debeziumProperties.setProperty("capture.scope", "deployment");
    debeziumProperties.setProperty("topic.prefix", "test-prefix");

    try (MockedStatic<MongoUtils> mockedMongoUtils = mockStatic(MongoUtils.class)) {
      mockedMongoUtils.when(() -> MongoUtils.openChangeStream(any(MongoClient.class), any()))
          .thenReturn(changeStreamIterable);

      final BsonDocument actualResumeToken =
          MongoDbResumeTokenHelper.getMostRecentResumeToken(mongoClient, debeziumProperties);
      assertEquals(resumeTokenDocument, actualResumeToken);

      // Verify Debezium's pipeline is used (not a custom pipeline)
      mockedMongoUtils.verify(() -> MongoUtils.openChangeStream(any(MongoClient.class), any()));
    }
  }

}
