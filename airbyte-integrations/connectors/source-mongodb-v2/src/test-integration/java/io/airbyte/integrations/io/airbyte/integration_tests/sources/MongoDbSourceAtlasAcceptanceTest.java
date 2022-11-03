/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static io.airbyte.db.mongodb.MongoUtils.MongoInstanceType.ATLAS;
import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.assertj.core.api.AssertionsForClassTypes.catchThrowable;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.mongodb.client.MongoCollection;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.integrations.source.mongodb.MongoDbSource;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.bson.BsonArray;
import org.bson.BsonString;
import org.bson.Document;
import org.junit.jupiter.api.Test;

public class MongoDbSourceAtlasAcceptanceTest extends MongoDbSourceAbstractAcceptanceTest {

  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");

  protected static final List<Field> SUB_FIELDS = List.of(
      Field.of("testObject", JsonSchemaType.OBJECT, List.of(
          Field.of("name", JsonSchemaType.STRING),
          Field.of("testField1", JsonSchemaType.STRING),
          Field.of("testInt", JsonSchemaType.NUMBER),
          Field.of("thirdLevelDocument", JsonSchemaType.OBJECT, List.of(
              Field.of("data", JsonSchemaType.STRING),
              Field.of("intData", JsonSchemaType.NUMBER))))));

  protected static final List<Field> FIELDS = List.of(
      Field.of("id", JsonSchemaType.STRING),
      Field.of("_id", JsonSchemaType.STRING),
      Field.of("name", JsonSchemaType.STRING),
      Field.of("test_aibyte_transform", JsonSchemaType.STRING),
      Field.of("test_array", JsonSchemaType.ARRAY),
      Field.of("int_test", JsonSchemaType.NUMBER),
      Field.of("double_test", JsonSchemaType.NUMBER),
      Field.of("object_test", JsonSchemaType.OBJECT, SUB_FIELDS));

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a MongoDB credentials file. By default {module-root}/" + CREDENTIALS_PATH
              + ". Override by setting setting path with the CREDENTIALS_PATH constant.");
    }

    final String credentialsJsonString = Files.readString(CREDENTIALS_PATH);
    final JsonNode credentialsJson = Jsons.deserialize(credentialsJsonString);

    final JsonNode instanceConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("instance", ATLAS.getType())
        .put("cluster_url", credentialsJson.get("cluster_url").asText())
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("user", credentialsJson.get("user").asText())
        .put(JdbcUtils.PASSWORD_KEY, credentialsJson.get(JdbcUtils.PASSWORD_KEY).asText())
        .put("instance_type", instanceConfig)
        .put(JdbcUtils.DATABASE_KEY, DATABASE_NAME)
        .put("auth_source", "admin")
        .build());

    final String connectionString = String.format("mongodb+srv://%s:%s@%s/%s?authSource=admin&retryWrites=true&w=majority&tls=true",
        config.get("user").asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        config.get("instance_type").get("cluster_url").asText(),
        config.get(JdbcUtils.DATABASE_KEY).asText());

    database = new MongoDatabase(connectionString, DATABASE_NAME);

    final MongoCollection<Document> collection = database.createCollection(COLLECTION_NAME);
    final var objectDocument = new Document("testObject", new Document("name", "subName").append("testField1", "testField1").append("testInt", 10)
        .append("thirdLevelDocument", new Document("data", "someData").append("intData", 1)));
    final var doc1 = new Document("id", "0001").append("name", "Test")
        .append("test", 10).append("test_array", new BsonArray(List.of(new BsonString("test"), new BsonString("mongo"))))
        .append("double_test", 100.12).append("int_test", 100).append("object_test", objectDocument);
    final var doc2 =
        new Document("id", "0002").append("name", "Mongo").append("test", "test_value").append("int_test", 201).append("object_test", objectDocument);
    final var doc3 = new Document("id", "0003").append("name", "Source").append("test", null)
        .append("double_test", 212.11).append("int_test", 302).append("object_test", objectDocument);

    collection.insertMany(List.of(doc1, doc2, doc3));
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    database.getDatabase().getCollection(COLLECTION_NAME).drop();
    database.close();
  }

  @Override
  protected void verifyCatalog(final AirbyteCatalog catalog) {
    final List<AirbyteStream> streams = catalog.getStreams();
    // only one stream is expected; the schema that should be ignored
    // must not be included in the retrieved catalog
    assertEquals(1, streams.size());
    final AirbyteStream actualStream = streams.get(0);
    assertEquals(CatalogHelpers.fieldsToJsonSchema(FIELDS), actualStream.getJsonSchema());
  }

  @Test
  public void testCheckIncorrectUsername() throws Exception {
    ((ObjectNode) config).put("user", "fake");
    final Throwable throwable = catchThrowable(() -> new MongoDbSource().check(config));
    assertThat(throwable).isInstanceOf(ConfigErrorException.class);
    assertThat(((ConfigErrorException) throwable).getDisplayMessage()
        .contains("State code: 18"));
  }

  @Test
  public void testCheckIncorrectPassword() throws Exception {
    ((ObjectNode) config).put("password", "fake");
    final Throwable throwable = catchThrowable(() -> new MongoDbSource().check(config));
    assertThat(throwable).isInstanceOf(ConfigErrorException.class);
    assertThat(((ConfigErrorException) throwable).getDisplayMessage()
        .contains("State code: 18"));
  }

  @Test
  public void testCheckIncorrectCluster() throws Exception {
    ((ObjectNode) config).with("instance_type")
        .put("cluster_url", "cluster0.iqgf8.mongodb.netfail");
    final Throwable throwable = catchThrowable(() -> new MongoDbSource().check(config));
    assertThat(throwable).isInstanceOf(ConfigErrorException.class);
    assertThat(((ConfigErrorException) throwable).getDisplayMessage()
        .contains("State code: -4"));
  }

  @Test
  public void testCheckIncorrectAccessToDataBase() throws Exception {
    ((ObjectNode) config).put("user", "test_user_without_access")
        .put("password", "test12321");
    final Throwable throwable = catchThrowable(() -> new MongoDbSource().check(config));
    assertThat(throwable).isInstanceOf(ConfigErrorException.class);
    assertThat(((ConfigErrorException) throwable).getDisplayMessage()
        .contains("State code: 13"));
  }

}
