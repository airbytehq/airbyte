/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static io.airbyte.db.mongodb.MongoUtils.MongoInstanceType.STANDALONE;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.mongodb.client.MongoCollection;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import java.util.List;
import org.bson.BsonArray;
import org.bson.BsonString;
import org.bson.Document;
import org.testcontainers.containers.MongoDBContainer;
import org.testcontainers.utility.DockerImageName;

public class MongoDbSourceStandaloneAcceptanceTest extends MongoDbSourceAbstractAcceptanceTest {

  private MongoDBContainer mongoDBContainer;

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws Exception {
    mongoDBContainer = new MongoDBContainer(DockerImageName.parse("mongo:4.0.10"));
    mongoDBContainer.start();

    final JsonNode instanceConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("instance", STANDALONE.getType())
        .put("host", mongoDBContainer.getHost())
        .put("port", mongoDBContainer.getFirstMappedPort())
        .put("tls", false)
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("instance_type", instanceConfig)
        .put("database", DATABASE_NAME)
        .put("auth_source", "admin")
        .build());

    final var connectionString = String.format("mongodb://%s:%s/",
        mongoDBContainer.getHost(),
        mongoDBContainer.getFirstMappedPort());

    database = new MongoDatabase(connectionString, DATABASE_NAME);

    final MongoCollection<Document> collection = database.createCollection(COLLECTION_NAME);
    final var doc1 = new Document("id", "0001").append("name", "Test")
        .append("test", 10).append("test_array", new BsonArray(List.of(new BsonString("test"), new BsonString("mongo"))));
    final var doc2 = new Document("id", "0002").append("name", "Mongo").append("test", "test_value");
    final var doc3 = new Document("id", "0003").append("name", "Source").append("test", null);

    collection.insertMany(List.of(doc1, doc2, doc3));
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    database.close();
    mongoDBContainer.close();
  }

}
