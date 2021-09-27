/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.mongodb.client.MongoCollection;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.bson.Document;

public class MongoDbSourceAtlasAcceptanceTest extends MongoDbSourceAbstractAcceptanceTest {

  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");

  @Override
  protected void setupEnvironment(TestDestinationEnv environment) throws Exception {
    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a MongoDB credentials file. By default {module-root}/" + CREDENTIALS_PATH
              + ". Override by setting setting path with the CREDENTIALS_PATH constant.");
    }

    final String credentialsJsonString = new String(Files.readAllBytes(CREDENTIALS_PATH));
    final JsonNode credentialsJson = Jsons.deserialize(credentialsJsonString);

    final JsonNode instanceConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("cluster_url", credentialsJson.get("cluster_url").asText())
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("user", credentialsJson.get("user").asText())
        .put("password", credentialsJson.get("password").asText())
        .put("instance_type", instanceConfig)
        .put("database", DATABASE_NAME)
        .put("auth_source", "admin")
        .build());

    String connectionString = String.format("mongodb+srv://%s:%s@%s/%s?authSource=admin&retryWrites=true&w=majority&tls=true",
        config.get("user").asText(),
        config.get("password").asText(),
        config.get("instance_type").get("cluster_url").asText(),
        config.get("database").asText());

    database = new MongoDatabase(connectionString, DATABASE_NAME);

    MongoCollection<Document> collection = database.createCollection(COLLECTION_NAME);
    var doc1 = new Document("id", "0001").append("name", "Test");
    var doc2 = new Document("id", "0002").append("name", "Mongo");
    var doc3 = new Document("id", "0003").append("name", "Source");

    collection.insertMany(List.of(doc1, doc2, doc3));
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    database.getDatabase().getCollection(COLLECTION_NAME).drop();
    database.close();
  }

}
