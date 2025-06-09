/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static com.mongodb.assertions.Assertions.assertNotNull;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcEventUtils.ID_FIELD;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcEventUtils.OBJECT_ID_FIELD;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.core.type.TypeReference;
import com.mongodb.client.ChangeStreamIterable;
import com.mongodb.client.MongoChangeStreamCursor;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Aggregates;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.changestream.ChangeStreamDocument;
import io.airbyte.cdk.integrations.debezium.internals.ChangeEventWithMetadata;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.Jsons;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.debezium.connector.mongodb.ResumeTokens;
import io.debezium.engine.ChangeEvent;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import org.bson.BsonDocument;
import org.bson.BsonTimestamp;
import org.bson.conversions.Bson;
import org.junit.jupiter.api.Test;

class MongoDbCdcTargetPositionTest {

  private static final String OBJECT_ID = "64f24244f95155351c4185b1";
  private static final String RESUME_TOKEN = "8264BEB9F3000000012B0229296E04";
  private static final String OTHER_RESUME_TOKEN = "8264BEB9F3000000012B0229296E05";
  private static final ConfiguredAirbyteCatalog CATALOG = new ConfiguredAirbyteCatalog();
  private static final String DATABASE = "test-database";
  private static final List<Bson> PIPELINE = Collections.singletonList(Aggregates.match(
      Filters.or(List.of(
          Filters.and(
              Filters.eq("ns.db", DATABASE),
              Filters.in("ns.coll", Collections.emptyList()))))));

  // Collections.singletonList(Aggregates.match(
  // Filters.in("ns.coll", Collections.emptyList())));

