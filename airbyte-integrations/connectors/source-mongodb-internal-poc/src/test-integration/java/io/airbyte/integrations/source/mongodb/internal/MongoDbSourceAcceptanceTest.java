/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal;

import static io.airbyte.integrations.source.mongodb.internal.MongoConstants.DATABASE_CONFIGURATION_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Lists;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCollection;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import org.bson.BsonArray;
import org.bson.BsonString;
import org.bson.Document;

public class MongoDbSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String DATABASE_NAME = "test";
  private static final String COLLECTION_NAME = "acceptance_test1";
  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");

  private JsonNode config;
  private MongoClient mongoClient;

  @Override
  protected void setupEnvironment(final TestDestinationEnv testEnv) throws IOException {
    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a MongoDB credentials file. By default {module-root}/" + CREDENTIALS_PATH
              + ". Override by setting setting path with the CREDENTIALS_PATH constant.");
    }

    config = Jsons.deserialize(Files.readString(CREDENTIALS_PATH));
    ((ObjectNode) config).put(DATABASE_CONFIGURATION_KEY, DATABASE_NAME);

    mongoClient = MongoConnectionUtils.createMongoClient(config);

    insertTestData(mongoClient);
  }

  private void insertTestData(final MongoClient mongoClient) {
    mongoClient.getDatabase(DATABASE_NAME).createCollection(COLLECTION_NAME);
    final MongoCollection<Document> collection = mongoClient.getDatabase(DATABASE_NAME).getCollection(COLLECTION_NAME);
    final var objectDocument = new Document("testObject", new Document("name", "subName").append("testField1", "testField1").append("testInt", 10)
        .append("thirdLevelDocument", new Document("data", "someData").append("intData", 1)));
    final var doc1 = new Document("id", "0001").append("name", "Test1")
        .append("test", "test_value1").append("test_array", new BsonArray(List.of(new BsonString("test"), new BsonString("mongo1"))))
        .append("double_test", 100.11).append("int_test", 100).append("object_test", objectDocument);
    final var doc2 = new Document("id", "0002").append("name", "Test2")
        .append("test", "test_value2").append("test_array", new BsonArray(List.of(new BsonString("test"), new BsonString("mongo2"))))
        .append("double_test", 200.12).append("int_test", 200).append("object_test", objectDocument);
    final var doc3 = new Document("id", "0003").append("name", "Test3")
        .append("test", "test_value3").append("test_array", new BsonArray(List.of(new BsonString("test"), new BsonString("mongo3"))))
        .append("double_test", 300.13).append("int_test", 300).append("object_test", objectDocument);

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
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("_id"))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withCursorField(List.of("_id"))
            .withStream(CatalogHelpers.createAirbyteStream(
                DATABASE_NAME + "." + COLLECTION_NAME,
                Field.of("_id", JsonSchemaType.STRING),
                Field.of("id", JsonSchemaType.STRING),
                Field.of("name", JsonSchemaType.STRING),
                Field.of("test", JsonSchemaType.STRING),
                Field.of("test_array", JsonSchemaType.ARRAY),
                Field.of("empty_test", JsonSchemaType.STRING),
                Field.of("double_test", JsonSchemaType.NUMBER),
                Field.of("int_test", JsonSchemaType.NUMBER),
                Field.of("object_test", JsonSchemaType.OBJECT))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.INCREMENTAL))
                .withDefaultCursorField(List.of("_id")))));
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

}
