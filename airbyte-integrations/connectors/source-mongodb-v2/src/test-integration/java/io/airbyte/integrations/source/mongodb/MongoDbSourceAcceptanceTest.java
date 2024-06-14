/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static io.airbyte.integrations.source.mongodb.MongoConstants.DATABASE_CONFIG_CONFIGURATION_KEY;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Iterables;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.model.Updates;
import io.airbyte.cdk.integrations.debezium.internals.ChangeEventWithMetadata;
import io.airbyte.cdk.integrations.debezium.internals.SnapshotMetadata;
import io.airbyte.cdk.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcState;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcTargetPosition;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumStateUtil;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbResumeTokenHelper;
import io.airbyte.integrations.source.mongodb.state.InitialSnapshotStatus;
import io.airbyte.integrations.source.mongodb.state.MongoDbStreamState;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.AirbyteTraceMessage;
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
import java.util.Optional;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import org.apache.commons.lang3.RandomStringUtils;
import org.bson.BsonArray;
import org.bson.BsonDocument;
import org.bson.BsonObjectId;
import org.bson.BsonString;
import org.bson.BsonTimestamp;
import org.bson.BsonValue;
import org.bson.Document;
import org.bson.types.ObjectId;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class MongoDbSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");
  public static final String DOCUMENT_ID_FIELD = "_id";
  private static final String DOUBLE_TEST_FIELD = "double_test";
  private static final String EMPTY_TEST_FIELD = "empty_test";
  private static final String ID_FIELD = "id";
  private static final String INT_TEST_FIELD = "int_test";
  private static final String INVALID_RESUME_TOKEN = "820000000000000000000000296E04";
  private static final String NAME_FIELD = "name";
  private static final String OBJECT_TEST_FIELD = "object_test";
  private static final String TEST_FIELD = "test";
  private static final String TEST_ARRAY_FIELD = "test_array";
  private static final ObjectId OBJECT_ID1 = new ObjectId("64c0029d95ad260d69ef28a0");
  private static final ObjectId OBJECT_ID2 = new ObjectId("64c0029d95ad260d69ef28a1");
  private static final ObjectId OBJECT_ID3 = new ObjectId("64c0029d95ad260d69ef28a2");

  private JsonNode config;
  private String collectionName;
  private String databaseName;
  private MongoClient mongoClient;
  private String otherCollection1Name;
  private String otherCollection2Name;
  private int recordCount = 0;

  @Override
  protected void setupEnvironment(final TestDestinationEnv testEnv) throws Exception {
    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a MongoDB credentials file. By default {module-root}/" + CREDENTIALS_PATH
              + ". Override by setting setting path with the CREDENTIALS_PATH constant.");
    }

    // Randomly generate the names to avoid collisions with other tests
    collectionName = "collection_" + RandomStringUtils.randomAlphabetic(8);
    databaseName = "acceptance_test_" + RandomStringUtils.randomAlphabetic(8);
    otherCollection1Name = "collection_" + RandomStringUtils.randomAlphabetic(8);
    otherCollection2Name = "collection_" + RandomStringUtils.randomAlphabetic(8);

    config = Jsons.deserialize(Files.readString(CREDENTIALS_PATH));
    final ObjectNode databaseConfig = (ObjectNode) config.get(DATABASE_CONFIG_CONFIGURATION_KEY);
    databaseConfig.put(MongoConstants.DATABASE_CONFIGURATION_KEY, databaseName);
    databaseConfig.put(MongoConstants.IS_TEST_CONFIGURATION_KEY, true);
    databaseConfig.put(MongoConstants.CHECKPOINT_INTERVAL_CONFIGURATION_KEY, 1);
    ((ObjectNode) config).put(DATABASE_CONFIG_CONFIGURATION_KEY, databaseConfig);

    final MongoDbSourceConfig sourceConfig = new MongoDbSourceConfig(config);

    mongoClient = MongoConnectionUtils.createMongoClient(sourceConfig);
    createTestCollections(mongoClient);
    insertTestData(mongoClient);
  }

  private void createTestCollections(final MongoClient mongoClient) {
    mongoClient.getDatabase(databaseName).getCollection(collectionName).drop();
    mongoClient.getDatabase(databaseName).getCollection(otherCollection1Name).drop();
    mongoClient.getDatabase(databaseName).getCollection(otherCollection2Name).drop();
    mongoClient.getDatabase(databaseName).createCollection(collectionName);
    mongoClient.getDatabase(databaseName).createCollection(otherCollection1Name);
    mongoClient.getDatabase(databaseName).createCollection(otherCollection2Name);
  }

  private void insertTestData(final MongoClient mongoClient) {
    final MongoCollection<Document> collection = mongoClient.getDatabase(databaseName).getCollection(collectionName);
    final var objectDocument =
        new Document("testObject", new Document(NAME_FIELD, "subName").append("testField1", "testField1").append(INT_TEST_FIELD, 10)
            .append("thirdLevelDocument", new Document("data", "someData").append("intData", 1)));

    final var doc1 = new Document(DOCUMENT_ID_FIELD, OBJECT_ID1)
        .append(ID_FIELD, "0001").append(NAME_FIELD, "Test")
        .append(TEST_FIELD, 10).append(TEST_ARRAY_FIELD, new BsonArray(List.of(new BsonString("test"), new BsonString("mongo"))))
        .append(DOUBLE_TEST_FIELD, 100.12).append(INT_TEST_FIELD, 100).append(OBJECT_TEST_FIELD, objectDocument);

    final var doc2 = new Document(DOCUMENT_ID_FIELD, OBJECT_ID2)
        .append(ID_FIELD, "0002").append(NAME_FIELD, "Mongo").append(TEST_FIELD, "test_value").append(INT_TEST_FIELD, 201)
        .append(OBJECT_TEST_FIELD, objectDocument);

    final var doc3 = new Document(DOCUMENT_ID_FIELD, OBJECT_ID3)
        .append(ID_FIELD, "0003").append(NAME_FIELD, "Source").append(TEST_FIELD, null)
        .append(DOUBLE_TEST_FIELD, 212.11).append(INT_TEST_FIELD, 302).append(OBJECT_TEST_FIELD, objectDocument);

    final List<Document> newDocuments = List.of(doc1, doc2, doc3);
    recordCount += newDocuments.size();
    collection.insertMany(newDocuments);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    mongoClient.getDatabase(databaseName).getCollection(collectionName).drop();
    mongoClient.getDatabase(databaseName).getCollection(otherCollection1Name).drop();
    mongoClient.getDatabase(databaseName).getCollection(otherCollection2Name).drop();
    mongoClient.getDatabase(databaseName).drop();
    mongoClient.close();
    recordCount = 0;
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-mongodb-v2:dev";
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
        Field.of(DOCUMENT_ID_FIELD, JsonSchemaType.STRING),
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
    final AirbyteStream airbyteStream = MongoCatalogHelper.buildAirbyteStream(collectionName, databaseName, enabledFields);
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
    verifyFieldNotExist(records, collectionName, DOUBLE_TEST_FIELD);
    verifyFieldNotExist(records, collectionName, EMPTY_TEST_FIELD);
    verifyFieldNotExist(records, collectionName, ID_FIELD);
    verifyFieldNotExist(records, collectionName, INT_TEST_FIELD);
    verifyFieldNotExist(records, collectionName, OBJECT_TEST_FIELD);
    verifyFieldNotExist(records, collectionName, TEST_FIELD);
    verifyFieldNotExist(records, collectionName, TEST_ARRAY_FIELD);
  }

  @Test
  void testSyncEmptyCollection() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalog();
    final AirbyteStream otherAirbyteStream = MongoCatalogHelper.buildAirbyteStream(otherCollection1Name, databaseName,
        List.of(Field.of(NAME_FIELD, JsonSchemaType.STRING), Field.of(INT_TEST_FIELD, JsonSchemaType.NUMBER)));
    configuredCatalog.withStreams(List.of(convertToConfiguredAirbyteStream(otherAirbyteStream, SyncMode.INCREMENTAL)));

    final List<AirbyteMessage> messages = runRead(configuredCatalog);
    final List<AirbyteRecordMessage> recordMessages = filterRecords(messages);
    final List<AirbyteStateMessage> stateMessages = filterStateMessages(messages);

    assertEquals(0, recordMessages.size());
    // Expect 1 state message from initial load and 1 from incremental load.
    assertEquals(2, stateMessages.size());

    final AirbyteStateMessage lastStateMessage = Iterables.getLast(stateMessages);
    assertNotNull(lastStateMessage.getGlobal().getSharedState());
    assertFalse(lastStateMessage.getGlobal().getSharedState().isEmpty());
    assertTrue(lastStateMessage.getGlobal().getStreamStates().isEmpty());
  }

  @Test
  void testNewStreamAddedToExistingCDCSync() throws Exception {
    /*
     * Insert the data into the second stream that will be added before the second sync. Do this before
     * the first sync to ensure that the resume token stored in the state at the end of the first sync
     * accounts for this data. If not, we will get duplicate records from the second sync: one batch
     * from the initial snapshot for the second stream and one batch from Debezium via the change event
     * stream. This is a known issue that happens when a stream with data inserted/changed AFTER the
     * first stream is added to the connection and is currently handled by de-duping during
     * normalization, so we will not test that case here.
     */
    final int otherCollectionCount = 100;
    insertData(databaseName, otherCollection1Name, otherCollectionCount);

    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalog();

    // Start a sync with one stream
    final List<AirbyteMessage> messages = runRead(configuredCatalog);
    final List<AirbyteRecordMessage> recordMessages = filterRecords(messages);
    final List<AirbyteStateMessage> stateMessages = filterStateMessages(messages);

    assertEquals(recordCount, recordMessages.size());
    assertEquals(recordCount + 1, stateMessages.size());

    final AirbyteStateMessage lastStateMessage = Iterables.getLast(stateMessages);
    validateStateMessages(stateMessages);
    validateAllStreamsComplete(stateMessages, List.of(
        new StreamDescriptor().withName(collectionName).withNamespace(databaseName)));
    assertFalse(lastStateMessage.getGlobal().getStreamStates().stream().anyMatch(
        createStateStreamFilter(new StreamDescriptor().withName(otherCollection1Name).withNamespace(databaseName))));

    final List<Field> fields = List.of(
        Field.of(NAME_FIELD, JsonSchemaType.STRING),
        Field.of(INT_TEST_FIELD, JsonSchemaType.NUMBER));
    addStreamToConfiguredCatalog(configuredCatalog, databaseName, otherCollection1Name, fields);

    // Start another sync with a newly added stream
    final List<AirbyteMessage> messages2 = runRead(configuredCatalog, Jsons.jsonNode(List.of(lastStateMessage)));
    final List<AirbyteRecordMessage> recordMessages2 = filterRecords(messages2);
    final List<AirbyteStateMessage> stateMessages2 = filterStateMessages(messages2);

    assertEquals(otherCollectionCount, recordMessages2.size());
    assertEquals(otherCollectionCount + 1, stateMessages2.size());

    validateStateMessages(stateMessages2);
    validateAllStreamsComplete(stateMessages2, List.of(
        new StreamDescriptor().withName(collectionName).withNamespace(databaseName),
        new StreamDescriptor().withName(otherCollection1Name).withNamespace(databaseName)));
  }

  @Test
  void testNoChangeForCDCIncrementalSync() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalog();

    // Start a sync with one stream
    final List<AirbyteMessage> messages = runRead(configuredCatalog);
    final List<AirbyteRecordMessage> recordMessages = filterRecords(messages);
    final List<AirbyteStateMessage> stateMessages = filterStateMessages(messages);

    assertEquals(recordCount, recordMessages.size());
    assertEquals(recordCount + 1, stateMessages.size());

    final AirbyteStateMessage lastStateMessage = Iterables.getLast(stateMessages);
    validateStateMessages(stateMessages);
    validateAllStreamsComplete(stateMessages, List.of(
        new StreamDescriptor().withName(collectionName).withNamespace(databaseName)));

    // Start another sync with no changes
    final List<AirbyteMessage> messages2 = runRead(configuredCatalog, Jsons.jsonNode(List.of(lastStateMessage)));
    final List<AirbyteRecordMessage> recordMessages2 = filterRecords(messages2);
    final List<AirbyteStateMessage> stateMessages2 = filterStateMessages(messages2);

    assertEquals(0, recordMessages2.size());
    assertEquals(1, stateMessages2.size());

    validateStateMessages(stateMessages2);
    validateAllStreamsComplete(stateMessages2, List.of(
        new StreamDescriptor().withName(collectionName).withNamespace(databaseName)));
  }

  @Test
  void testInsertUpdateDeleteIncrementalSync() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalog();

    // Start a sync with one stream
    final List<AirbyteMessage> messages = runRead(configuredCatalog);
    final List<AirbyteRecordMessage> recordMessages = filterRecords(messages);
    final List<AirbyteStateMessage> stateMessages = filterStateMessages(messages);

    assertEquals(recordCount, recordMessages.size());
    assertEquals(recordCount + 1, stateMessages.size());

    validateCdcEventRecordData(recordMessages.get(0), new BsonObjectId(OBJECT_ID1), false);
    validateCdcEventRecordData(recordMessages.get(1), new BsonObjectId(OBJECT_ID2), false);
    validateCdcEventRecordData(recordMessages.get(2), new BsonObjectId(OBJECT_ID3), false);

    final AirbyteStateMessage lastStateMessage = Iterables.getLast(stateMessages);
    validateStateMessages(stateMessages);
    validateAllStreamsComplete(stateMessages, List.of(
        new StreamDescriptor().withName(collectionName).withNamespace(databaseName)));

    final var result = mongoClient.getDatabase(databaseName).getCollection(collectionName).insertOne(createDocument(1));
    final var insertedId = result.getInsertedId();

    // Start another sync that finds the insert change
    final List<AirbyteMessage> messages2 = runRead(configuredCatalog, Jsons.jsonNode(List.of(lastStateMessage)));
    final List<AirbyteRecordMessage> recordMessages2 = filterRecords(messages2);
    final List<AirbyteStateMessage> stateMessages2 = filterStateMessages(messages2);

    assertEquals(1, recordMessages2.size());
    assertEquals(1, stateMessages2.size());

    validateCdcEventRecordData(recordMessages2.get(0), insertedId, false);

    final AirbyteStateMessage lastStateMessage2 = Iterables.getLast(stateMessages2);
    validateStateMessages(stateMessages2);
    validateAllStreamsComplete(stateMessages2, List.of(
        new StreamDescriptor().withName(collectionName).withNamespace(databaseName)));

    final var idFilter = new Document(DOCUMENT_ID_FIELD, insertedId);
    mongoClient.getDatabase(databaseName).getCollection(collectionName).updateOne(idFilter, Updates.combine(Updates.set("newField", "new")));

    // Start another sync that finds the update change
    final List<AirbyteMessage> messages3 = runRead(configuredCatalog, Jsons.jsonNode(List.of(lastStateMessage2)));
    final List<AirbyteRecordMessage> recordMessages3 = filterRecords(messages3);
    final List<AirbyteStateMessage> stateMessages3 = filterStateMessages(messages3);

    assertEquals(1, recordMessages3.size());
    assertEquals(1, stateMessages3.size());

    validateCdcEventRecordData(recordMessages3.get(0), insertedId, false);

    final AirbyteStateMessage lastStateMessage3 = Iterables.getLast(stateMessages3);
    validateStateMessages(stateMessages3);
    validateAllStreamsComplete(stateMessages3, List.of(
        new StreamDescriptor().withName(collectionName).withNamespace(databaseName)));

    mongoClient.getDatabase(databaseName).getCollection(collectionName).deleteOne(idFilter);

    // Start another sync that finds the delete change
    final List<AirbyteMessage> messages4 = runRead(configuredCatalog, Jsons.jsonNode(List.of(lastStateMessage3)));
    final List<AirbyteRecordMessage> recordMessages4 = filterRecords(messages4);
    final List<AirbyteStateMessage> stateMessages4 = filterStateMessages(messages4);

    assertEquals(1, recordMessages4.size());
    assertEquals(1, stateMessages4.size());

    validateCdcEventRecordData(recordMessages4.get(0), insertedId, true);

    validateStateMessages(stateMessages4);
    validateAllStreamsComplete(stateMessages3, List.of(
        new StreamDescriptor().withName(collectionName).withNamespace(databaseName)));

  }

  @Test
  void testCDCStreamCheckpointingWithMultipleStreams() throws Exception {
    final int otherCollection1Count = 100;
    insertData(databaseName, otherCollection1Name, otherCollection1Count);
    final int otherCollection2Count = 1;
    insertData(databaseName, otherCollection2Name, otherCollection2Count);

    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalog();
    final List<ConfiguredAirbyteStream> streams = configuredCatalog.getStreams();
    final AirbyteStream otherAirbyteStream1 = MongoCatalogHelper.buildAirbyteStream(otherCollection1Name, databaseName,
        List.of(Field.of(NAME_FIELD, JsonSchemaType.STRING), Field.of(INT_TEST_FIELD, JsonSchemaType.NUMBER)));
    final AirbyteStream otherAirbyteStream2 = MongoCatalogHelper.buildAirbyteStream(otherCollection2Name, databaseName,
        List.of(Field.of(NAME_FIELD, JsonSchemaType.STRING), Field.of(INT_TEST_FIELD, JsonSchemaType.NUMBER)));
    streams.add(convertToConfiguredAirbyteStream(otherAirbyteStream1, SyncMode.INCREMENTAL));
    streams.add(convertToConfiguredAirbyteStream(otherAirbyteStream2, SyncMode.INCREMENTAL));
    configuredCatalog.withStreams(streams);

    // Start a sync with three streams
    final List<AirbyteMessage> messages = runRead(configuredCatalog);
    final List<AirbyteRecordMessage> recordMessages = filterRecords(messages);
    final List<AirbyteStateMessage> stateMessages = filterStateMessages(messages);

    assertEquals(recordCount + otherCollection1Count + otherCollection2Count, recordMessages.size());
    assertEquals(recordCount + otherCollection1Count + otherCollection2Count + 1, stateMessages.size());

    validateStateMessages(stateMessages);
    validateAllStreamsComplete(stateMessages, List.of(
        new StreamDescriptor().withName(collectionName).withNamespace(databaseName),
        new StreamDescriptor().withName(otherCollection1Name).withNamespace(databaseName),
        new StreamDescriptor().withName(otherCollection2Name).withNamespace(databaseName)));

    // Start a second sync from somewhere in the middle of stream 2
    final List<AirbyteMessage> messages2 = runRead(configuredCatalog, Jsons.jsonNode(List.of(stateMessages.get(recordCount + 50))));
    final List<AirbyteRecordMessage> recordMessages2 = filterRecords(messages2);
    final List<AirbyteStateMessage> stateMessages2 = filterStateMessages(messages2);

    assertEquals(50, recordMessages2.size());
    assertEquals(51, stateMessages2.size());

    // get state message where stream 1 has completed, stream 2 is in progress, and stream 3 has not
    // started
    final AirbyteStateMessage airbyteStateMessage = stateMessages2.get(0);

    final Optional<AirbyteStreamState> collectionStreamState = getStreamState(airbyteStateMessage,
        new StreamDescriptor().withName(collectionName).withNamespace(databaseName));
    assertEquals(InitialSnapshotStatus.COMPLETE, Jsons.object(collectionStreamState.get().getStreamState(), MongoDbStreamState.class).status());

    final Optional<AirbyteStreamState> otherCollection1StreamState = getStreamState(airbyteStateMessage,
        new StreamDescriptor().withName(otherCollection1Name).withNamespace(databaseName));
    assertTrue(otherCollection1StreamState.isPresent());
    assertEquals(InitialSnapshotStatus.IN_PROGRESS,
        Jsons.object(otherCollection1StreamState.get().getStreamState(), MongoDbStreamState.class).status());

    final Optional<AirbyteStreamState> otherCollection2StreamState = getStreamState(airbyteStateMessage,
        new StreamDescriptor().withName(otherCollection2Name).withNamespace(databaseName));
    assertTrue(otherCollection2StreamState.isEmpty());

    validateStateMessages(stateMessages2);
    validateAllStreamsComplete(stateMessages, List.of(
        new StreamDescriptor().withName(collectionName).withNamespace(databaseName),
        new StreamDescriptor().withName(otherCollection1Name).withNamespace(databaseName),
        new StreamDescriptor().withName(otherCollection2Name).withNamespace(databaseName)));

    // Insert more data for one stream
    insertData(databaseName, otherCollection1Name, otherCollection1Count);

    // Start a third sync to test that only the new records are synced via incremental CDC
    final List<AirbyteMessage> messages3 = runRead(configuredCatalog, Jsons.jsonNode(List.of(Iterables.getLast(stateMessages2))));
    final List<AirbyteRecordMessage> recordMessages3 = filterRecords(messages3);
    final List<AirbyteStateMessage> stateMessages3 = filterStateMessages(messages3);

    assertEquals(otherCollection1Count, recordMessages3.size());
    assertEquals(0, recordMessages3.stream().map(r -> new StreamDescriptor().withName(r.getStream()).withNamespace(r.getNamespace()))
        .filter(createRecordStreamFilter(collectionName, databaseName)).count());
    assertEquals(0, recordMessages3.stream().map(r -> new StreamDescriptor().withName(r.getStream()).withNamespace(r.getNamespace()))
        .filter(createRecordStreamFilter(otherCollection2Name, databaseName)).count());
    assertEquals(otherCollection1Count,
        recordMessages3.stream().map(r -> new StreamDescriptor().withName(r.getStream()).withNamespace(r.getNamespace()))
            .filter(createRecordStreamFilter(otherCollection1Name, databaseName)).count());
    assertEquals(1, stateMessages3.size());
    validateStateMessages(stateMessages3);
    validateAllStreamsComplete(stateMessages, List.of(
        new StreamDescriptor().withName(collectionName).withNamespace(databaseName),
        new StreamDescriptor().withName(otherCollection1Name).withNamespace(databaseName),
        new StreamDescriptor().withName(otherCollection2Name).withNamespace(databaseName)));
  }

  @Test
  void testSyncShouldHandlePurgedLogsGracefully() throws Exception {
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
        MongoDbDebeziumStateUtil.formatState(databaseName, INVALID_RESUME_TOKEN));
    stateMessage.getGlobal().setSharedState(Jsons.jsonNode(cdcState));
    final JsonNode state = Jsons.jsonNode(List.of(stateMessage));

    // Re-run the sync to prove that a config error is thrown due to invalid resume token
    List<AirbyteMessage> messages1 = runRead(configuredCatalog, state);
    List<AirbyteMessage> records = messages1.stream().filter(r -> r.getType() == Type.RECORD).toList();
    // In this sync, there should be no records expected - only error trace messages indicating that the
    // offset is not valid.
    assertEquals(0, records.size());
    List<AirbyteMessage> traceMessages = messages1.stream().filter(r -> r.getType() == Type.TRACE).toList();
    assertOplogErrorTracePresent(traceMessages);
  }

  @Test
  void testReachedTargetPosition() {
    final long eventTimestamp = Long.MAX_VALUE;
    final Integer order = 0;
    final MongoDbCdcTargetPosition targetPosition =
        new MongoDbCdcTargetPosition(MongoDbResumeTokenHelper.getMostRecentResumeToken(mongoClient, databaseName, getConfiguredCatalog()));
    final ChangeEventWithMetadata changeEventWithMetadata = mock(ChangeEventWithMetadata.class);

    when(changeEventWithMetadata.isSnapshotEvent()).thenReturn(true);

    assertFalse(targetPosition.reachedTargetPosition(changeEventWithMetadata));

    when(changeEventWithMetadata.isSnapshotEvent()).thenReturn(false);
    when(changeEventWithMetadata.snapshotMetadata()).thenReturn(SnapshotMetadata.LAST);

    assertTrue(targetPosition.reachedTargetPosition(changeEventWithMetadata));

    when(changeEventWithMetadata.snapshotMetadata()).thenReturn(SnapshotMetadata.FIRST);
    when(changeEventWithMetadata.eventValueAsJson()).thenReturn(Jsons.jsonNode(
        Map.of(MongoDbDebeziumConstants.ChangeEvent.SOURCE,
            Map.of(MongoDbDebeziumConstants.ChangeEvent.SOURCE_TIMESTAMP_MS, eventTimestamp,
                MongoDbDebeziumConstants.ChangeEvent.SOURCE_ORDER, order))));

    assertTrue(targetPosition.reachedTargetPosition(changeEventWithMetadata));

    assertTrue(targetPosition.reachedTargetPosition(new BsonTimestamp(eventTimestamp)));
    assertFalse(targetPosition.reachedTargetPosition(new BsonTimestamp(0L)));
    assertFalse(targetPosition.reachedTargetPosition((BsonTimestamp) null));
  }

  @Test
  void testIsSameOffset() {
    final MongoDbCdcTargetPosition targetPosition =
        new MongoDbCdcTargetPosition(MongoDbResumeTokenHelper.getMostRecentResumeToken(mongoClient, databaseName, getConfiguredCatalog()));
    final BsonDocument resumeToken = MongoDbResumeTokenHelper.getMostRecentResumeToken(mongoClient, databaseName, getConfiguredCatalog());
    final String resumeTokenString = resumeToken.get("_data").asString().getValue();
    final Map<String, String> emptyOffsetA = Map.of();
    final Map<String, String> emptyOffsetB = Map.of();
    final Map<String, String> offsetA = Jsons.object(MongoDbDebeziumStateUtil.formatState(databaseName,
        resumeTokenString), new TypeReference<>() {});
    final Map<String, String> offsetB = Jsons.object(MongoDbDebeziumStateUtil.formatState(databaseName,
        resumeTokenString), new TypeReference<>() {});
    final Map<String, String> offsetBDifferent = Jsons.object(MongoDbDebeziumStateUtil.formatState(databaseName,
        INVALID_RESUME_TOKEN), new TypeReference<>() {});

    assertFalse(targetPosition.isSameOffset(null, offsetB));
    assertFalse(targetPosition.isSameOffset(emptyOffsetA, offsetB));
    assertFalse(targetPosition.isSameOffset(offsetA, null));
    assertFalse(targetPosition.isSameOffset(offsetA, emptyOffsetB));
    assertFalse(targetPosition.isSameOffset(offsetA, offsetBDifferent));
    assertTrue(targetPosition.isSameOffset(offsetA, offsetB));
  }

  @Test
  void testStreamStatusTraces() throws Exception {
    final ConfiguredAirbyteCatalog configuredCatalog = getConfiguredCatalog();

    // Start a sync with one stream
    final List<AirbyteMessage> messages = runRead(configuredCatalog);
    final List<AirbyteRecordMessage> recordMessages = filterRecords(messages);
    final List<AirbyteStateMessage> stateMessages = filterStateMessages(messages);
    final List<AirbyteTraceMessage> statusTraceMessages = filterStatusTraceMessages(messages);

    assertEquals(recordCount, recordMessages.size());
    assertEquals(recordCount + 1, stateMessages.size());
    assertEquals(2, statusTraceMessages.size());

    final AirbyteStateMessage lastStateMessage = Iterables.getLast(stateMessages);

    final var result = mongoClient.getDatabase(databaseName).getCollection(collectionName).insertOne(createDocument(1));
    final var insertedId = result.getInsertedId();

    // Start another sync that finds the insert change
    final List<AirbyteMessage> messages2 = runRead(configuredCatalog, Jsons.jsonNode(List.of(lastStateMessage)));
    final List<AirbyteRecordMessage> recordMessages2 = filterRecords(messages2);
    final List<AirbyteStateMessage> stateMessages2 = filterStateMessages(messages2);
    final List<AirbyteTraceMessage> statusTraceMessages2 = filterStatusTraceMessages(messages2);

    assertEquals(1, recordMessages2.size());
    assertEquals(1, stateMessages2.size());
    assertEquals(2, statusTraceMessages2.size());
  }

  private ConfiguredAirbyteStream convertToConfiguredAirbyteStream(final AirbyteStream airbyteStream, final SyncMode syncMode) {
    return new ConfiguredAirbyteStream()
        .withSyncMode(syncMode)
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
        .withCursorField(List.of(MongoCatalogHelper.DEFAULT_CURSOR_FIELD))
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

  private List<AirbyteTraceMessage> filterStatusTraceMessages(final List<AirbyteMessage> messages) {
    return messages.stream().filter(m -> m.getType() == Type.TRACE &&
        m.getTrace().getType() == AirbyteTraceMessage.Type.STREAM_STATUS).map(AirbyteMessage::getTrace)
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

  private void validateAllStreamsComplete(final List<AirbyteStateMessage> stateMessages, final List<StreamDescriptor> completedStreams) {
    final AirbyteStateMessage lastStateMessage = Iterables.getLast(stateMessages);
    assertNotNull(lastStateMessage.getGlobal().getSharedState());
    assertFalse(lastStateMessage.getGlobal().getSharedState().isEmpty());
    completedStreams.forEach(s -> {
      assertTrue(lastStateMessage.getGlobal().getStreamStates().stream().anyMatch(createStateStreamFilter(s)));
      Assertions.assertEquals(InitialSnapshotStatus.COMPLETE,
          Jsons.object(getStreamState(lastStateMessage, s).get().getStreamState(), MongoDbStreamState.class).status());
    });
  }

  private Optional<AirbyteStreamState> getStreamState(final AirbyteStateMessage stateMessage, final StreamDescriptor streamDescriptor) {
    return stateMessage.getGlobal().getStreamStates().stream().filter(createStateStreamFilter(streamDescriptor)).findFirst();
  }

  private Predicate<AirbyteStreamState> createStateStreamFilter(final StreamDescriptor streamDescriptor) {
    return s -> s.getStreamDescriptor().equals(streamDescriptor);
  }

  private Predicate<StreamDescriptor> createRecordStreamFilter(final String name, final String namespace) {
    return s -> s.equals(new StreamDescriptor().withName(name).withNamespace(namespace));
  }

  private void addStreamToConfiguredCatalog(final ConfiguredAirbyteCatalog configuredAirbyteCatalog,
                                            final String databaseName,
                                            final String collectionName,
                                            final List<Field> fields) {
    final List<ConfiguredAirbyteStream> streams = configuredAirbyteCatalog.getStreams();
    final AirbyteStream otherAirbyteStream = MongoCatalogHelper.buildAirbyteStream(collectionName, databaseName, fields);
    streams.add(convertToConfiguredAirbyteStream(otherAirbyteStream, SyncMode.INCREMENTAL));
    configuredAirbyteCatalog.withStreams(streams);
  }

  private void validateCdcEventRecordData(final AirbyteRecordMessage airbyteRecordMessage, final BsonValue expectedObjectId, final boolean isDelete) {
    final Map<String, Object> data = Jsons.object(airbyteRecordMessage.getData(), new TypeReference<>() {});
    assertEquals(expectedObjectId.asObjectId().getValue().toString(), data.get(DOCUMENT_ID_FIELD));
    assertTrue(data.containsKey(CDC_DELETED_AT));
    assertTrue(data.containsKey(CDC_UPDATED_AT));
    if (isDelete) {
      assertNotNull(data.get(CDC_DELETED_AT));
    } else {
      assertNull(data.get(CDC_DELETED_AT));
    }
  }

  private void assertOplogErrorTracePresent(List<AirbyteMessage> traceMessages) {
    final boolean oplogTracePresent = traceMessages
        .stream()
        .anyMatch(trace -> trace.getTrace().getType().equals(AirbyteTraceMessage.Type.ERROR)
            && trace.getTrace().getError().getMessage().contains("Saved offset is not valid"));
    assertTrue(oplogTracePresent);
  }

}
