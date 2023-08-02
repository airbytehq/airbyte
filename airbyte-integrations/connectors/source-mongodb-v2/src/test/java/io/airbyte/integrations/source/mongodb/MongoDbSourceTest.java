/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.mongodb.MongoDatabase;
import io.airbyte.db.mongodb.MongoUtils;
import io.airbyte.integrations.source.relationaldb.CursorInfo;
import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import org.bson.BsonType;
import org.bson.Document;
import org.bson.types.ObjectId;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MongoDBContainer;

class MongoDbSourceTest {

  private static final String COLLECTION_NAME = "movies";
  private static final String DB_NAME = "local";
  private static final Integer DATASET_SIZE = 10000;

  private static MongoDBContainer MONGO_DB;

  private JsonNode airbyteSourceConfig;

  private MongoDbSource source;

  @BeforeAll
  static void init() {
    MONGO_DB = new MongoDBContainer("mongo:6.0.8");
    MONGO_DB.start();

    try (final MongoClient client = MongoClients.create(MONGO_DB.getReplicaSetUrl() + "?retryWrites=false")) {
      final MongoCollection<Document> collection = client.getDatabase(DB_NAME).getCollection(COLLECTION_NAME);
      final List<Document> documents = IntStream.range(0, DATASET_SIZE).boxed().map(MongoDbSourceTest::buildDocument).collect(Collectors.toList());
      collection.insertMany(documents);
    }
  }

  @AfterAll
  static void cleanup() {
    MONGO_DB.stop();
  }

  @BeforeEach
  void setup() {
    airbyteSourceConfig = createConfiguration(Optional.empty(), Optional.empty());
    source = new MongoDbSource();
  }

  @AfterEach
  void tearDown() throws Exception {
    source.close();
  }

  @Test
  void testToDatabaseConfig() {
    final String authSource = "admin";
    final String password = "password";
    final String username = "username";
    final JsonNode airbyteSourceConfig = createConfiguration(Optional.of(username), Optional.of(password));

    final JsonNode databaseConfig = source.toDatabaseConfig(airbyteSourceConfig);

    assertNotNull(databaseConfig);
    assertEquals(String.format(MongoUtils.MONGODB_SERVER_URL,
        String.format("%s:%s@", username, password),
        MONGO_DB.getHost(), MONGO_DB.getFirstMappedPort(), DB_NAME, authSource, false), databaseConfig.get("connectionString").asText());
    assertEquals(DB_NAME, databaseConfig.get(JdbcUtils.DATABASE_KEY).asText());
  }

  @Test
  void testGetCheckOperations() throws Exception {
    final MongoDatabase database = source.createDatabase(airbyteSourceConfig);
    final List<CheckedConsumer<MongoDatabase, Exception>> checkedConsumerList = source.getCheckOperations(airbyteSourceConfig);
    assertNotNull(checkedConsumerList);

    for (CheckedConsumer<MongoDatabase, Exception> mongoDatabaseExceptionCheckedConsumer : checkedConsumerList) {
      assertDoesNotThrow(() -> mongoDatabaseExceptionCheckedConsumer.accept(database));
    }
  }

  @Test
  void testGetCheckOperationsWithFailure() throws Exception {
    airbyteSourceConfig = createConfiguration(Optional.of("username"), Optional.of("password"));

    final MongoDatabase database = source.createDatabase(airbyteSourceConfig);
    final List<CheckedConsumer<MongoDatabase, Exception>> checkedConsumerList = source.getCheckOperations(airbyteSourceConfig);
    assertNotNull(checkedConsumerList);

    for (CheckedConsumer<MongoDatabase, Exception> mongoDatabaseExceptionCheckedConsumer : checkedConsumerList) {
      assertThrows(ConnectionErrorException.class, () -> mongoDatabaseExceptionCheckedConsumer.accept(database));
    }
  }

  @Test
  void testGetExcludedInternalNameSpaces() {
    assertEquals(0, source.getExcludedInternalNameSpaces().size());
  }

  @Test
  void testFullRefresh() throws Exception {
    final List<JsonNode> results = new ArrayList<>();
    final MongoDatabase database = source.createDatabase(airbyteSourceConfig);

    final AutoCloseableIterator<JsonNode> stream = source.queryTableFullRefresh(database, List.of(), null, COLLECTION_NAME, null, null);
    stream.forEachRemaining(results::add);

    assertNotNull(results);
    assertEquals(DATASET_SIZE, results.size());
  }

  @Test
  void testIncrementalRefresh() throws Exception {
    final CursorInfo cursor = new CursorInfo("index", "0", "index", "999");
    final List<JsonNode> results = new ArrayList<>();
    final MongoDatabase database = source.createDatabase(airbyteSourceConfig);

    final AutoCloseableIterator<JsonNode> stream =
        source.queryTableIncremental(database, List.of(), null, COLLECTION_NAME, cursor, BsonType.INT32);
    stream.forEachRemaining(results::add);

    assertNotNull(results);
    assertEquals(DATASET_SIZE - 1000, results.size());
  }

  private static JsonNode createConfiguration(final Optional<String> username, final Optional<String> password) {
    final Map<String, Object> config = new HashMap<>();
    final Map<String, Object> baseConfig = Map.of(
        JdbcUtils.DATABASE_KEY, DB_NAME,
        MongoUtils.INSTANCE_TYPE, Map.of(
            JdbcUtils.HOST_KEY, MONGO_DB.getHost(),
            MongoUtils.INSTANCE, MongoUtils.MongoInstanceType.STANDALONE.getType(),
            JdbcUtils.PORT_KEY, MONGO_DB.getFirstMappedPort()),
        MongoUtils.AUTH_SOURCE, "admin",
        JdbcUtils.TLS_KEY, "false");

    config.putAll(baseConfig);
    username.ifPresent(u -> config.put(MongoUtils.USER, u));
    password.ifPresent(p -> config.put(JdbcUtils.PASSWORD_KEY, p));
    return Jsons.deserialize(Jsons.serialize(config));
  }

  private static Document buildDocument(final Integer i) {
    return new Document().append("_id", new ObjectId())
        .append("title", "Movie #" + i)
        .append("index", i)
        .append("timestamp", new Timestamp(System.currentTimeMillis()).toString().replace(' ', 'T'));
  }

}