  @Test
  void testCreateTargetPosition() {
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(RESUME_TOKEN);
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);
    final MongoClient mongoClient = mock(MongoClient.class);

    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeTokenDocument);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);
    when(mongoClient.watch(PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);

    final MongoDbCdcTargetPosition targetPosition =
        new MongoDbCdcTargetPosition(
            MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(CATALOG.getStreams())));
    assertNotNull(targetPosition);
    assertEquals(ResumeTokens.getTimestamp(resumeTokenDocument), targetPosition.getResumeTokenTimestamp());
  }

  @Test
  void testReachedTargetPosition() throws IOException {
    final String changeEventJson = MoreResources.readResource("mongodb/change_event.json");
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(RESUME_TOKEN);
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
    final ChangeEvent<String, String> changeEvent = mock(ChangeEvent.class);

    when(changeEvent.key()).thenReturn("{\"" + ID_FIELD + "\":\"{\\\"" + OBJECT_ID_FIELD + "\\\": \\\"" + OBJECT_ID + "\\\"}\"}");
    when(changeEvent.value()).thenReturn(changeEventJson);
    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeTokenDocument);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);
    when(mongoClient.watch(PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);

    final ChangeEventWithMetadata changeEventWithMetadata = new ChangeEventWithMetadata(changeEvent);
    final MongoDbCdcTargetPosition targetPosition =
        new MongoDbCdcTargetPosition(
            MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(CATALOG.getStreams())));
    assertTrue(targetPosition.reachedTargetPosition(changeEventWithMetadata));

    when(changeEvent.value()).thenReturn(changeEventJson.replaceAll("\"ts_ms\": \\d+,", "\"ts_ms\": 1590221043000,"));
    final ChangeEventWithMetadata changeEventWithMetadata2 = new ChangeEventWithMetadata(changeEvent);
    assertFalse(targetPosition.reachedTargetPosition(changeEventWithMetadata2));
  }

  @Test
  void testReachedTargetPositionSnapshotEvent() throws IOException {
    final String changeEventJson = MoreResources.readResource("mongodb/change_event_snapshot.json");
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(RESUME_TOKEN);
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final ChangeEvent<String, String> changeEvent = mock(ChangeEvent.class);

    when(changeEvent.key()).thenReturn("{\"" + ID_FIELD + "\":\"{\\\"" + OBJECT_ID_FIELD + "\\\": \\\"" + OBJECT_ID + "\\\"}\"}");
    when(changeEvent.value()).thenReturn(changeEventJson);
    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeTokenDocument);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);
    when(mongoClient.watch(PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);

    final ChangeEventWithMetadata changeEventWithMetadata = new ChangeEventWithMetadata(changeEvent);
    final MongoDbCdcTargetPosition targetPosition =
        new MongoDbCdcTargetPosition(
            MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(CATALOG.getStreams())));
    assertFalse(targetPosition.reachedTargetPosition(changeEventWithMetadata));
  }

  @Test
  void testReachedTargetPositionSnapshotLastEvent() throws IOException {
    final String changeEventJson = MoreResources.readResource("mongodb/change_event_snapshot_last.json");
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(RESUME_TOKEN);
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final ChangeEvent<String, String> changeEvent = mock(ChangeEvent.class);

    when(changeEvent.key()).thenReturn("{\"" + ID_FIELD + "\":\"{\\\"" + OBJECT_ID_FIELD + "\\\": \\\"" + OBJECT_ID + "\\\"}\"}");
    when(changeEvent.value()).thenReturn(changeEventJson);
    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeTokenDocument);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);
    when(mongoClient.watch(PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);

    final ChangeEventWithMetadata changeEventWithMetadata = new ChangeEventWithMetadata(changeEvent);
    final MongoDbCdcTargetPosition targetPosition =
        new MongoDbCdcTargetPosition(
            MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(CATALOG.getStreams())));
    assertTrue(targetPosition.reachedTargetPosition(changeEventWithMetadata));
  }

  @Test
  void testReachedTargetPositionFromHeartbeat() {
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(RESUME_TOKEN);
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);
    final MongoClient mongoClient = mock(MongoClient.class);

    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeTokenDocument);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);
    when(mongoClient.watch(PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);

    final MongoDbCdcTargetPosition targetPosition =
        new MongoDbCdcTargetPosition(
            MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(CATALOG.getStreams())));

    final BsonTimestamp heartbeatTimestamp = new BsonTimestamp(
        Long.valueOf(ResumeTokens.getTimestamp(resumeTokenDocument).getTime() + TimeUnit.HOURS.toSeconds(1)).intValue(),
        0);

    assertTrue(targetPosition.reachedTargetPosition(heartbeatTimestamp));
    assertFalse(targetPosition.reachedTargetPosition((BsonTimestamp) null));
  }

  @Test
  void testIsHeartbeatSupported() {
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(RESUME_TOKEN);
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);
    final MongoClient mongoClient = mock(MongoClient.class);

    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeTokenDocument);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);
    when(mongoClient.watch(PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);
    final MongoDbCdcTargetPosition targetPosition =
        new MongoDbCdcTargetPosition(
            MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(CATALOG.getStreams())));

    assertTrue(targetPosition.isHeartbeatSupported());
  }

  @Test
  void testExtractPositionFromHeartbeatOffset() {
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(RESUME_TOKEN);
    final BsonTimestamp resumeTokenTimestamp = ResumeTokens.getTimestamp(resumeTokenDocument);
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);
    final MongoClient mongoClient = mock(MongoClient.class);

    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeTokenDocument);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);
    when(mongoClient.watch(PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);

    final MongoDbCdcTargetPosition targetPosition =
        new MongoDbCdcTargetPosition(
            MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(CATALOG.getStreams())));

    final Map<String, ?> sourceOffset = Map.of(
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_SECONDS, resumeTokenTimestamp.getTime(),
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_ORDER, resumeTokenTimestamp.getInc(),
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_RESUME_TOKEN, RESUME_TOKEN);

    final BsonTimestamp timestamp = targetPosition.extractPositionFromHeartbeatOffset(sourceOffset);
    assertEquals(resumeTokenTimestamp, timestamp);
  }

  @Test
  void testIsEventAheadOfOffset() throws IOException {
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(RESUME_TOKEN);
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final String changeEventJson = MoreResources.readResource("mongodb/change_event.json");
    final ChangeEvent<String, String> changeEvent = mock(ChangeEvent.class);

    when(changeEvent.key()).thenReturn("{\"" + ID_FIELD + "\":\"{\\\"" + OBJECT_ID_FIELD + "\\\": \\\"" + OBJECT_ID + "\\\"}\"}");
    when(changeEvent.value()).thenReturn(changeEventJson);
    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeTokenDocument);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);
    when(mongoClient.watch(PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);

    final ChangeEventWithMetadata changeEventWithMetadata = new ChangeEventWithMetadata(changeEvent);
    final Map<String, String> offset =
        Jsons.object(MongoDbDebeziumStateUtil.formatState(null, RESUME_TOKEN), new TypeReference<>() {});

    final MongoDbCdcTargetPosition targetPosition =
        new MongoDbCdcTargetPosition(
            MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(CATALOG.getStreams())));
    final boolean result = targetPosition.isEventAheadOffset(offset, changeEventWithMetadata);
    assertTrue(result);
  }

  @Test
  void testIsSameOffset() {
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(RESUME_TOKEN);
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);
    final MongoClient mongoClient = mock(MongoClient.class);

    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeTokenDocument);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);
    when(mongoClient.watch(PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);

    final Map<String, String> offsetA =
        Jsons.object(MongoDbDebeziumStateUtil.formatState(null, RESUME_TOKEN), new TypeReference<>() {});
    final Map<String, String> offsetB =
        Jsons.object(MongoDbDebeziumStateUtil.formatState(null, RESUME_TOKEN), new TypeReference<>() {});
    final Map<String, String> offsetC =
        Jsons.object(MongoDbDebeziumStateUtil.formatState(null, OTHER_RESUME_TOKEN), new TypeReference<>() {});

    final MongoDbCdcTargetPosition targetPosition =
        new MongoDbCdcTargetPosition(
            MongoDbResumeTokenHelper.getMostRecentResumeTokenForDatabases(mongoClient, List.of(DATABASE), List.of(CATALOG.getStreams())));

    assertTrue(targetPosition.isSameOffset(offsetA, offsetA));
    assertTrue(targetPosition.isSameOffset(offsetA, offsetB));
    assertTrue(targetPosition.isSameOffset(offsetB, offsetA));
    assertFalse(targetPosition.isSameOffset(offsetA, offsetC));
    assertFalse(targetPosition.isSameOffset(offsetB, offsetC));
  }

}
