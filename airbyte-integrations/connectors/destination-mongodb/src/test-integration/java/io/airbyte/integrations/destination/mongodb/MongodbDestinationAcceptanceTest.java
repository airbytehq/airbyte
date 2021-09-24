/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mongodb;

import static com.mongodb.client.model.Projections.excludeId;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.mongodb.MongoClient;
import com.mongodb.ServerAddress;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.bson.Document;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.MongoDBContainer;

public class MongodbDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongodbDestinationAcceptanceTest.class);

  private static final String DOCER_IMAGE_NAME = "mongo:4.0.10";
  private static final String HOST = "host";
  private static final String PORT = "port";
  private static final String DATABASE = "database";
  private static final String DATABASE_NAME = "admin";
  private static final String DATABASE_FAIL_NAME = "fail_db";
  private static final String AUTH_TYPE = "auth_type";
  private static final String AIRBYTE_DATA = "_airbyte_data";

  private MongoDBContainer container;
  private MongodbNameTransformer namingResolver = new MongodbNameTransformer();

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
        .put(AUTH_TYPE, getAuthTypeConfig())
        .build());
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema) {
    var database = getMongoDatabase(container.getHost(),
        container.getFirstMappedPort(), DATABASE_NAME);
    var collection = getOrCreateNewMongodbCollection(database,
        namingResolver.getRawTableName(streamName));
    List<JsonNode> result = new ArrayList<>();
    try (MongoCursor<Document> cursor = collection.find().projection(excludeId()).iterator()) {
      while (cursor.hasNext()) {
        result.add(Jsons.jsonNode(cursor.next().get(AIRBYTE_DATA)));
      }
    }
    return result;
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    container = new MongoDBContainer(DOCER_IMAGE_NAME);
    container.start();
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    container.stop();
    container.close();
  }

  /* Helpers */

  private JsonNode getAuthTypeConfig() {
    return Jsons.deserialize("{\n"
        + "  \"authorization\": \"none\"\n"
        + "}");
  }

  private MongoDatabase getMongoDatabase(String host, int port, String dataBaseName) {
    try {
      var serverAddress = new ServerAddress(host, port);
      var mongoClient = new MongoClient(serverAddress);
      return mongoClient.getDatabase(dataBaseName);
    } catch (RuntimeException e) {
      throw new RuntimeException(e);
    }
  }

  private MongoCollection<Document> getOrCreateNewMongodbCollection(MongoDatabase database, String collectionName) {
    var collectionNames = StreamSupport
        .stream(database.listCollectionNames().spliterator(), false)
        .collect(Collectors.toSet());
    if (!collectionNames.contains(collectionName)) {
      database.createCollection(collectionName);
    }
    return database.getCollection(collectionName);
  }

}
