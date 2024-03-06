/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableSet;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.source.mongodb.state.IdType;
import io.airbyte.integrations.source.mongodb.state.MongoDbStateManager;
import io.airbyte.integrations.source.mongodb.state.MongoDbStreamState;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import org.bson.Document;
import org.bson.types.ObjectId;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MongoDBContainer;

class InitialSnapshotHandlerTest {

  private static final String DB_NAME = "airbyte_test";

  private static final String CURSOR_FIELD = "_id";
  private static final String NAME_FIELD = "name";

  private static final String NAMESPACE = "database";

  private static final String COLLECTION1 = "collection1";
  private static final String COLLECTION2 = "collection2";
  private static final String COLLECTION3 = "collection3";

  private static final String OBJECT_ID1_STRING = "64c0029d95ad260d69ef28a1";
  private static final String OBJECT_ID2_STRING = "64c0029d95ad260d69ef28a2";
  private static final String OBJECT_ID3_STRING = "64c0029d95ad260d69ef28a3";
  private static final ObjectId OBJECT_ID1 = new ObjectId(OBJECT_ID1_STRING);
  private static final ObjectId OBJECT_ID2 = new ObjectId(OBJECT_ID2_STRING);
  private static final ObjectId OBJECT_ID3 = new ObjectId(OBJECT_ID3_STRING);
  private static final ObjectId OBJECT_ID4 = new ObjectId("64c0029d95ad260d69ef28a4");
  private static final ObjectId OBJECT_ID5 = new ObjectId("64c0029d95ad260d69ef28a5");
  private static final ObjectId OBJECT_ID6 = new ObjectId("64c0029d95ad260d69ef28a6");

  private static final String NAME1 = "name1";
  private static final String NAME2 = "name2";
  private static final String NAME3 = "name3";
  private static final String NAME4 = "name4";
  private static final String NAME5 = "name5";
  private static final String NAME6 = "name6";

  private static final List<ConfiguredAirbyteStream> STREAMS = List.of(
      CatalogHelpers.createConfiguredAirbyteStream(
          COLLECTION1,
          NAMESPACE,
          Field.of(CURSOR_FIELD, JsonSchemaType.STRING),
          Field.of(NAME_FIELD, JsonSchemaType.STRING))
          .withSyncMode(SyncMode.INCREMENTAL),
      CatalogHelpers.createConfiguredAirbyteStream(
          COLLECTION2,
          NAMESPACE,
          Field.of(CURSOR_FIELD, JsonSchemaType.STRING))
          .withSyncMode(SyncMode.INCREMENTAL),
      CatalogHelpers.createConfiguredAirbyteStream(
          COLLECTION3,
          NAMESPACE,
          Field.of(CURSOR_FIELD, JsonSchemaType.STRING),
          Field.of(NAME_FIELD, JsonSchemaType.STRING))
          .withSyncMode(SyncMode.FULL_REFRESH));

  private static MongoDBContainer MONGO_DB;
  private MongoClient mongoClient;

  @BeforeAll
  static void init() {
    MONGO_DB = new MongoDBContainer("mongo:6.0.8");
    MONGO_DB.start();
  }

  @BeforeEach
  void setup() {
    mongoClient = MongoClients.create(MONGO_DB.getConnectionString());
    mongoClient.getDatabase(DB_NAME).drop();
  }

  @AfterEach
  void tearDown() {
    mongoClient.close();
  }

  @AfterAll
  static void cleanup() {
    MONGO_DB.stop();
  }

