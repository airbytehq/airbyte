/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_DELETED_AT;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_UPDATED_AT;
import static io.airbyte.integrations.source.mongodb.MongoConstants.DATABASE_CONFIG_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcConnectorMetadataInjector.CDC_DEFAULT_CURSOR;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableSet;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants;
import io.airbyte.integrations.source.mongodb.state.IdType;
import io.airbyte.integrations.source.mongodb.state.InitialSnapshotStatus;
import io.airbyte.integrations.source.mongodb.state.MongoDbStateManager;
import io.airbyte.integrations.source.mongodb.state.MongoDbStreamState;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.*;
import org.bson.BsonBinarySubType;
import org.bson.Document;
import org.bson.UuidRepresentation;
import org.bson.internal.UuidHelper;
import org.bson.types.Binary;
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
  private static final String COLLECTION4 = "collection4";

  private static final String OBJECT_ID1_STRING = "64c0029d95ad260d69ef28a1";
  private static final String OBJECT_ID2_STRING = "64c0029d95ad260d69ef28a2";
  private static final String OBJECT_ID3_STRING = "64c0029d95ad260d69ef28a3";
  private static final String OBJECT_ID4_STRING = "64c0029d95ad260d69ef28a4";
  private static final String OBJECT_ID5_STRING = "64c0029d95ad260d69ef28a5";
  private static final String OBJECT_ID6_STRING = "64c0029d95ad260d69ef28a6";
  private static final String OBJECT_ID7_STRING = "enp6enp6enp6eg==";
  private static final String OBJECT_ID8_STRING = "8cee6d1e-ce07-4dc9-8bcb-c99c5a163a75";
  private static final ObjectId OBJECT_ID1 = new ObjectId(OBJECT_ID1_STRING);
  private static final ObjectId OBJECT_ID2 = new ObjectId(OBJECT_ID2_STRING);
  private static final ObjectId OBJECT_ID3 = new ObjectId(OBJECT_ID3_STRING);
  private static final ObjectId OBJECT_ID4 = new ObjectId(OBJECT_ID4_STRING);
  private static final ObjectId OBJECT_ID5 = new ObjectId(OBJECT_ID5_STRING);
  private static final ObjectId OBJECT_ID6 = new ObjectId(OBJECT_ID6_STRING);
  private static final Binary OBJECT_ID7 = new Binary(Base64.getDecoder().decode(OBJECT_ID7_STRING));
  private static final Binary OBJECT_ID8 =
      new Binary(BsonBinarySubType.UUID_STANDARD, UuidHelper.encodeUuidToBinary(UUID.fromString(OBJECT_ID8_STRING), UuidRepresentation.STANDARD));
  private static final String NAME1 = "name1";
  private static final String NAME2 = "name2";
  private static final String NAME3 = "name3";
  private static final String NAME4 = "name4";
  private static final String NAME5 = "name5";
  private static final String NAME6 = "name6";
  private static final String NAME7 = "name7";
  private static final String NAME8 = "name8";

  private static final String DATABASE = "test-database";

  final MongoDbSourceConfig CONFIG = new MongoDbSourceConfig(Jsons.jsonNode(
      Map.of(DATABASE_CONFIG_CONFIGURATION_KEY,
          Map.of(
              MongoDbDebeziumConstants.Configuration.CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://host:12345/",
              MongoDbDebeziumConstants.Configuration.DATABASE_CONFIGURATION_KEY, DATABASE))));

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
          .withSyncMode(SyncMode.FULL_REFRESH),
      CatalogHelpers.createConfiguredAirbyteStream(
          COLLECTION4,
          NAMESPACE,
          Field.of(CURSOR_FIELD, JsonSchemaType.STRING),
          Field.of(NAME_FIELD, JsonSchemaType.STRING))
          .withSyncMode(SyncMode.INCREMENTAL));

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

    insertDocuments(COLLECTION4, List.of(
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID7,
            NAME_FIELD, NAME7)),
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID8,
            NAME_FIELD, NAME8))));

    final InitialSnapshotHandler initialSnapshotHandler = new InitialSnapshotHandler();
    final MongoDbStateManager ogStateManager = MongoDbStateManager.createStateManager(null, CONFIG);
    final MongoDbStateManager stateManager = spy(ogStateManager);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators =
        initialSnapshotHandler.getIterators(STREAMS, stateManager, mongoClient.getDatabase(DB_NAME), CONFIG, false, false);

    assertEquals(iterators.size(), 4);

    final AutoCloseableIterator<AirbyteMessage> collection1 = iterators.get(0);
    final AutoCloseableIterator<AirbyteMessage> collection2 = iterators.get(1);
    final AutoCloseableIterator<AirbyteMessage> collection3 = iterators.get(2);
    final AutoCloseableIterator<AirbyteMessage> collection4 = iterators.get(3);

    // collection1
    final AirbyteMessage collection1StreamMessage1 = collection1.next();
    assertEquals(Type.RECORD, collection1StreamMessage1.getType());
    assertEquals(COLLECTION1, collection1StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID1.toString(), collection1StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());
    assertEquals(NAME1, collection1StreamMessage1.getRecord().getData().get(NAME_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD, NAME_FIELD, CDC_UPDATED_AT, CDC_DELETED_AT, CDC_DEFAULT_CURSOR),
        collection1StreamMessage1.getRecord().getData());

    final AirbyteMessage collection1StreamMessage2 = collection1.next();
    assertEquals(Type.RECORD, collection1StreamMessage2.getType());
    assertEquals(COLLECTION1, collection1StreamMessage2.getRecord().getStream());
    assertEquals(OBJECT_ID2.toString(), collection1StreamMessage2.getRecord().getData().get(CURSOR_FIELD).asText());
    assertEquals(NAME2, collection1StreamMessage2.getRecord().getData().get(NAME_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD, NAME_FIELD, CDC_UPDATED_AT, CDC_DELETED_AT, CDC_DEFAULT_CURSOR),
        collection1StreamMessage2.getRecord().getData());

    final AirbyteMessage collection1StreamMessage3 = collection1.next();
    assertEquals(Type.RECORD, collection1StreamMessage3.getType());
    assertEquals(COLLECTION1, collection1StreamMessage3.getRecord().getStream());
    assertEquals(OBJECT_ID3.toString(), collection1StreamMessage3.getRecord().getData().get(CURSOR_FIELD).asText());
    assertEquals(NAME3, collection1StreamMessage3.getRecord().getData().get(NAME_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD, NAME_FIELD, CDC_UPDATED_AT, CDC_DELETED_AT, CDC_DEFAULT_CURSOR),
        collection1StreamMessage3.getRecord().getData());

    final AirbyteMessage collection1SateMessage = collection1.next();
    assertEquals(Type.STATE, collection1SateMessage.getType(), "State message is expected after all records in a stream are emitted");

    assertFalse(collection1.hasNext());

    // collection2
    final AirbyteMessage collection2StreamMessage1 = collection2.next();
    assertEquals(Type.RECORD, collection2StreamMessage1.getType());
    assertEquals(COLLECTION2, collection2StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID4.toString(), collection2StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD, CDC_UPDATED_AT, CDC_DELETED_AT, CDC_DEFAULT_CURSOR),
        collection2StreamMessage1.getRecord().getData());

    final AirbyteMessage collection2StreamMessage2 = collection2.next();
    assertEquals(Type.RECORD, collection2StreamMessage2.getType());
    assertEquals(COLLECTION2, collection2StreamMessage2.getRecord().getStream());
    assertEquals(OBJECT_ID5.toString(), collection2StreamMessage2.getRecord().getData().get(CURSOR_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD, CDC_UPDATED_AT, CDC_DELETED_AT, CDC_DEFAULT_CURSOR),
        collection2StreamMessage1.getRecord().getData());

    final AirbyteMessage collection2SateMessage = collection2.next();
    assertEquals(Type.STATE, collection2SateMessage.getType(), "State message is expected after all records in a stream are emitted");

    assertFalse(collection2.hasNext());

    final AirbyteMessage collection3StreamMessage1 = collection3.next();
    assertEquals(Type.RECORD, collection3StreamMessage1.getType());
    assertEquals(COLLECTION3, collection3StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID6.toString(), collection3StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());
    // Full refresh record have no cdc fields
    assertTrue(collection3StreamMessage1.getRecord().getData().has(CURSOR_FIELD));
    assertFalse(collection3StreamMessage1.getRecord().getData().has(CDC_UPDATED_AT));
    assertFalse(collection3StreamMessage1.getRecord().getData().has(CDC_DELETED_AT));
    assertFalse(collection3StreamMessage1.getRecord().getData().has(CDC_DEFAULT_CURSOR));

    final AirbyteMessage collection3SateMessage = collection3.next();
    assertEquals(Type.STATE, collection3SateMessage.getType(), "State message is expected after all records in a stream are emitted");

    // collection4
    final AirbyteMessage collection4StreamMessage1 = collection4.next();
    assertEquals(Type.RECORD, collection1StreamMessage1.getType());
    assertEquals(COLLECTION4, collection4StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID7_STRING, collection4StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());
    assertEquals(NAME7, collection4StreamMessage1.getRecord().getData().get(NAME_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD, NAME_FIELD, CDC_UPDATED_AT, CDC_DELETED_AT, CDC_DEFAULT_CURSOR),
        collection4StreamMessage1.getRecord().getData());

    final AirbyteMessage collection4StreamMessage2 = collection4.next();
    assertEquals(Type.RECORD, collection4StreamMessage2.getType());
    assertEquals(COLLECTION4, collection4StreamMessage2.getRecord().getStream());
    assertEquals(Base64.getEncoder().encodeToString(OBJECT_ID8.getData()),
        collection4StreamMessage2.getRecord().getData().get(CURSOR_FIELD).asText());
    assertEquals(NAME8, collection4StreamMessage2.getRecord().getData().get(NAME_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD, NAME_FIELD, CDC_UPDATED_AT, CDC_DELETED_AT, CDC_DEFAULT_CURSOR),
        collection4StreamMessage2.getRecord().getData());

    final AirbyteMessage collection4StateMessage = collection4.next();
    assertEquals(Type.STATE, collection4StateMessage.getType(), "State message is expected after all records in a stream are emitted");
    assertEquals(OBJECT_ID8_STRING, collection4StateMessage.getState().getGlobal().getStreamStates().get(3).getStreamState().get("id").asText());
    assertFalse(collection4.hasNext());

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

    insertDocuments(COLLECTION3, List.of(
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID4,
            NAME_FIELD, NAME4)),
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID5,
            NAME_FIELD, NAME5))));

    insertDocuments(COLLECTION4, List.of(
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID7,
            NAME_FIELD, NAME7))));

    final InitialSnapshotHandler initialSnapshotHandler = new InitialSnapshotHandler();
    final MongoDbStateManager ogStateManager = MongoDbStateManager.createStateManager(null, CONFIG);
    final MongoDbStateManager stateManager = spy(ogStateManager);
    when(stateManager.getStreamState(COLLECTION1, NAMESPACE))
        .thenReturn(Optional.of(new MongoDbStreamState(OBJECT_ID1_STRING, null, IdType.OBJECT_ID)));
    when(stateManager.getStreamState(COLLECTION3, NAMESPACE))
        .thenReturn(Optional.of(new MongoDbStreamState(OBJECT_ID4_STRING, InitialSnapshotStatus.FULL_REFRESH, IdType.OBJECT_ID)));
    final List<AutoCloseableIterator<AirbyteMessage>> iterators =
        initialSnapshotHandler.getIterators(STREAMS, stateManager, mongoClient.getDatabase(DB_NAME), CONFIG, false, false);

    assertEquals(iterators.size(), 4);

    final AutoCloseableIterator<AirbyteMessage> collection1 = iterators.get(0);
    final AutoCloseableIterator<AirbyteMessage> collection2 = iterators.get(1);
    final AutoCloseableIterator<AirbyteMessage> collection3 = iterators.get(2);
    final AutoCloseableIterator<AirbyteMessage> collection4 = iterators.get(3);

    // collection1, first document should be skipped
    final AirbyteMessage collection1StreamMessage1 = collection1.next();
    assertEquals(Type.RECORD, collection1StreamMessage1.getType());
    assertEquals(COLLECTION1, collection1StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID2.toString(), collection1StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());
    assertEquals(NAME2, collection1StreamMessage1.getRecord().getData().get(NAME_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD, NAME_FIELD, CDC_UPDATED_AT, CDC_DELETED_AT, CDC_DEFAULT_CURSOR),
        collection1StreamMessage1.getRecord().getData());

    final AirbyteMessage collection1SateMessage = collection1.next();
    assertEquals(Type.STATE, collection1SateMessage.getType(), "State message is expected after all records in a stream are emitted");

    assertFalse(collection1.hasNext());

    // collection2, no documents should be skipped
    final AirbyteMessage collection2StreamMessage1 = collection2.next();
    assertEquals(Type.RECORD, collection2StreamMessage1.getType());
    assertEquals(COLLECTION2, collection2StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID3.toString(), collection2StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD, CDC_UPDATED_AT, CDC_DELETED_AT, CDC_DEFAULT_CURSOR),
        collection2StreamMessage1.getRecord().getData());

    final AirbyteMessage collection2SateMessage = collection2.next();
    assertEquals(Type.STATE, collection2SateMessage.getType(), "State message is expected after all records in a stream are emitted");

    assertFalse(collection2.hasNext());

    // collection3 will skip the first document
    final AirbyteMessage collection3StreamMessage1 = collection3.next();
    assertEquals(Type.RECORD, collection3StreamMessage1.getType());
    assertEquals(COLLECTION3, collection3StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID5.toString(), collection3StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());
    assertEquals(NAME5, collection3StreamMessage1.getRecord().getData().get(NAME_FIELD).asText());

    final AirbyteMessage collection3StateMessage = collection3.next();
    assertEquals(Type.STATE, collection3StateMessage.getType(), "State message is expected after all records in a stream are emitted");
    assertFalse(collection3.hasNext());

    // collection4, no documents should be skipped
    final AirbyteMessage collection4StreamMessage1 = collection4.next();
    assertEquals(Type.RECORD, collection4StreamMessage1.getType());
    assertEquals(COLLECTION4, collection4StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID7_STRING, collection4StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());
    assertEquals(NAME7, collection4StreamMessage1.getRecord().getData().get(NAME_FIELD).asText());

    final AirbyteMessage collection4StateMessage = collection4.next();
    assertEquals(Type.STATE, collection3StateMessage.getType(), "State message is expected after all records in a stream are emitted");
    assertFalse(collection4.hasNext());
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
        () -> initialSnapshotHandler.getIterators(STREAMS, stateManager, mongoClient.getDatabase(DB_NAME),
            /* MongoConstants.CHECKPOINT_INTERVAL, true */ CONFIG, false, false));
    assertTrue(thrown.getMessage().contains("must be consistently typed"));
  }

  @Test
  void testGetIteratorsThrowsExceptionWhenThereAreUnsupportedIdTypes() {
    insertDocuments(COLLECTION1, List.of(
        new Document(Map.of(
            CURSOR_FIELD, 0.1,
            NAME_FIELD, NAME1))));

    final InitialSnapshotHandler initialSnapshotHandler = new InitialSnapshotHandler();
    final MongoDbStateManager stateManager = spy(MongoDbStateManager.class);

    final var thrown = assertThrows(ConfigErrorException.class,
        () -> initialSnapshotHandler.getIterators(STREAMS, stateManager, mongoClient.getDatabase(DB_NAME),
            /* MongoConstants.CHECKPOINT_INTERVAL, true */ CONFIG, false, false));
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
    final MongoDbStateManager ogStateManager = MongoDbStateManager.createStateManager(null, CONFIG);
    final MongoDbStateManager stateManager = spy(ogStateManager);
    final List<AutoCloseableIterator<AirbyteMessage>> iterators =
        initialSnapshotHandler.getIterators(STREAMS, stateManager, mongoClient.getDatabase(DB_NAME), CONFIG, false, false);

    assertEquals(iterators.size(), 4);

    final AutoCloseableIterator<AirbyteMessage> collection1 = iterators.get(0);
    final AutoCloseableIterator<AirbyteMessage> collection2 = iterators.get(1);
    final AutoCloseableIterator<AirbyteMessage> collection3 = iterators.get(2);
    final AutoCloseableIterator<AirbyteMessage> collection4 = iterators.get(3);

    // collection1
    final AirbyteMessage collection1StreamMessage1 = collection1.next();
    assertEquals(Type.RECORD, collection1StreamMessage1.getType());
    assertEquals(COLLECTION1, collection1StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID1.toString(), collection1StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());
    assertEquals(NAME1, collection1StreamMessage1.getRecord().getData().get(NAME_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD, NAME_FIELD, CDC_UPDATED_AT, CDC_DELETED_AT, CDC_DEFAULT_CURSOR),
        collection1StreamMessage1.getRecord().getData());

    final AirbyteMessage collection1SateMessage = collection1.next();
    assertEquals(Type.STATE, collection1SateMessage.getType(), "State message is expected after all records in a stream are emitted");

    assertFalse(collection1.hasNext());

    // collection2 will generate a final state.

    final AirbyteMessage collection2StateMessage = collection2.next();
    assertEquals(Type.STATE, collection2StateMessage.getType(), "State message is expected after all records in a stream are emitted");
    assertFalse(collection2.hasNext());

    // collection3 will generate a final state.

    final AirbyteMessage collection3StateMessage = collection3.next();
    assertEquals(Type.STATE, collection3StateMessage.getType(), "State message is expected after all records in a stream are emitted");
    assertFalse(collection3.hasNext());

    // collection4 will generate a final state.

    final AirbyteMessage collection4StateMessage = collection4.next();
    assertEquals(Type.STATE, collection3StateMessage.getType(), "State message is expected after all records in a stream are emitted");
    assertFalse(collection4.hasNext());
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

    insertDocuments(COLLECTION3, List.of(
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID4_STRING,
            NAME_FIELD, NAME4))));

    insertDocuments(COLLECTION4, List.of(
        new Document(Map.of(
            CURSOR_FIELD, OBJECT_ID7,
            NAME_FIELD, NAME7))));

    final InitialSnapshotHandler initialSnapshotHandler = new InitialSnapshotHandler();
    final MongoDbStateManager ogStateManager = MongoDbStateManager.createStateManager(null, CONFIG);
    final MongoDbStateManager stateManager = spy(ogStateManager);
    when(stateManager.getStreamState(COLLECTION1, NAMESPACE))
        .thenReturn(Optional.of(new MongoDbStreamState(OBJECT_ID1_STRING, null, IdType.STRING)));
    final List<AutoCloseableIterator<AirbyteMessage>> iterators =
        initialSnapshotHandler.getIterators(STREAMS, stateManager, mongoClient.getDatabase(DB_NAME), CONFIG, false, false);

    assertEquals(iterators.size(), 4);

    final AutoCloseableIterator<AirbyteMessage> collection1 = iterators.get(0);
    final AutoCloseableIterator<AirbyteMessage> collection2 = iterators.get(1);
    final AutoCloseableIterator<AirbyteMessage> collection3 = iterators.get(2);
    final AutoCloseableIterator<AirbyteMessage> collection4 = iterators.get(3);

    // collection1, first document should be skipped
    final AirbyteMessage collection1StreamMessage1 = collection1.next();
    System.out.println("message 1: " + collection1StreamMessage1);
    final AirbyteMessage collection2StreamMessage1 = collection2.next();
    System.out.println("message 2: " + collection2StreamMessage1);
    final AirbyteMessage collection3StreamMessage1 = collection3.next();

    assertEquals(Type.RECORD, collection1StreamMessage1.getType());
    assertEquals(COLLECTION1, collection1StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID2.toString(), collection1StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());
    assertEquals(NAME2, collection1StreamMessage1.getRecord().getData().get(NAME_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD, NAME_FIELD, CDC_UPDATED_AT, CDC_DELETED_AT, CDC_DEFAULT_CURSOR),
        collection1StreamMessage1.getRecord().getData());

    final AirbyteMessage collection1SateMessage = collection1.next();
    assertEquals(Type.STATE, collection1SateMessage.getType(), "State message is expected after all records in a stream are emitted");

    assertFalse(collection1.hasNext());

    // collection2, no documents should be skipped
    assertEquals(Type.RECORD, collection2StreamMessage1.getType());
    assertEquals(COLLECTION2, collection2StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID3.toString(), collection2StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());
    assertConfiguredFieldsEqualsRecordDataFields(Set.of(CURSOR_FIELD, CDC_UPDATED_AT, CDC_DELETED_AT, CDC_DEFAULT_CURSOR),
        collection2StreamMessage1.getRecord().getData());

    final AirbyteMessage collection2SateMessage = collection2.next();
    assertEquals(Type.STATE, collection2SateMessage.getType(), "State message is expected after all records in a stream are emitted");

    assertFalse(collection2.hasNext());

    // collection3, no documents should be skipped
    assertEquals(Type.RECORD, collection3StreamMessage1.getType());
    assertEquals(COLLECTION3, collection3StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID4.toString(), collection3StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());

    final AirbyteMessage collection3SateMessage = collection3.next();
    assertEquals(Type.STATE, collection3SateMessage.getType(), "State message is expected after all records in a stream are emitted");

    assertFalse(collection3.hasNext());

    // collection4, no documents should be skipped
    final AirbyteMessage collection4StreamMessage1 = collection4.next();
    assertEquals(Type.RECORD, collection4StreamMessage1.getType());
    assertEquals(COLLECTION4, collection4StreamMessage1.getRecord().getStream());
    assertEquals(OBJECT_ID7_STRING, collection4StreamMessage1.getRecord().getData().get(CURSOR_FIELD).asText());

    final AirbyteMessage collection4SateMessage = collection4.next();
    assertEquals(Type.STATE, collection3SateMessage.getType(), "State message is expected after all records in a stream are emitted");
    assertEquals(OBJECT_ID7_STRING, collection4SateMessage.getState().getGlobal().getStreamStates().get(3).getStreamState().get("id").asText());
    assertFalse(collection4.hasNext());
  }

}
