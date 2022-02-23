/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import static com.mongodb.client.model.Projections.excludeId;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.mongodb.client.MongoCursor;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.util.ArrayList;
import java.util.List;
import org.bson.Document;
import org.testcontainers.containers.MongoDBContainer;

public class MongodbDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final String DOCKER_IMAGE_NAME = "mongo:4.0.10";
  private static final String HOST = "host";
  private static final String PORT = "port";
  private static final String DATABASE = "database";
  private static final String DATABASE_NAME = "admin";
  private static final String DATABASE_FAIL_NAME = "fail_db";
  private static final String AUTH_TYPE = "auth_type";
  private static final String AIRBYTE_DATA = "_airbyte_data";

  private MongoDBContainer container;
  private final MongodbNameTransformer namingResolver = new MongodbNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-mongodb:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(HOST, container.getHost())
        .put(PORT, container.getFirstMappedPort())
        .put(DATABASE, DATABASE_NAME)
        .put(AUTH_TYPE, getAuthTypeConfig())
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(HOST, container.getHost())
        .put(PORT, container.getFirstMappedPort())
        .put(DATABASE, DATABASE_FAIL_NAME)
        .put(AUTH_TYPE, Jsons.jsonNode(ImmutableMap.builder()
            .put("authorization", "login/password")
            .put("username", "user")
            .put("password", "pass")
            .build()))
        .build());
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema) {
    final var database = getMongoDatabase(container.getHost(),
        container.getFirstMappedPort(), DATABASE_NAME);
    final var collection = database.getOrCreateNewCollection(namingResolver.getRawTableName(streamName));
    final List<JsonNode> result = new ArrayList<>();
    try (final MongoCursor<Document> cursor = collection.find().projection(excludeId()).iterator()) {
      while (cursor.hasNext()) {
        result.add(Jsons.jsonNode(cursor.next().get(AIRBYTE_DATA)));
      }
    }
    return result;
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    container = new MongoDBContainer(DOCKER_IMAGE_NAME);
    container.start();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    container.stop();
    container.close();
  }

  /* Helpers */

  private JsonNode getAuthTypeConfig() {
    return Jsons.deserialize("{\n"
        + "  \"authorization\": \"none\"\n"
        + "}");
  }

  private MongoDatabase getMongoDatabase(final String host, final int port, final String databaseName) {
    try {
      final var connectionString = String.format("mongodb://%s:%s/", host, port);
      return new MongoDatabase(connectionString, databaseName);
    } catch (final RuntimeException e) {
      throw new RuntimeException(e);
    }
  }

}
