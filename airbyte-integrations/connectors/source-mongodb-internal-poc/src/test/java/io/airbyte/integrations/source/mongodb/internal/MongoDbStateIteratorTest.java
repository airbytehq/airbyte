/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.when;

import com.mongodb.MongoException;
import com.mongodb.client.MongoCursor;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import org.bson.Document;
import org.bson.types.ObjectId;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.mockito.invocation.InvocationOnMock;
import org.mockito.stubbing.Answer;

class MongoDbStateIteratorTest {

  private static final int CHECKPOINT_INTERVAL = 2;
  @Mock
  private MongoCursor<Document> mongoCursor;
  private AutoCloseable closeable;

  @BeforeEach
  public void setup() {
    closeable = MockitoAnnotations.openMocks(this);
  }

  @AfterEach
  public void teardown() throws Exception {
    closeable.close();
  }

  @Test
  void happyPath() {
    final var docs = docs();

    when(mongoCursor.hasNext()).thenAnswer(new Answer<Boolean>() {

      private int count = 0;

      @Override
      public Boolean answer(InvocationOnMock invocation) throws Throwable {
        count++;
        // hasNext will be called for each doc plus for each state message
        return count <= (docs.size() + (docs.size() % CHECKPOINT_INTERVAL));
      }

    });

    when(mongoCursor.next()).thenAnswer(new Answer<Document>() {

      private int offset = 0;

      @Override
      public Document answer(InvocationOnMock invocation) throws Throwable {
        final var doc = docs.get(offset);
        offset++;
        return doc;
      }

    });

    final var stream = catalog().getStreams().stream().findFirst().orElseThrow();

    final var iter = new MongoDbStateIterator(mongoCursor, stream, Optional.empty(), Instant.now(), CHECKPOINT_INTERVAL);

    // with a batch size of 2, the MongoDbStateIterator should return the following after each
    // `hasNext`/`next` call:
    // true, record Air Force Blue
    // true, record Alice Blue
    // true, state (with Alice Blue as the state)
    // true, record Alizarin Crimson
    // true, state (with Alizarin Crimson)
    // false
    AirbyteMessage message;
    assertTrue(iter.hasNext(), "air force blue should be next");
    message = iter.next();
    assertEquals(Type.RECORD, message.getType());
    assertEquals(docs.get(0).get("_id").toString(), message.getRecord().getData().get("_id").asText());

    assertTrue(iter.hasNext(), "alice blue should be next");
    message = iter.next();
    assertEquals(Type.RECORD, message.getType());
    assertEquals(docs.get(1).get("_id").toString(), message.getRecord().getData().get("_id").asText());

    assertTrue(iter.hasNext(), "state should be next");
    message = iter.next();
    assertEquals(Type.STATE, message.getType());
    assertEquals(
        docs.get(1).get("_id").toString(),
        message.getState().getStream().getStreamState().get("id").asText(),
        "state id should match last record id");

    assertTrue(iter.hasNext(), "alizarin crimson should be next");
    message = iter.next();
    assertEquals(Type.RECORD, message.getType());
    assertEquals(docs.get(2).get("_id").toString(), message.getRecord().getData().get("_id").asText());

    assertTrue(iter.hasNext(), "state should be next");
    message = iter.next();
    assertEquals(Type.STATE, message.getType());
    assertEquals(
        docs.get(2).get("_id").toString(),
        message.getState().getStream().getStreamState().get("id").asText(),
        "state id should match last record id");

    assertFalse(iter.hasNext(), "should have no more records");
  }

  @Test
  void treatHasNextExceptionAsFalse() {
    final var docs = docs();

    // on the second hasNext call, throw an exception
    when(mongoCursor.hasNext())
        .thenReturn(true)
        .thenThrow(new MongoException("test exception"));

    when(mongoCursor.next()).thenReturn(docs.get(0));

    final var stream = catalog().getStreams().stream().findFirst().orElseThrow();

    final var iter = new MongoDbStateIterator(mongoCursor, stream, Optional.empty(), Instant.now(), CHECKPOINT_INTERVAL);

    // with a batch size of 2, the MongoDbStateIterator should return the following after each
    // `hasNext`/`next` call:
    // true, record Air Force Blue
    // true (exception thrown), state (with Air Force Blue as the state)
    // false
    AirbyteMessage message;
    assertTrue(iter.hasNext(), "air force blue should be next");
    message = iter.next();
    assertEquals(Type.RECORD, message.getType());
    assertEquals(docs.get(0).get("_id").toString(), message.getRecord().getData().get("_id").asText());

    assertTrue(iter.hasNext(), "state should be next");
    message = iter.next();
    assertEquals(Type.STATE, message.getType());
    assertEquals(
        docs.get(0).get("_id").toString(),
        message.getState().getStream().getStreamState().get("id").asText(),
        "state id should match last record id");

    assertFalse(iter.hasNext(), "should have no more records");
  }

  @Test
  void initialStateIsReturnedIfUnderlyingIteratorIsEmpty() {
    final var docs = docs();

    // on the second hasNext call, throw an exception
    when(mongoCursor.hasNext()).thenReturn(false);

    final var stream = catalog().getStreams().stream().findFirst().orElseThrow();
    final var objectId = "64dfb6a7bb3c3458c30801f4";
    final var iter = new MongoDbStateIterator(mongoCursor, stream, Optional.of(new MongodbStreamState(objectId)), Instant.now(), CHECKPOINT_INTERVAL);

    // the MongoDbStateIterator should return the following after each
    // `hasNext`/`next` call:
    // false
    // then the generated state message should have the same id as the initial state
    assertTrue(iter.hasNext(), "state should be next");

    final AirbyteMessage message = iter.next();
    assertEquals(Type.STATE, message.getType());
    assertEquals(
        objectId,
        message.getState().getStream().getStreamState().get("id").asText(),
        "state id should match initial state ");

    assertFalse(iter.hasNext(), "should have no more records");
  }

  private ConfiguredAirbyteCatalog catalog() {
    return new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(List.of("_id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withCursorField(List.of("_id"))
            .withStream(CatalogHelpers.createAirbyteStream(
                "test.unit",
                Field.of("_id", JsonSchemaType.STRING),
                Field.of("name", JsonSchemaType.STRING),
                Field.of("hex", JsonSchemaType.STRING))
                .withSupportedSyncModes(List.of(SyncMode.INCREMENTAL))
                .withDefaultCursorField(List.of("_id")))));
  }

  private List<Document> docs() {
    return List.of(
        new Document("_id", new ObjectId("64c0029d95ad260d69ef28a0"))
            .append("name", "Air Force Blue").append("hex", "#5d8aa8"),
        new Document("_id", new ObjectId("64c0029d95ad260d69ef28a1"))
            .append("name", "Alice Blue").append("hex", "#f0f8ff"),
        new Document("_id", new ObjectId("64c0029d95ad260d69ef28a2"))
            .append("name", "Alizarin Crimson").append("hex", "#e32636"));
  }

}