  @Test
  void testGetIteratorsEmptyInitialState() {
    insertDocuments(COLLECTION1, List.of(
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID1,
            NAME_FIELD, NAME1)),
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID2,
            NAME_FIELD, NAME2)),
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID3,
            NAME_FIELD, NAME3))));

    insertDocuments(COLLECTION2, List.of(
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID4,
            NAME_FIELD, NAME4)),
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID5,
            NAME_FIELD, NAME5))));

    insertDocuments(COLLECTION3, List.of(
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID6,
            NAME_FIELD, NAME6))));

    final InitialSnapshotHandler initialSnapshotHandler = new InitialSnapshotHandler();
    final MongoDbStateManager stateManager = mock(MongoDbStateManager.class);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators =
        initialSnapshotHandler.getIterators(STREAMS, stateManager, mongoClient.getDatabase(DB_NAME), null, Instant.now(),
            MongoConstants.CHECKPOINT_INTERVAL, true);

    assertEquals(iterators.size(), 2, "Only two streams are configured as incremental, full refresh streams should be ignored");

    final AutoCloseableIterator<AirbyteMessage> collection1 = iterators.get(0);
    final AutoCloseableIterator<AirbyteMessage> collection2 = iterators.get(1);

    // collection1
    final AirbyteMessage collection1StreamMessage1 = collection1.next();
    assertEquals(Type.RECORD, collection1StreamMessage1.getType());
    assertEquals(COLLECTION1, collection1StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID1.toString(), collection1StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());
    assertEquals(NAME1, collection1StreamMessage1.getRecord().getData().get(NAME_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD, NAME_FIELD), collection1StreamMessage1.getRecord().getData());

    final AirbyteMessage collection1StreamMessage2 = collection1.next();
    assertEquals(Type.RECORD, collection1StreamMessage2.getType());
    assertEquals(COLLECTION1, collection1StreamMessage2.getRecord().getStream());
    assertEquals(OBJECT_ID2.toString(), collection1StreamMessage2.getRecord().getData().get(CURSOR_FIELD).asText());
    assertEquals(NAME2, collection1StreamMessage2.getRecord().getData().get(NAME_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD, NAME_FIELD), collection1StreamMessage2.getRecord().getData());

    final AirbyteMessage collection1StreamMessage3 = collection1.next();
    assertEquals(Type.RECORD, collection1StreamMessage3.getType());
    assertEquals(COLLECTION1, collection1StreamMessage3.getRecord().getStream());
    assertEquals(OBJECT_ID3.toString(), collection1StreamMessage3.getRecord().getData().get(CURSOR_FIELD).asText());
    assertEquals(NAME3, collection1StreamMessage3.getRecord().getData().get(NAME_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD, NAME_FIELD), collection1StreamMessage3.getRecord().getData());

    final AirbyteMessage collection1SateMessage = collection1.next();
    assertEquals(Type.STATE, collection1SateMessage.getType(), "State message is expected after all records in a stream are emitted");

    assertFalse(collection1.hasNext());

    // collection2
    final AirbyteMessage collection2StreamMessage1 = collection2.next();
    assertEquals(Type.RECORD, collection2StreamMessage1.getType());
    assertEquals(COLLECTION2, collection2StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID4.toString(), collection2StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD), collection2StreamMessage1.getRecord().getData());

    final AirbyteMessage collection2StreamMessage2 = collection2.next();
    assertEquals(Type.RECORD, collection2StreamMessage2.getType());
    assertEquals(COLLECTION2, collection2StreamMessage2.getRecord().getStream());
    assertEquals(OBJECT_ID5.toString(), collection2StreamMessage2.getRecord().getData().get(CURSOR_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD), collection2StreamMessage1.getRecord().getData());

    final AirbyteMessage collection2SateMessage = collection2.next();
    assertEquals(Type.STATE, collection2SateMessage.getType(), "State message is expected after all records in a stream are emitted");

    assertFalse(collection2.hasNext());
  }

  @Test
  void testGetIteratorsNonEmptyInitialState() {
    insertDocuments(COLLECTION1, List.of(
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID1,
            NAME_FIELD, NAME1)),
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID2,
            NAME_FIELD, NAME2))));

    insertDocuments(COLLECTION2, List.of(
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID3,
            NAME_FIELD, NAME3))));

    final InitialSnapshotHandler initialSnapshotHandler = new InitialSnapshotHandler();
    final MongoDbStateManager stateManager = mock(MongoDbStateManager.class);
    when(stateManager.getStreamState(COLLECTION1, NAMESPACE))
        .thenReturn(Optional.of(new MongoDbStreamState(OBJECT_ID1_STRING, null, IdType.OBJECT_ID)));
    final List<AutoCloseableIterator<AirbyteMessage>> iterators =
        initialSnapshotHandler.getIterators(STREAMS, stateManager, mongoClient.getDatabase(DB_NAME), null, Instant.now(),
            MongoConstants.CHECKPOINT_INTERVAL, true);

    assertEquals(iterators.size(), 2, "Only two streams are configured as incremental, full refresh streams should be ignored");

    final AutoCloseableIterator<AirbyteMessage> collection1 = iterators.get(0);
    final AutoCloseableIterator<AirbyteMessage> collection2 = iterators.get(1);

    // collection1, first document should be skipped
    final AirbyteMessage collection1StreamMessage1 = collection1.next();
    assertEquals(Type.RECORD, collection1StreamMessage1.getType());
    assertEquals(COLLECTION1, collection1StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID2.toString(), collection1StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());
    assertEquals(NAME2, collection1StreamMessage1.getRecord().getData().get(NAME_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD, NAME_FIELD), collection1StreamMessage1.getRecord().getData());

    final AirbyteMessage collection1SateMessage = collection1.next();
    assertEquals(Type.STATE, collection1SateMessage.getType(), "State message is expected after all records in a stream are emitted");

    assertFalse(collection1.hasNext());

    // collection2, no documents should be skipped
    final AirbyteMessage collection2StreamMessage1 = collection2.next();
    assertEquals(Type.RECORD, collection2StreamMessage1.getType());
    assertEquals(COLLECTION2, collection2StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID3.toString(), collection2StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD), collection2StreamMessage1.getRecord().getData());

    final AirbyteMessage collection2SateMessage = collection2.next();
    assertEquals(Type.STATE, collection2SateMessage.getType(), "State message is expected after all records in a stream are emitted");

    assertFalse(collection2.hasNext());
  }

  @Test
  void testGetIteratorsThrowsExceptionWhenThereAreDifferentIdTypes() {
    insertDocuments(COLLECTION1, List.of(
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID1,
            NAME_FIELD, NAME1)),
        new Document(Map.of(
            CURSOR_FIELD, "string-id",
            NAME_FIELD, NAME2))));

    final InitialSnapshotHandler initialSnapshotHandler = new InitialSnapshotHandler();
    final MongoDbStateManager stateManager = mock(MongoDbStateManager.class);

    final var thrown = assertThrows(ConfigErrorException.class,
        () -> initialSnapshotHandler.getIterators(STREAMS, stateManager, mongoClient.getDatabase(DB_NAME), null, Instant.now(),
            MongoConstants.CHECKPOINT_INTERVAL, true));
    assertTrue(thrown.getMessage().contains("must be consistently typed"));
  }

  @Test
  void testGetIteratorsThrowsExceptionWhenThereAreUnsupportedIdTypes() {
    insertDocuments(COLLECTION1, List.of(
        new Document(Map.of(
            CURSOR_FIELD, 0.1,
            NAME_FIELD, NAME1))));

    final InitialSnapshotHandler initialSnapshotHandler = new InitialSnapshotHandler();
    final MongoDbStateManager stateManager = mock(MongoDbStateManager.class);

    final var thrown = assertThrows(ConfigErrorException.class,
        () -> initialSnapshotHandler.getIterators(STREAMS, stateManager, mongoClient.getDatabase(DB_NAME), null, Instant.now(),
            MongoConstants.CHECKPOINT_INTERVAL, true));
    assertTrue(thrown.getMessage().contains("_id fields with the following types are currently supported"));
  }

  private void assertConfiguredFieldsEqualsRecordDataFields(final Set<String> configuredStreamFields, final JsonNode recordMessageData) {
    final Set<String> recordDataFields = ImmutableSet.copyOf(recordMessageData.fieldNames());
    assertEquals(configuredStreamFields, recordDataFields,
        "Fields in record message should be the same as fields in their corresponding stream configuration");
  }

  private void insertDocuments(final String collectionName, final List<Document> documents) {
    final MongoCollection<Document> collection = mongoClient.getDatabase(DB_NAME).getCollection(collectionName);
    collection.insertMany(documents);
  }

  @Test
  void testGetIteratorsWithOneEmptyCollection() {
    insertDocuments(COLLECTION1, List.of(
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID1,
            NAME_FIELD, NAME1))));

    final InitialSnapshotHandler initialSnapshotHandler = new InitialSnapshotHandler();
    final MongoDbStateManager stateManager = mock(MongoDbStateManager.class);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators =
        initialSnapshotHandler.getIterators(STREAMS, stateManager, mongoClient.getDatabase(DB_NAME), null, Instant.now(),
            MongoConstants.CHECKPOINT_INTERVAL, true);

    assertEquals(iterators.size(), 2, "Only two streams are configured as incremental, full refresh streams should be ignored");

    final AutoCloseableIterator<AirbyteMessage> collection1 = iterators.get(0);
    final AutoCloseableIterator<AirbyteMessage> collection2 = iterators.get(1);

    // collection1
    final AirbyteMessage collection1StreamMessage1 = collection1.next();
    assertEquals(Type.RECORD, collection1StreamMessage1.getType());
    assertEquals(COLLECTION1, collection1StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID1.toString(), collection1StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());
    assertEquals(NAME1, collection1StreamMessage1.getRecord().getData().get(NAME_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD, NAME_FIELD), collection1StreamMessage1.getRecord().getData());

    final AirbyteMessage collection1SateMessage = collection1.next();
    assertEquals(Type.STATE, collection1SateMessage.getType(), "State message is expected after all records in a stream are emitted");

    assertFalse(collection1.hasNext());

    // collection2
    assertFalse(collection2.hasNext());
  }

  @Test
  void testGetIteratorsWithInitialStateNonDefaultIdType() {
    insertDocuments(COLLECTION1, List.of(
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID1_STRING,
            NAME_FIELD, NAME1)),
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID2_STRING,
            NAME_FIELD, NAME2))));

    insertDocuments(COLLECTION2, List.of(
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID3_STRING,
            NAME_FIELD, NAME3))));

    final InitialSnapshotHandler initialSnapshotHandler = new InitialSnapshotHandler();
    final MongoDbStateManager stateManager = mock(MongoDbStateManager.class);
    when(stateManager.getStreamState(COLLECTION1, NAMESPACE))
        .thenReturn(Optional.of(new MongoDbStreamState(OBJECT_ID1_STRING, null, IdType.STRING)));
    final List<AutoCloseableIterator<AirbyteMessage>> iterators =
        initialSnapshotHandler.getIterators(STREAMS, stateManager, mongoClient.getDatabase(DB_NAME), null, Instant.now(),
            MongoConstants.CHECKPOINT_INTERVAL, true);

    assertEquals(iterators.size(), 2, "Only two streams are configured as incremental, full refresh streams should be ignored");

    final AutoCloseableIterator<AirbyteMessage> collection1 = iterators.get(0);
    final AutoCloseableIterator<AirbyteMessage> collection2 = iterators.get(1);

    // collection1, first document should be skipped
    final AirbyteMessage collection1StreamMessage1 = collection1.next();
    assertEquals(Type.RECORD, collection1StreamMessage1.getType());
    assertEquals(COLLECTION1, collection1StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID2.toString(), collection1StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());
    assertEquals(NAME2, collection1StreamMessage1.getRecord().getData().get(NAME_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD, NAME_FIELD), collection1StreamMessage1.getRecord().getData());

    final AirbyteMessage collection1SateMessage = collection1.next();
    assertEquals(Type.STATE, collection1SateMessage.getType(), "State message is expected after all records in a stream are emitted");

    assertFalse(collection1.hasNext());

    // collection2, no documents should be skipped
    final AirbyteMessage collection2StreamMessage1 = collection2.next();
    assertEquals(Type.RECORD, collection2StreamMessage1.getType());
    assertEquals(COLLECTION2, collection2StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID3.toString(), collection2StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD), collection2StreamMessage1.getRecord().getData());

    final AirbyteMessage collection2SateMessage = collection2.next();
    assertEquals(Type.STATE, collection2SateMessage.getType(), "State message is expected after all records in a stream are emitted");

    assertFalse(collection2.hasNext());
  }

}
