/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.mongodb;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.ReadConcern;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;
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

  private static MongoDBContainer MONGO_DB;

  private MongoDatabase mongoDatabase;

  @BeforeAll
  static void init() {
    MONGO_DB = new MongoDBContainer("mongo:6.0.8");
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

}
