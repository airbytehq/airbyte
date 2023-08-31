/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal;

import static io.airbyte.integrations.source.mongodb.internal.MongoCatalogHelper.DEFAULT_CURSOR_FIELD;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.DATABASE_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.IS_TEST_CONFIGURATION_KEY;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCollection;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import java.util.stream.Collectors;
import org.bson.BsonArray;
import org.bson.BsonString;
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
  private static final String TEST_FIELD = "test";
  private static final String TEST_ARRAY_FIELD = "test_array";

  protected JsonNode config;
  protected MongoClient mongoClient;

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

    mongoClient = MongoConnectionUtils.createMongoClient(config);

    insertTestData(mongoClient);
  }

  private void insertTestData(final MongoClient mongoClient) {
    mongoClient.getDatabase(DATABASE_NAME).createCollection(COLLECTION_NAME);
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

    collection.insertMany(List.of(doc1, doc2, doc3));
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    mongoClient.getDatabase(DATABASE_NAME).getCollection(COLLECTION_NAME).drop();
    mongoClient.close();
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

    return new ConfiguredAirbyteCatalog().withStreams(List.of(configuredIncrementalAirbyteStream));
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

}
