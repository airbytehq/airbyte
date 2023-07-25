/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.mongodb;

import static io.airbyte.db.mongodb.MongoDatabase.COLLECTION_COUNT_KEY;
import static io.airbyte.db.mongodb.MongoDatabase.COLLECTION_STORAGE_SIZE_KEY;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.MongoCommandException;
import com.mongodb.ReadConcern;
import com.mongodb.ServerAddress;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.connection.ClusterType;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;
import org.bson.BsonDocument;
import org.bson.BsonString;
import org.bson.Document;
import org.bson.types.ObjectId;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MongoDBContainer;

class MongoDatabaseTest {

  private static final String COLLECTION_NAME = "movies";
  private static final String DB_NAME = "airbyte_test";
  private static final Integer DATASET_SIZE = 10000;
  private static final String MONGO_DB_VERSION = "6.0.8";

  private static MongoDBContainer MONGO_DB;

  private MongoDatabase mongoDatabase;

  @BeforeAll
  static void init() {
    MONGO_DB = new MongoDBContainer("mongo:" + MONGO_DB_VERSION);
    MONGO_DB.start();

    try (final MongoClient client = MongoClients.create(MONGO_DB.getReplicaSetUrl() + "?retryWrites=false")) {
      final MongoCollection<Document> collection = client.getDatabase(DB_NAME).getCollection(COLLECTION_NAME);
      final List<Document> documents = IntStream.range(0, DATASET_SIZE).boxed()
          .map(i -> new Document().append("_id", new ObjectId()).append("title", "Movie #" + i)).collect(Collectors.toList());
      collection.insertMany(documents);
    }
  }

  @AfterAll
  static void cleanup() {
    MONGO_DB.stop();
  }

  @BeforeEach
  void setup() {
    mongoDatabase = new MongoDatabase(MONGO_DB.getReplicaSetUrl(), DB_NAME);
  }

  @AfterEach
  void tearDown() throws Exception {
    mongoDatabase.close();
  }

  @Test
  void testInvalidClientConnectionString() {
    assertThrows(RuntimeException.class, () -> new MongoDatabase("invalid connection string", DB_NAME));
    assertThrows(RuntimeException.class, () -> new MongoDatabase(null, DB_NAME));
  }

  @Test
  void testGetDatabase() {
    assertEquals(DB_NAME, mongoDatabase.getDatabase().getName());
  }

  @Test
  void testGetDatabaseNames() {
    final List<String> databaseNames = new ArrayList<>();
    mongoDatabase.getDatabaseNames().forEach(databaseNames::add);
    assertEquals(4, databaseNames.size());
    assertTrue(databaseNames.contains(DB_NAME));

    // Built-in MongoDB databases
    assertTrue(databaseNames.contains("admin"));
    assertTrue(databaseNames.contains("config"));
    assertTrue(databaseNames.contains("local"));
  }

  @Test
  void testGetCollectionNames() {
    final Set<String> collectionNames = mongoDatabase.getCollectionNames();
    assertEquals(1, collectionNames.size());
    assertTrue(collectionNames.contains(COLLECTION_NAME));
  }

  @Test
  void testGetCollection() {
    final MongoCollection<Document> collection = mongoDatabase.getCollection(COLLECTION_NAME);
    assertNotNull(collection);
    assertEquals(COLLECTION_NAME, collection.getNamespace().getCollectionName());
    assertEquals(ReadConcern.MAJORITY, collection.getReadConcern());
  }

  @Test
  void testGetUnknownCollection() {
    final MongoCollection<Document> collection = mongoDatabase.getCollection("unknown collection");
    assertNotNull(collection);
    assertEquals(ReadConcern.MAJORITY, collection.getReadConcern());
  }

  @Test
  void testGetOrCreateNewCollection() {
    final String collectionName = "newCollection";
    final MongoCollection<Document> collection = mongoDatabase.getOrCreateNewCollection(collectionName);
    assertNotNull(collection);
    final MongoCollection<Document> collection2 = mongoDatabase.getOrCreateNewCollection(collectionName);
    assertNotNull(collection2);
    assertEquals(collection.getNamespace().getCollectionName(), collection2.getNamespace().getCollectionName());
  }

  @Test
  void testCreateCollection() {
    final String collectionName = "newCollection";
    final MongoCollection<Document> collection = mongoDatabase.createCollection(collectionName);
    assertNotNull(collection);
    assertEquals(collectionName, collection.getNamespace().getCollectionName());
  }

  @Test
  void getDatabaseName() {
    assertEquals(DB_NAME, mongoDatabase.getName());
  }

  @Test
  void testReadingResults() {
    final Stream<JsonNode> results = mongoDatabase.read(COLLECTION_NAME, List.of("_id", "title"), Optional.empty());
    assertEquals(DATASET_SIZE.longValue(), results.count());
  }

  @Test
  void testGetCollectionStatistics() {
    final Map<String, Object> statistics = mongoDatabase.getCollectionStats(COLLECTION_NAME);
    assertEquals(DATASET_SIZE, statistics.get(COLLECTION_COUNT_KEY));
    assertEquals(4096, statistics.get(COLLECTION_STORAGE_SIZE_KEY));
  }

  @Test
  void testGetCollectionStatisticsCommandError() {
    final MongoDatabase mongoDatabase1 = mock(MongoDatabase.class);
    final com.mongodb.client.MongoDatabase clientMongoDatabase = mock(com.mongodb.client.MongoDatabase.class);
    final BsonDocument response = new BsonDocument("test", new BsonString("error"));
    final MongoCommandException error = new MongoCommandException(response, mock(ServerAddress.class));
    when(clientMongoDatabase.runCommand(any())).thenThrow(error);
    when(mongoDatabase1.getDatabase()).thenReturn(clientMongoDatabase);

    final Map<String, Object> statistics = mongoDatabase1.getCollectionStats(COLLECTION_NAME);
    assertTrue(statistics.isEmpty());
  }

  @Test
  void testGetServerType() {
    assertEquals(ClusterType.UNKNOWN.name(), mongoDatabase.getServerType());
  }

  @Test
  void testGetServerVersion() {
    assertEquals(MONGO_DB_VERSION, mongoDatabase.getServerVersion());
  }

  @Test
  void testGetServerVersionCommandError() {
    final MongoDatabase mongoDatabase1 = mock(MongoDatabase.class);
    final com.mongodb.client.MongoDatabase clientMongoDatabase = mock(com.mongodb.client.MongoDatabase.class);
    final BsonDocument response = new BsonDocument("test", new BsonString("error"));
    final MongoCommandException error = new MongoCommandException(response, mock(ServerAddress.class));
    when(clientMongoDatabase.runCommand(any())).thenThrow(error);
    when(mongoDatabase1.getDatabase()).thenReturn(clientMongoDatabase);

    assertNull(mongoDatabase1.getServerVersion());
  }

}
