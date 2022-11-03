/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static io.airbyte.db.mongodb.MongoUtils.MongoInstanceType.STANDALONE;
import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.assertj.core.api.AssertionsForClassTypes.catchThrowable;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
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
import java.util.List;
import org.bson.BsonArray;
import org.bson.BsonString;
import org.bson.Document;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MongoDBContainer;
import org.testcontainers.utility.DockerImageName;

public class MongoDbSourceStandaloneAcceptanceTest extends MongoDbSourceAbstractAcceptanceTest {

  private MongoDBContainer mongoDBContainer;

  private static final List<Field> SUB_FIELDS = List.of(
      Field.of("testObject", JsonSchemaType.OBJECT, List.of(
          Field.of("name", JsonSchemaType.STRING),
          Field.of("testField1", JsonSchemaType.STRING),
          Field.of("testInt", JsonSchemaType.NUMBER),
          Field.of("thirdLevelDocument", JsonSchemaType.OBJECT, List.of(
              Field.of("data", JsonSchemaType.STRING),
              Field.of("intData", JsonSchemaType.NUMBER))))));

  private static final List<Field> FIELDS = List.of(
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
    mongoDBContainer = new MongoDBContainer(DockerImageName.parse("mongo:4.0.10"));
    mongoDBContainer.start();

    final JsonNode instanceConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("instance", STANDALONE.getType())
        .put(JdbcUtils.HOST_KEY, mongoDBContainer.getHost())
        .put(JdbcUtils.PORT_KEY, mongoDBContainer.getFirstMappedPort())
        .put(JdbcUtils.TLS_KEY, false)
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("instance_type", instanceConfig)
        .put(JdbcUtils.DATABASE_KEY, DATABASE_NAME)
        .put("auth_source", "admin")
        .build());

    final var connectionString = String.format("mongodb://%s:%s/",
        mongoDBContainer.getHost(),
        mongoDBContainer.getFirstMappedPort());

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
    database.close();
    mongoDBContainer.close();
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
  public void testCheckIncorrectHost() throws Exception {
    final JsonNode instanceConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("instance", STANDALONE.getType())
        .put("host", "localhost2")
        .put("port", mongoDBContainer.getFirstMappedPort())
        .put("tls", false)
        .build());

    final JsonNode conf = Jsons.jsonNode(ImmutableMap.builder()
        .put("instance_type", instanceConfig)
        .put("database", DATABASE_NAME)
        .put("auth_source", "admin")
        .build());
    final Throwable throwable = catchThrowable(() -> new MongoDbSource().check(config));
    assertThat(throwable).isInstanceOf(ConfigErrorException.class);
    assertThat(((ConfigErrorException) throwable).getDisplayMessage()
        .contains("State code: -3"));
  }

  @Test
  public void testCheckIncorrectPort() throws Exception {
    final JsonNode instanceConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("instance", STANDALONE.getType())
        .put("host", mongoDBContainer.getHost())
        .put("port", 1234)
        .put("tls", false)
        .build());

    final JsonNode conf = Jsons.jsonNode(ImmutableMap.builder()
        .put("instance_type", instanceConfig)
        .put("database", DATABASE_NAME)
        .put("auth_source", "admin")
        .build());
    final Throwable throwable = catchThrowable(() -> new MongoDbSource().check(config));
    assertThat(throwable).isInstanceOf(ConfigErrorException.class);
    assertThat(((ConfigErrorException) throwable).getDisplayMessage()
        .contains("State code: -3"));
  }

}
