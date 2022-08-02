/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import static com.mongodb.client.model.Projections.excludeId;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.mongodb.client.MongoCursor;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.db.mongodb.MongoUtils.MongoInstanceType;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import org.bson.Document;
import org.testcontainers.containers.BindMode;
import org.testcontainers.containers.MongoDBContainer;
import org.testcontainers.containers.wait.strategy.Wait;

public class MongodbDestinationStrictEncryptAcceptanceTest extends DestinationAcceptanceTest {

  private static final String AUTH_TYPE = "auth_type";
  private static final String INSTANCE_TYPE = "instance_type";
  private static final String AIRBYTE_DATA = "_airbyte_data";
  private static final String DATABASE_NAME = "test";
  private static final String DATABASE_USER_NAME = "po";
  private static final String DATABASE_PASSWORD = "password";

  private static JsonNode config;
  private static MongoDBContainer container;
  private final MongodbNameTransformer namingResolver = new MongodbNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-mongodb-strict-encrypt:dev";
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    List<String> list = new ArrayList<>();
    list.add("MONGO_INITDB_ROOT_USERNAME=" + DATABASE_USER_NAME);
    list.add("MONGO_INITDB_ROOT_PASSWORD=" + DATABASE_PASSWORD);
    list.add("MONGO_INITDB_DATABASE=" + DATABASE_NAME);
    container = new MongoDBContainer("mongo:4.0.10")
        .withClasspathResourceMapping("mongod.conf", "/etc/mongod.conf", BindMode.READ_ONLY)
        .withClasspathResourceMapping("mongodb.pem", "/etc/ssl/mongodb.pem", BindMode.READ_ONLY)
        .withClasspathResourceMapping("mongodb-cert.crt", "/etc/ssl/mongodb-cert.crt", BindMode.READ_ONLY)
        .withExposedPorts(27017)
        .withCommand("mongod --auth --config /etc/mongod.conf")
        .waitingFor(Wait.forListeningPort().withStartupTimeout(Duration.ofSeconds(120)));
    container.setEnv(list);

    container.start();
  }

  @Override
  protected JsonNode getConfig() {
    final JsonNode instanceConfig = getInstanceConfig();

    final JsonNode authConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("authorization", "login/password")
        .put(JdbcUtils.USERNAME_KEY, DATABASE_USER_NAME)
        .put(JdbcUtils.PASSWORD_KEY, DATABASE_PASSWORD)
        .build());

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.DATABASE_KEY, DATABASE_NAME)
        .put(AUTH_TYPE, authConfig)
        .put(INSTANCE_TYPE, instanceConfig)
        .build());
    return Jsons.clone(config);
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode instanceConfig = getInstanceConfig();
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.DATABASE_KEY, DATABASE_NAME)
        .put(AUTH_TYPE, Jsons.jsonNode(ImmutableMap.builder()
            .put("authorization", "none")
            .build()))
        .put(INSTANCE_TYPE, instanceConfig)
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
    var mongoDatabase = getMongoDatabase();
    final var collection = mongoDatabase.getOrCreateNewCollection(namingResolver.getRawTableName(streamName));
    final List<JsonNode> result = new ArrayList<>();
    try (final MongoCursor<Document> cursor = collection.find().projection(excludeId()).iterator()) {
      while (cursor.hasNext()) {
        result.add(Jsons.jsonNode(cursor.next().get(AIRBYTE_DATA)));
      }
    }
    return result;
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    container.close();
  }

  private MongoDatabase getMongoDatabase() {
    final String connectionString = String.format("mongodb://%s:%s@%s:%s/%s?authSource=admin&tcl=true",
        config.get(AUTH_TYPE).get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(AUTH_TYPE).get(JdbcUtils.PASSWORD_KEY).asText(),
        config.get(INSTANCE_TYPE).get(JdbcUtils.HOST_KEY).asText(),
        config.get(INSTANCE_TYPE).get(JdbcUtils.PORT_KEY).asText(),
        config.get(JdbcUtils.DATABASE_KEY).asText());

    return new MongoDatabase(connectionString, config.get(JdbcUtils.DATABASE_KEY).asText());
  }

  private JsonNode getInstanceConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("instance", MongoInstanceType.STANDALONE.getType())
        .put(JdbcUtils.HOST_KEY, container.getHost())
        .put(JdbcUtils.PORT_KEY, container.getMappedPort(27017))
        .build());
  }

}
