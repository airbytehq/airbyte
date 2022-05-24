/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.mongodb.client.MongoCursor;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import org.bson.Document;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MongoDBContainer;

import java.util.ArrayList;
import java.util.List;

import static com.mongodb.client.model.Projections.excludeId;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD_OR_DATABASE;
import static org.junit.jupiter.api.Assertions.assertEquals;

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
  protected TestDataComparator getTestDataComparator() {
    return new AdvancedTestDataComparator();
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
    return true;
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

  @Test
  void testCheckIncorrectPasswordFailure() {
    final JsonNode invalidConfig = getFailCheckConfig();
    ((ObjectNode) invalidConfig).put(DATABASE, DATABASE_NAME);
    ((ObjectNode) invalidConfig.get(AUTH_TYPE)).put("password", "fake");
    var destination = new MongodbDestination();
    final AirbyteConnectionStatus actual = destination.check(invalidConfig);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
    assertEquals(INCORRECT_USERNAME_OR_PASSWORD_OR_DATABASE.getValue(), actual.getMessage());
  }

  @Test
  public void testCheckIncorrectUsernameFailure() {
    final JsonNode invalidConfig = getFailCheckConfig();
    ((ObjectNode) invalidConfig).put(DATABASE, DATABASE_NAME);
    ((ObjectNode) invalidConfig.get(AUTH_TYPE)).put("username", "fakeusername");
    var destination = new MongodbDestination();
    final AirbyteConnectionStatus actual = destination.check(invalidConfig);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
    assertEquals(INCORRECT_USERNAME_OR_PASSWORD_OR_DATABASE.getValue(), actual.getMessage());
  }

  @Test
  public void testCheckIncorrectDataBaseFailure() {
    final JsonNode invalidConfig = getFailCheckConfig();
    ((ObjectNode) invalidConfig).put(DATABASE, DATABASE_FAIL_NAME);
    var destination = new MongodbDestination();
    final AirbyteConnectionStatus actual = destination.check(invalidConfig);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
    assertEquals(INCORRECT_USERNAME_OR_PASSWORD_OR_DATABASE.getValue(), actual.getMessage());
  }

  @Test
  public void testCheckIncorrectHost() {
    final JsonNode invalidConfig = getConfig();
    ((ObjectNode) invalidConfig).put(HOST, "localhost2");
    var destination = new MongodbDestination();
    final AirbyteConnectionStatus actual = destination.check(invalidConfig);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
    assertEquals(INCORRECT_HOST_OR_PORT.getValue(), actual.getMessage());
  }

  @Test
  public void testCheckIncorrectPort() {
    final JsonNode invalidConfig = getConfig();
    ((ObjectNode) invalidConfig).put(PORT, 1234);
    var destination = new MongodbDestination();
    final AirbyteConnectionStatus actual = destination.check(invalidConfig);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
    assertEquals(INCORRECT_HOST_OR_PORT.getValue(), actual.getMessage());
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
