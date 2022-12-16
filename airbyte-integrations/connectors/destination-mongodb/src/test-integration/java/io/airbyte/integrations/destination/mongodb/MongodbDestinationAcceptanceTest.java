/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import static com.mongodb.client.model.Projections.excludeId;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.mongodb.client.MongoCursor;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import org.bson.Document;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MongoDBContainer;

public class MongodbDestinationAcceptanceTest extends DestinationAcceptanceTest {

  protected static final String DOCKER_IMAGE_NAME = "mongo:4.0.10";
  protected static final String DATABASE_NAME = "admin";
  private static final String DATABASE_FAIL_NAME = "fail_db";
  protected static final String AUTH_TYPE = "auth_type";
  protected static final String AIRBYTE_DATA = "_airbyte_data";

  private MongoDBContainer container;
  protected final MongodbNameTransformer namingResolver = new MongodbNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-mongodb:dev";
  }

  @Override
  protected JsonNode getConfig() throws Exception {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, container.getHost())
        .put(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, DATABASE_NAME)
        .put(AUTH_TYPE, getAuthTypeConfig())
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, container.getHost())
        .put(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, DATABASE_FAIL_NAME)
        .put(AUTH_TYPE, Jsons.jsonNode(ImmutableMap.builder()
            .put("authorization", "login/password")
            .put(JdbcUtils.USERNAME_KEY, "user")
            .put(JdbcUtils.PASSWORD_KEY, "pass")
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
    final MongoDatabase database = getMongoDatabase(container.getHost(),
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

  /**
   * For each of the state codes reference MongoDb's base error code yaml
   * <p>
   * https://github.com/mongodb/mongo/blob/master/src/mongo/base/error_codes.yml
   * </p>
   */
  @Test
  void testCheckIncorrectPasswordFailure() {
    try {
      final JsonNode invalidConfig = getFailCheckConfig();
      ((ObjectNode) invalidConfig).put(JdbcUtils.DATABASE_KEY, DATABASE_NAME);
      ((ObjectNode) invalidConfig.get(AUTH_TYPE)).put(JdbcUtils.PASSWORD_KEY, "fake");
      final MongodbDestination destination = new MongodbDestination();
      final AirbyteConnectionStatus status = destination.check(invalidConfig);
      assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    } catch (final Exception e) {
      assertTrue(e instanceof IOException);
    }
  }

  @Test
  public void testCheckIncorrectUsernameFailure() {
    try {
      final JsonNode invalidConfig = getFailCheckConfig();
      ((ObjectNode) invalidConfig).put(JdbcUtils.DATABASE_KEY, DATABASE_NAME);
      ((ObjectNode) invalidConfig.get(AUTH_TYPE)).put(JdbcUtils.USERNAME_KEY, "fakeusername");
      final MongodbDestination destination = new MongodbDestination();
      final AirbyteConnectionStatus status = destination.check(invalidConfig);
      assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    } catch (final Exception e) {
      assertTrue(e instanceof IOException);
    }

  }

  @Test
  public void testCheckIncorrectDataBaseFailure() {
    try {
      final JsonNode invalidConfig = getFailCheckConfig();
      ((ObjectNode) invalidConfig).put(JdbcUtils.DATABASE_KEY, DATABASE_FAIL_NAME);
      final MongodbDestination destination = new MongodbDestination();
      final AirbyteConnectionStatus status = destination.check(invalidConfig);
      assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    } catch (final Exception e) {
      assertTrue(e instanceof IOException);
    }

  }

  @Test
  public void testCheckIncorrectHost() {
    try {
      final JsonNode invalidConfig = getConfig();
      ((ObjectNode) invalidConfig).put(JdbcUtils.HOST_KEY, "localhost2");
      final MongodbDestination destination = new MongodbDestination();
      final AirbyteConnectionStatus status = destination.check(invalidConfig);
      assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    } catch (final Exception e) {
      assertTrue(e instanceof IOException);
    }

  }

  @Test
  public void testCheckIncorrectPort() {
    try {
      final JsonNode invalidConfig = getConfig();
      ((ObjectNode) invalidConfig).put(JdbcUtils.PORT_KEY, 1234);
      final MongodbDestination destination = new MongodbDestination();
      final AirbyteConnectionStatus status = destination.check(invalidConfig);
      assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    } catch (final Exception e) {
      assertTrue(e instanceof IOException);
    }
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

  protected JsonNode getAuthTypeConfig() {
    return Jsons.deserialize("{\n"
        + "  \"authorization\": \"none\"\n"
        + "}");
  }

  protected MongoDatabase getMongoDatabase(final String host, final int port, final String databaseName) {
    try {
      final String connectionString = String.format("mongodb://%s:%s/", host, port);
      return new MongoDatabase(connectionString, databaseName);
    } catch (final RuntimeException e) {
      throw new RuntimeException(e);
    }
  }

}
