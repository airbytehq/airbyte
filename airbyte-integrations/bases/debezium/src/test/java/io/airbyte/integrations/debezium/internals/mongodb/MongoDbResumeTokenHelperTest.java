/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.mongodb;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.client.ChangeStreamIterable;
import com.mongodb.client.MongoChangeStreamCursor;
import com.mongodb.client.MongoClient;
import com.mongodb.client.model.changestream.ChangeStreamDocument;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.debezium.connector.mongodb.ResumeTokens;
import java.io.IOException;
import java.util.concurrent.TimeUnit;
import org.bson.BsonDocument;
import org.bson.BsonTimestamp;
import org.junit.jupiter.api.Test;

class MongoDbResumeTokenHelperTest {

  @Test
  void testRetrievingResumeToken() {
    final String resumeToken = "8264BEB9F3000000012B0229296E04";
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(resumeToken);
    final ChangeStreamIterable changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);
    final MongoClient mongoClient = mock(MongoClient.class);

    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeTokenDocument);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);
    when(mongoClient.watch(BsonDocument.class)).thenReturn(changeStreamIterable);

    final BsonDocument actualResumeToken = MongoDbResumeTokenHelper.getResumeToken(mongoClient);
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

}
