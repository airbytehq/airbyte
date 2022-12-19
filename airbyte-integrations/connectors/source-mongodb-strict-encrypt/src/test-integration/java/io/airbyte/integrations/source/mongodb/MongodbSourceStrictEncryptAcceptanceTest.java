/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.assertj.core.api.AssertionsForClassTypes.catchThrowable;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.mongodb.client.MongoCollection;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.db.mongodb.MongoUtils.MongoInstanceType;
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
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.List;
import org.bson.BsonArray;
import org.bson.BsonString;
import org.bson.Document;
import org.junit.jupiter.api.Test;

public class MongodbSourceStrictEncryptAcceptanceTest extends SourceAcceptanceTest {

  private static final String DATABASE_NAME = "test";
  private static final String COLLECTION_NAME = "acceptance_test1";
  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");
  private static final String INSTANCE_TYPE = "instance_type";

  protected JsonNode config;
  protected MongoDatabase database;

  @Override
  protected String getImageName() {
    return "airbyte/source-mongodb-strict-encrypt:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return config;
  }

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
        .put("instance", MongoInstanceType.ATLAS.getType())
        .put("cluster_url", credentialsJson.get("cluster_url").asText())
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("user", credentialsJson.get("user").asText())
        .put(JdbcUtils.PASSWORD_KEY, credentialsJson.get(JdbcUtils.PASSWORD_KEY).asText())
        .put(INSTANCE_TYPE, instanceConfig)
        .put(JdbcUtils.DATABASE_KEY, DATABASE_NAME)
        .put("auth_source", "admin")
        .build());

    final var credentials = String.format("%s:%s@", config.get("user").asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText());
    final String connectionString = String.format("mongodb+srv://%s%s/%s?retryWrites=true&w=majority&tls=true",
        credentials,
        config.get(INSTANCE_TYPE).get("cluster_url").asText(),
        config.get(JdbcUtils.DATABASE_KEY).asText());

    database = new MongoDatabase(connectionString, DATABASE_NAME);

    final MongoCollection<Document> collection = database.createCollection(COLLECTION_NAME);
    final var doc1 = new Document("id", "0001").append("name", "Test")
        .append("test", 10).append("test_array", new BsonArray(List.of(new BsonString("test"), new BsonString("mongo"))))
        .append("double_test", 100.12).append("int_test", 100);
    final var doc2 = new Document("id", "0002").append("name", "Mongo").append("test", "test_value").append("int_test", 201);
    final var doc3 = new Document("id", "0003").append("name", "Source").append("test", null)
        .append("double_test", 212.11).append("int_test", 302);

    collection.insertMany(List.of(doc1, doc2, doc3));
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    for (final String collectionName : database.getCollectionNames()) {
      database.getDatabase().getCollection(collectionName).drop();
    }
    database.close();
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("expected_spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() throws Exception {
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
                Field.of("int_test", JsonSchemaType.NUMBER))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.INCREMENTAL))
                .withDefaultCursorField(List.of("_id")))));
  }

  @Override
  protected JsonNode getState() throws Exception {
    return Jsons.jsonNode(new HashMap<>());
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = new MongodbSourceStrictEncrypt().spec();
    final ConnectorSpecification expected = getSpec();

    assertEquals(expected, actual);
  }

  @Test
  void testCheck() throws Exception {
    final JsonNode instanceConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("instance", MongoInstanceType.STANDALONE.getType())
        .put("tls", false)
        .build());

    final JsonNode invalidStandaloneConfig = Jsons.clone(getConfig());

    ((ObjectNode) invalidStandaloneConfig).put(INSTANCE_TYPE, instanceConfig);

    final Throwable throwable = catchThrowable(() -> new MongodbSourceStrictEncrypt().check(invalidStandaloneConfig));
    assertThat(throwable).isInstanceOf(ConfigErrorException.class);
    assertThat(((ConfigErrorException) throwable)
        .getDisplayMessage()
        .contains("TLS connection must be used to read from MongoDB."));
  }

}
