/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal;

import static io.airbyte.integrations.source.mongodb.internal.MongoCatalogHelper.DEFAULT_CURSOR_FIELD;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.CHECKPOINT_INTERVAL_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.DATABASE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.IS_TEST_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.REPLICA_SET_CONFIGURATION_KEY;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Iterables;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCollection;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.debezium.internals.ChangeEventWithMetadata;
import io.airbyte.integrations.debezium.internals.SnapshotMetadata;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbCdcTargetPosition;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumStateUtil;
import io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcState;
import io.airbyte.integrations.source.mongodb.internal.state.InitialSnapshotStatus;
import io.airbyte.integrations.source.mongodb.internal.state.MongoDbStreamState;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import org.bson.BsonArray;
import org.bson.BsonString;
import org.bson.BsonTimestamp;
import org.bson.Document;
import org.bson.types.ObjectId;
import org.junit.jupiter.api.Test;

public class MongoDbSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String DATABASE_NAME = "test";
  private static final String COLLECTION_NAME = "acceptance_test1";
  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");
  private static final String DOUBLE_TEST_FIELD = "double_test";
  private static final String EMPTY_TEST_FIELD = "empty_test";
  private static final String ID_FIELD = "id";
  private static final String INT_TEST_FIELD = "int_test";
  private static final String NAME_FIELD = "name";
  private static final String OBJECT_TEST_FIELD = "object_test";
  private static final String OTHER_COLLECTION_NAME = "acceptance_test2";
  private static final String TEST_FIELD = "test";
  private static final String TEST_ARRAY_FIELD = "test_array";

  protected JsonNode config;
  protected MongoClient mongoClient;

  private int recordCount = 0;

  @Override
  protected void setupEnvironment(final TestDestinationEnv testEnv) throws Exception {
    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a MongoDB credentials file. By default {module-root}/" + CREDENTIALS_PATH
              + ". Override by setting setting path with the CREDENTIALS_PATH constant.");
    }

    config = Jsons.deserialize(Files.readString(CREDENTIALS_PATH));
    ((ObjectNode) config).put(DATABASE_CONFIGURATION_KEY, DATABASE_NAME);
    ((ObjectNode) config).put(IS_TEST_CONFIGURATION_KEY, true);
    ((ObjectNode) config).put(CHECKPOINT_INTERVAL_CONFIGURATION_KEY, 1);

    mongoClient = MongoConnectionUtils.createMongoClient(config);
    mongoClient.getDatabase(DATABASE_NAME).createCollection(COLLECTION_NAME);
    mongoClient.getDatabase(DATABASE_NAME).createCollection(OTHER_COLLECTION_NAME);

    insertTestData(mongoClient);
  }

  private void insertTestData(final MongoClient mongoClient) {
    final MongoCollection<Document> collection = mongoClient.getDatabase(DATABASE_NAME).getCollection(COLLECTION_NAME);
    final var objectDocument =
        new Document("testObject", new Document(NAME_FIELD, "subName").append("testField1", "testField1").append(INT_TEST_FIELD, 10)
            .append("thirdLevelDocument", new Document("data", "someData").append("intData", 1)));

    final var doc1 = new Document("_id", new ObjectId("64c0029d95ad260d69ef28a0"))
        .append(ID_FIELD, "0001").append(NAME_FIELD, "Test")
        .append(TEST_FIELD, 10).append(TEST_ARRAY_FIELD, new BsonArray(List.of(new BsonString("test"), new BsonString("mongo"))))
        .append(DOUBLE_TEST_FIELD, 100.12).append(INT_TEST_FIELD, 100).append(OBJECT_TEST_FIELD, objectDocument);

    final var doc2 = new Document("_id", new ObjectId("64c0029d95ad260d69ef28a1"))
        .append(ID_FIELD, "0002").append(NAME_FIELD, "Mongo").append(TEST_FIELD, "test_value").append(INT_TEST_FIELD, 201)
        .append(OBJECT_TEST_FIELD, objectDocument);

    final var doc3 = new Document("_id", new ObjectId("64c0029d95ad260d69ef28a2"))
        .append(ID_FIELD, "0003").append(NAME_FIELD, "Source").append(TEST_FIELD, null)
        .append(DOUBLE_TEST_FIELD, 212.11).append(INT_TEST_FIELD, 302).append(OBJECT_TEST_FIELD, objectDocument);

    final List<Document> newDocuments = List.of(doc1, doc2, doc3);
    recordCount += newDocuments.size();
    collection.insertMany(newDocuments);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    mongoClient.getDatabase(DATABASE_NAME).getCollection(COLLECTION_NAME).drop();
    mongoClient.getDatabase(DATABASE_NAME).getCollection(OTHER_COLLECTION_NAME).drop();
    mongoClient.close();
    recordCount = 0;
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-mongodb-internal-poc:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    final List<Field> fields = List.of(
        Field.of(DEFAULT_CURSOR_FIELD, JsonSchemaType.STRING),
        Field.of(ID_FIELD, JsonSchemaType.STRING),
        Field.of(NAME_FIELD, JsonSchemaType.STRING),
        Field.of(TEST_FIELD, JsonSchemaType.STRING),
        Field.of(TEST_ARRAY_FIELD, JsonSchemaType.ARRAY),
        Field.of(EMPTY_TEST_FIELD, JsonSchemaType.STRING),
        Field.of(DOUBLE_TEST_FIELD, JsonSchemaType.NUMBER),
        Field.of(INT_TEST_FIELD, JsonSchemaType.NUMBER),
        Field.of(OBJECT_TEST_FIELD, JsonSchemaType.OBJECT));

    return getConfiguredCatalog(fields);
  }

  private ConfiguredAirbyteCatalog getConfiguredCatalog(final List<Field> enabledFields) {
    final AirbyteStream airbyteStream = MongoCatalogHelper.buildAirbyteStream(COLLECTION_NAME, DATABASE_NAME, enabledFields);
    final ConfiguredAirbyteStream configuredIncrementalAirbyteStream = convertToConfiguredAirbyteStream(airbyteStream, SyncMode.INCREMENTAL);
    final List<ConfiguredAirbyteStream> streams = new ArrayList<>();
    streams.add(configuredIncrementalAirbyteStream);
    return new ConfiguredAirbyteCatalog().withStreams(streams);
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

  @Test
  public void testIncrementalReadSelectedColumns() throws Exception {
    final List<Field> selectedColumns = List.of(Field.of(NAME_FIELD, JsonSchemaType.STRING));
    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog(selectedColumns);
    final List<AirbyteMessage> allMessages = runRead(catalog);

    final List<AirbyteRecordMessage> records = filterRecords(allMessages);
    assertFalse(records.isEmpty(), "Expected a incremental sync to produce records");
    verifyFieldNotExist(records, COLLECTION_NAME, DOUBLE_TEST_FIELD);
    verifyFieldNotExist(records, COLLECTION_NAME, EMPTY_TEST_FIELD);
    verifyFieldNotExist(records, COLLECTION_NAME, ID_FIELD);
    verifyFieldNotExist(records, COLLECTION_NAME, INT_TEST_FIELD);
    verifyFieldNotExist(records, COLLECTION_NAME, OBJECT_TEST_FIELD);
    verifyFieldNotExist(records, COLLECTION_NAME, TEST_FIELD);
    verifyFieldNotExist(records, COLLECTION_NAME, TEST_ARRAY_FIELD);
  }

  @Test
  void testSyncEmptyCollection() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalog();
    final AirbyteStream otherAirbyteStream = MongoCatalogHelper.buildAirbyteStream(OTHER_COLLECTION_NAME, DATABASE_NAME,
        List.of(Field.of(NAME_FIELD, JsonSchemaType.STRING), Field.of(INT_TEST_FIELD, JsonSchemaType.NUMBER)));
    configuredCatalog.withStreams(List.of(convertToConfiguredAirbyteStream(otherAirbyteStream, SyncMode.INCREMENTAL)));

    final List<AirbyteMessage> messages = runRead(configuredCatalog);
    final List<AirbyteRecordMessage> recordMessages = filterRecords(messages);
    final List<AirbyteStateMessage> stateMessages = filterStateMessages(messages);

    assertEquals(0, recordMessages.size());
    assertEquals(0, stateMessages.size());
  }

  @Test
  void testCDCStreamCheckpointingWithMultipleStreams() throws Exception {
    final int otherCollectionCount = 100;
    insertData(DATABASE_NAME, OTHER_COLLECTION_NAME, otherCollectionCount);

    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalog();
    final List<ConfiguredAirbyteStream> streams = configuredCatalog.getStreams();
    final AirbyteStream otherAirbyteStream = MongoCatalogHelper.buildAirbyteStream(OTHER_COLLECTION_NAME, DATABASE_NAME,
        List.of(Field.of(NAME_FIELD, JsonSchemaType.STRING), Field.of(INT_TEST_FIELD, JsonSchemaType.NUMBER)));
    streams.add(convertToConfiguredAirbyteStream(otherAirbyteStream, SyncMode.INCREMENTAL));
    configuredCatalog.withStreams(streams);

    // Start a sync with two streams
    final List<AirbyteMessage> messages = runRead(configuredCatalog);
    final List<AirbyteRecordMessage> recordMessages = filterRecords(messages);
    final List<AirbyteStateMessage> stateMessages = filterStateMessages(messages);

    assertEquals(recordCount + otherCollectionCount, recordMessages.size());
    assertEquals(recordCount + otherCollectionCount + 1, stateMessages.size());

    validateStateMessages(stateMessages);

    final AirbyteStateMessage lastStateMessage = Iterables.getLast(stateMessages);
    assertNotNull(lastStateMessage.getGlobal().getSharedState());
    assertFalse(lastStateMessage.getGlobal().getSharedState().isEmpty());
    assertTrue(lastStateMessage.getGlobal().getStreamStates().stream().filter(createStateStreamFilter(COLLECTION_NAME, DATABASE_NAME)).findFirst()
        .isPresent());
    assertTrue(
        lastStateMessage.getGlobal().getStreamStates().stream().filter(createStateStreamFilter(OTHER_COLLECTION_NAME, DATABASE_NAME)).findFirst()
            .isPresent());
    assertEquals(InitialSnapshotStatus.COMPLETE, Jsons.object(lastStateMessage.getGlobal().getStreamStates().stream()
        .filter(createStateStreamFilter(COLLECTION_NAME, DATABASE_NAME)).findFirst().get().getStreamState(), MongoDbStreamState.class).status());

    // Start a second sync from somewhere in the middle of stream 2 in order to test that only stream 2
    // is synced via initial snapshot
    final List<AirbyteMessage> messages2 = runRead(configuredCatalog, Jsons.jsonNode(List.of(stateMessages.get(recordCount + 50))));
    final List<AirbyteRecordMessage> recordMessages2 = filterRecords(messages2);
    final List<AirbyteStateMessage> stateMessages2 = filterStateMessages(messages2);

    assertEquals(49, recordMessages2.size());
    assertEquals(50, stateMessages2.size());

    validateStateMessages(stateMessages2);

    final AirbyteStateMessage lastStateMessage2 = Iterables.getLast(stateMessages2);
    assertNotNull(lastStateMessage2.getGlobal().getSharedState());
    assertFalse(lastStateMessage2.getGlobal().getSharedState().isEmpty());
    assertTrue(lastStateMessage2.getGlobal().getStreamStates().stream().filter(createStateStreamFilter(COLLECTION_NAME, DATABASE_NAME)).findFirst()
        .isPresent());
    assertTrue(
        lastStateMessage2.getGlobal().getStreamStates().stream().filter(createStateStreamFilter(OTHER_COLLECTION_NAME, DATABASE_NAME)).findFirst()
            .isPresent());
    assertEquals(InitialSnapshotStatus.COMPLETE, Jsons.object(lastStateMessage2.getGlobal().getStreamStates().stream()
        .filter(createStateStreamFilter(COLLECTION_NAME, DATABASE_NAME)).findFirst().get().getStreamState(), MongoDbStreamState.class).status());
    assertEquals(InitialSnapshotStatus.COMPLETE, Jsons.object(lastStateMessage2.getGlobal().getStreamStates().stream()
        .filter(createStateStreamFilter(OTHER_COLLECTION_NAME, DATABASE_NAME)).findFirst().get().getStreamState(), MongoDbStreamState.class)
        .status());

    // Insert more data for one stream
    insertData(DATABASE_NAME, OTHER_COLLECTION_NAME, otherCollectionCount);

    // Start a third sync to test that only the new records are synced via incremental CDC
    final List<AirbyteMessage> messages3 = runRead(configuredCatalog, Jsons.jsonNode(List.of(lastStateMessage2)));
    final List<AirbyteRecordMessage> recordMessages3 = filterRecords(messages3);
    final List<AirbyteStateMessage> stateMessages3 = filterStateMessages(messages3);

    assertEquals(otherCollectionCount, recordMessages3.size());
    assertEquals(0, recordMessages3.stream().map(r -> new StreamDescriptor().withName(r.getStream()).withNamespace(r.getNamespace()))
        .filter(createRecordStreamFilter(COLLECTION_NAME, DATABASE_NAME)).count());
    assertEquals(otherCollectionCount,
        recordMessages3.stream().map(r -> new StreamDescriptor().withName(r.getStream()).withNamespace(r.getNamespace()))
            .filter(createRecordStreamFilter(OTHER_COLLECTION_NAME, DATABASE_NAME)).count());
    assertEquals(1, stateMessages3.size());
    validateStateMessages(stateMessages3);

    final AirbyteStateMessage lastStateMessage3 = Iterables.getLast(stateMessages3);
    assertNotNull(lastStateMessage3.getGlobal().getSharedState());
    assertFalse(lastStateMessage3.getGlobal().getSharedState().isEmpty());
    assertEquals(InitialSnapshotStatus.COMPLETE, Jsons.object(lastStateMessage3.getGlobal().getStreamStates().stream()
        .filter(createStateStreamFilter(COLLECTION_NAME, DATABASE_NAME)).findFirst().get().getStreamState(), MongoDbStreamState.class).status());
    assertEquals(InitialSnapshotStatus.COMPLETE, Jsons.object(lastStateMessage3.getGlobal().getStreamStates().stream()
        .filter(createStateStreamFilter(OTHER_COLLECTION_NAME, DATABASE_NAME)).findFirst().get().getStreamState(), MongoDbStreamState.class)
        .status());
  }

  @Test
  void syncShouldHandlePurgedLogsGracefully() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalog();

    // Run the sync to establish the next resume token value
    final List<AirbyteMessage> messages = runRead(configuredCatalog);
    final List<AirbyteRecordMessage> recordMessages = filterRecords(messages);
    final List<AirbyteStateMessage> stateMessages = filterStateMessages(messages);

    assertEquals(recordCount, recordMessages.size());
    assertEquals(recordCount + 1, stateMessages.size());

    // Modify the state to point to a non-existing resume token value
    final AirbyteStateMessage stateMessage = Iterables.getLast(stateMessages);
    final MongoDbCdcState cdcState = new MongoDbCdcState(
        MongoDbDebeziumStateUtil.formatState(DATABASE_NAME,
            config.get(REPLICA_SET_CONFIGURATION_KEY).asText(), "820000000000000000000000296E04"));
    stateMessage.getGlobal().setSharedState(Jsons.jsonNode(cdcState));
    final JsonNode state = Jsons.jsonNode(List.of(stateMessage));
    System.out.println(state);

    // Re-run the sync to prove that an initial snapshot is initiated due to invalid resume token
    final List<AirbyteMessage> messages2 = runRead(configuredCatalog, state);

    final List<AirbyteRecordMessage> recordMessages2 = filterRecords(messages2);
    final List<AirbyteStateMessage> stateMessages2 = filterStateMessages(messages2);

    assertEquals(recordCount, recordMessages2.size());
    assertEquals(recordCount + 1, stateMessages2.size());
  }

  @Test
  void testReachedTargetPosition() {
    final Long eventTimestamp = Long.MAX_VALUE;
    final Integer order = 0;
    final MongoDbCdcTargetPosition targetPosition = MongoDbCdcTargetPosition.targetPosition(mongoClient);
    final ChangeEventWithMetadata changeEventWithMetadata = mock(ChangeEventWithMetadata.class);

    when(changeEventWithMetadata.isSnapshotEvent()).thenReturn(true);

    assertFalse(targetPosition.reachedTargetPosition(changeEventWithMetadata));

    when(changeEventWithMetadata.isSnapshotEvent()).thenReturn(false);
    when(changeEventWithMetadata.snapshotMetadata()).thenReturn(SnapshotMetadata.LAST);

    assertTrue(targetPosition.reachedTargetPosition(changeEventWithMetadata));

    when(changeEventWithMetadata.snapshotMetadata()).thenReturn(SnapshotMetadata.FIRST);
    when(changeEventWithMetadata.eventValueAsJson()).thenReturn(Jsons.jsonNode(
        Map.of("source", Map.of("ts_ms", eventTimestamp, "ord", order))));

    assertTrue(targetPosition.reachedTargetPosition(changeEventWithMetadata));

    assertTrue(targetPosition.reachedTargetPosition(new BsonTimestamp(eventTimestamp)));
    assertFalse(targetPosition.reachedTargetPosition(new BsonTimestamp(0L)));
    assertFalse(targetPosition.reachedTargetPosition((BsonTimestamp) null));
  }

  private ConfiguredAirbyteStream convertToConfiguredAirbyteStream(final AirbyteStream airbyteStream, final SyncMode syncMode) {
    return new ConfiguredAirbyteStream()
        .withSyncMode(syncMode)
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
        .withCursorField(List.of(DEFAULT_CURSOR_FIELD))
        .withStream(airbyteStream);
  }

  private void verifyFieldNotExist(final List<AirbyteRecordMessage> records, final String stream, final String field) {
    assertTrue(records.stream()
        .filter(r -> r.getStream().equals(stream) && r.getData().get(field) != null)
        .collect(Collectors.toList())
        .isEmpty(), "Records contain unselected columns [%s:%s]".formatted(stream, field));
  }

  private List<AirbyteStateMessage> filterStateMessages(final List<AirbyteMessage> messages) {
    return messages.stream().filter(r -> r.getType() == AirbyteMessage.Type.STATE).map(AirbyteMessage::getState)
        .collect(Collectors.toList());
  }

  private void insertData(final String databaseName, final String collectionName, final int numberOfDocuments) {
    mongoClient.getDatabase(databaseName).getCollection(collectionName).drop();
    mongoClient.getDatabase(databaseName).createCollection(collectionName);
    final MongoCollection<Document> collection = mongoClient.getDatabase(databaseName).getCollection(collectionName);
    collection
        .insertMany(IntStream.range(0, numberOfDocuments).boxed().map(this::createDocument).toList());
  }

  private Document createDocument(final Integer i) {
    return new Document(NAME_FIELD, "value" + i).append(INT_TEST_FIELD, i);
  }

  private void validateStateMessages(final List<AirbyteStateMessage> stateMessages) {
    stateMessages.forEach(stateMessage -> {
      assertEquals(AirbyteStateMessage.AirbyteStateType.GLOBAL, stateMessage.getType());
      final AirbyteGlobalState global = stateMessage.getGlobal();
      assertNotNull(global.getSharedState());
      assertFalse(global.getSharedState().isEmpty());
    });
  }

  private Predicate<AirbyteStreamState> createStateStreamFilter(final String name, final String namespace) {
    return s -> s.getStreamDescriptor().equals(new StreamDescriptor().withName(name).withNamespace(namespace));
  }

  private Predicate<StreamDescriptor> createRecordStreamFilter(final String name, final String namespace) {
    return s -> s.equals(new StreamDescriptor().withName(name).withNamespace(namespace));
  }

}
