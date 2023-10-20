/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static io.airbyte.integrations.source.mongodb.MongoCatalogHelper.AIRBYTE_STREAM_PROPERTIES;
import static io.airbyte.integrations.source.mongodb.MongoConstants.DATABASE_CONFIG_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.MongoConstants.DEFAULT_DISCOVER_SAMPLE_SIZE;
import static io.airbyte.integrations.source.mongodb.MongoUtil.MAX_QUEUE_SIZE;
import static io.airbyte.integrations.source.mongodb.MongoUtil.MIN_QUEUE_SIZE;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyBoolean;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.core.type.TypeReference;
import com.mongodb.MongoCommandException;
import com.mongodb.MongoCredential;
import com.mongodb.MongoException;
import com.mongodb.MongoSecurityException;
import com.mongodb.ServerAddress;
import com.mongodb.client.AggregateIterable;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.MongoIterable;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcConnectorMetadataInjector;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import org.bson.BsonDocument;
import org.bson.Document;
import org.junit.jupiter.api.Test;

public class MongoUtilTest {

  private static final String JSON_TYPE_PROPERTY_NAME = "type";

  @Test
  void testCheckDatabaseExists() {
    final String databaseName = "test";
    final List<String> databaseNames = List.of("test", "test1", "test2");
    final MongoIterable<String> iterable = mock(MongoIterable.class);
    final MongoClient mongoClient = mock(MongoClient.class);

    when(iterable.spliterator()).thenReturn(databaseNames.spliterator());
    when(mongoClient.listDatabaseNames()).thenReturn(iterable);

    assertTrue(MongoUtil.checkDatabaseExists(mongoClient, databaseName));
    assertFalse(MongoUtil.checkDatabaseExists(mongoClient, "other"));
  }

  @Test
  void testGetAirbyteStreams() throws IOException {
    final AggregateIterable<Document> aggregateIterable = mock(AggregateIterable.class);
    final MongoCursor<Document> cursor = mock(MongoCursor.class);
    final String databaseName = "database";
    final Document authorizedCollectionsResponse = Document.parse(MoreResources.readResource("authorized_collections_response.json"));
    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoCollection mongoCollection = mock(MongoCollection.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
    final List<Map<String, Object>> schemaDiscoveryJsonResponses =
        Jsons.deserialize(MoreResources.readResource("schema_discovery_response.json"), new TypeReference<>() {});
    final List<Document> schemaDiscoveryResponses = schemaDiscoveryJsonResponses.stream().map(Document::new).toList();

    when(cursor.hasNext()).thenReturn(true, true, false);
    when(cursor.next()).thenReturn(schemaDiscoveryResponses.get(0), schemaDiscoveryResponses.get(1));
    when(aggregateIterable.cursor()).thenReturn(cursor);
    when(mongoCollection.aggregate(any())).thenReturn(aggregateIterable);
    when(mongoDatabase.getCollection(any())).thenReturn(mongoCollection);
    when(mongoDatabase.runCommand(any())).thenReturn(authorizedCollectionsResponse);
    when(aggregateIterable.allowDiskUse(anyBoolean())).thenReturn(aggregateIterable);
    when(mongoClient.getDatabase(databaseName)).thenReturn(mongoDatabase);

    final List<AirbyteStream> streams = MongoUtil.getAirbyteStreams(mongoClient, databaseName, DEFAULT_DISCOVER_SAMPLE_SIZE);
    assertNotNull(streams);
    assertEquals(1, streams.size());
    assertEquals(12, streams.get(0).getJsonSchema().get(AIRBYTE_STREAM_PROPERTIES).size());
  }

  @Test
  void testGetAirbyteStreamsEmptyCollection() throws IOException {
    final AggregateIterable<Document> aggregateIterable = mock(AggregateIterable.class);
    final MongoCursor<Document> cursor = mock(MongoCursor.class);
    final String databaseName = "database";
    final Document authorizedCollectionsResponse = Document.parse(MoreResources.readResource("authorized_collections_response.json"));
    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoCollection mongoCollection = mock(MongoCollection.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);

    when(cursor.hasNext()).thenReturn(false);
    when(aggregateIterable.cursor()).thenReturn(cursor);
    when(mongoCollection.aggregate(any())).thenReturn(aggregateIterable);
    when(mongoDatabase.getCollection(any())).thenReturn(mongoCollection);
    when(mongoDatabase.runCommand(any())).thenReturn(authorizedCollectionsResponse);
    when(mongoClient.getDatabase(databaseName)).thenReturn(mongoDatabase);
    when(aggregateIterable.allowDiskUse(anyBoolean())).thenReturn(aggregateIterable);

    final List<AirbyteStream> streams = MongoUtil.getAirbyteStreams(mongoClient, databaseName, DEFAULT_DISCOVER_SAMPLE_SIZE);
    assertNotNull(streams);
    assertEquals(0, streams.size());
  }

  @Test
  void testGetAirbyteStreamsDifferentDataTypes() throws IOException {
    final AggregateIterable<Document> aggregateIterable = mock(AggregateIterable.class);
    final MongoCursor<Document> cursor = mock(MongoCursor.class);
    final String databaseName = "database";
    final Document authorizedCollectionsResponse = Document.parse(MoreResources.readResource("authorized_collections_response.json"));
    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoCollection mongoCollection = mock(MongoCollection.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
    final List<Map<String, Object>> schemaDiscoveryJsonResponses =
        Jsons.deserialize(MoreResources.readResource("schema_discovery_response_different_datatypes.json"), new TypeReference<>() {});
    final List<Document> schemaDiscoveryResponses = schemaDiscoveryJsonResponses.stream().map(Document::new).toList();

    when(cursor.hasNext()).thenReturn(true, true, false);
    when(cursor.next()).thenReturn(schemaDiscoveryResponses.get(0), schemaDiscoveryResponses.get(1));
    when(aggregateIterable.cursor()).thenReturn(cursor);
    when(mongoCollection.aggregate(any())).thenReturn(aggregateIterable);
    when(mongoDatabase.getCollection(any())).thenReturn(mongoCollection);
    when(mongoDatabase.runCommand(any())).thenReturn(authorizedCollectionsResponse);
    when(mongoClient.getDatabase(databaseName)).thenReturn(mongoDatabase);
    when(aggregateIterable.allowDiskUse(anyBoolean())).thenReturn(aggregateIterable);

    final List<AirbyteStream> streams = MongoUtil.getAirbyteStreams(mongoClient, databaseName, DEFAULT_DISCOVER_SAMPLE_SIZE);
    assertNotNull(streams);
    assertEquals(1, streams.size());
    assertEquals(11, streams.get(0).getJsonSchema().get(AIRBYTE_STREAM_PROPERTIES).size());
    assertEquals(JsonSchemaType.NUMBER.getJsonSchemaTypeMap().get(JSON_TYPE_PROPERTY_NAME),
        streams.get(0).getJsonSchema().get(AIRBYTE_STREAM_PROPERTIES).get("total").get(JSON_TYPE_PROPERTY_NAME).asText());
    assertEquals(JsonSchemaType.STRING.getJsonSchemaTypeMap().get(JSON_TYPE_PROPERTY_NAME),
        streams.get(0).getJsonSchema().get(AIRBYTE_STREAM_PROPERTIES).get(CDC_UPDATED_AT).get(JSON_TYPE_PROPERTY_NAME).asText());
    assertEquals(JsonSchemaType.STRING.getJsonSchemaTypeMap().get(JSON_TYPE_PROPERTY_NAME),
        streams.get(0).getJsonSchema().get(AIRBYTE_STREAM_PROPERTIES).get(CDC_DELETED_AT).get(JSON_TYPE_PROPERTY_NAME).asText());
    assertEquals(JsonSchemaType.NUMBER.getJsonSchemaTypeMap().get(JSON_TYPE_PROPERTY_NAME),
        streams.get(0).getJsonSchema().get(AIRBYTE_STREAM_PROPERTIES).get(MongoDbCdcConnectorMetadataInjector.CDC_DEFAULT_CURSOR)
            .get(JSON_TYPE_PROPERTY_NAME).asText());
  }

  @Test
  void testGetAuthorizedCollections() {
    final String databaseName = "test-database";
    final String collectionName = "test-collection";
    final Document result = new Document(Map.of("cursor", Map.of("firstBatch", List.of(Map.of("name", collectionName)))));
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
    final MongoClient mongoClient = mock(MongoClient.class);

    when(mongoDatabase.runCommand(any())).thenReturn(result);
    when(mongoClient.getDatabase(databaseName)).thenReturn(mongoDatabase);

    final Set<String> authorizedCollections = MongoUtil.getAuthorizedCollections(mongoClient, databaseName);

    assertEquals(Set.of(collectionName), authorizedCollections);
  }

  @Test
  void testGetAuthorizedCollectionsMongoException() {
    final String databaseName = "test-database";
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
    final MongoClient mongoClient = mock(MongoClient.class);

    when(mongoDatabase.runCommand(any())).thenThrow(new MongoException("test"));
    when(mongoClient.getDatabase(databaseName)).thenReturn(mongoDatabase);

    assertThrows(MongoException.class, () -> MongoUtil.getAuthorizedCollections(mongoClient, databaseName));
  }

  @Test
  void testGetAuthorizedCollectionsMongoSecurityException() {
    final String databaseName = "test-database";
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoCommandException cause = new MongoCommandException(new BsonDocument(), new ServerAddress());
    final MongoSecurityException exception =
        new MongoSecurityException(MongoCredential.createCredential("username", databaseName, "password".toCharArray()), "test", cause);

    when(mongoDatabase.runCommand(any())).thenThrow(exception);
    when(mongoClient.getDatabase(databaseName)).thenReturn(mongoDatabase);

    assertThrows(MongoSecurityException.class, () -> MongoUtil.getAuthorizedCollections(mongoClient, databaseName));
  }

  @Test
  void testGetDebeziumEventQueueSize() {
    final int queueSize = 5000;
    final MongoDbSourceConfig validQueueSizeConfiguration = new MongoDbSourceConfig(
        Jsons.jsonNode(Map.of(DATABASE_CONFIG_CONFIGURATION_KEY, Map.of(MongoConstants.QUEUE_SIZE_CONFIGURATION_KEY, queueSize))));
    final MongoDbSourceConfig tooSmallQueueSizeConfiguration = new MongoDbSourceConfig(
        Jsons.jsonNode(Map.of(DATABASE_CONFIG_CONFIGURATION_KEY, Map.of(MongoConstants.QUEUE_SIZE_CONFIGURATION_KEY, Integer.MIN_VALUE))));
    final MongoDbSourceConfig tooLargeQueueSizeConfiguration = new MongoDbSourceConfig(
        Jsons.jsonNode(Map.of(DATABASE_CONFIG_CONFIGURATION_KEY, Map.of(MongoConstants.QUEUE_SIZE_CONFIGURATION_KEY, Integer.MAX_VALUE))));
    final MongoDbSourceConfig missingQueueSizeConfiguration =
        new MongoDbSourceConfig(Jsons.jsonNode(Map.of(DATABASE_CONFIG_CONFIGURATION_KEY, Map.of())));

    assertEquals(queueSize, MongoUtil.getDebeziumEventQueueSize(validQueueSizeConfiguration).getAsInt());
    assertEquals(MIN_QUEUE_SIZE, MongoUtil.getDebeziumEventQueueSize(tooSmallQueueSizeConfiguration).getAsInt());
    assertEquals(MAX_QUEUE_SIZE, MongoUtil.getDebeziumEventQueueSize(tooLargeQueueSizeConfiguration).getAsInt());
    assertEquals(MAX_QUEUE_SIZE, MongoUtil.getDebeziumEventQueueSize(missingQueueSizeConfiguration).getAsInt());
  }

  @Test
  void testGetCollectionStatistics() throws IOException {
    final String collectionName = "test-collection";
    final String databaseName = "test-database";
    final String collStats = MoreResources.readResource("coll_stats_response.json");
    final List<Map<String, Object>> collStatsList = Jsons.deserialize(collStats, new TypeReference<>() {});
    final MongoCursor<Document> cursor = mock(MongoCursor.class);
    final AggregateIterable<Document> aggregateIterable = mock(AggregateIterable.class);
    final MongoCollection mongoCollection = mock(MongoCollection.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
    final MongoClient mongoClient = mock(MongoClient.class);

    final AirbyteStream stream = new AirbyteStream().withName(collectionName).withNamespace(databaseName);
    final ConfiguredAirbyteStream configuredAirbyteStream = new ConfiguredAirbyteStream().withStream(stream);

    when(cursor.hasNext()).thenReturn(true);
    when(cursor.next()).thenReturn(new Document(collStatsList.get(0)));
    when(aggregateIterable.cursor()).thenReturn(cursor);
    when(mongoCollection.aggregate(any())).thenReturn(aggregateIterable);
    when(mongoDatabase.getCollection(collectionName)).thenReturn(mongoCollection);
    when(mongoClient.getDatabase(databaseName)).thenReturn(mongoDatabase);
    when(aggregateIterable.allowDiskUse(anyBoolean())).thenReturn(aggregateIterable);

    final Optional<MongoUtil.CollectionStatistics> statistics = MongoUtil.getCollectionStatistics(mongoClient, configuredAirbyteStream);

    assertTrue(statistics.isPresent());
    assertEquals(746, statistics.get().count());
    assertEquals(67771, statistics.get().size());
  }

  @Test
  void testGetCollectionStatisticsNoResult() {
    final String collectionName = "test-collection";
    final String databaseName = "test-database";
    final MongoCursor<Document> cursor = mock(MongoCursor.class);
    final AggregateIterable<Document> aggregateIterable = mock(AggregateIterable.class);
    final MongoCollection mongoCollection = mock(MongoCollection.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
    final MongoClient mongoClient = mock(MongoClient.class);

    final AirbyteStream stream = new AirbyteStream().withName(collectionName).withNamespace(databaseName);
    final ConfiguredAirbyteStream configuredAirbyteStream = new ConfiguredAirbyteStream().withStream(stream);

    when(cursor.hasNext()).thenReturn(false);
    when(aggregateIterable.cursor()).thenReturn(cursor);
    when(mongoCollection.aggregate(any())).thenReturn(aggregateIterable);
    when(mongoDatabase.getCollection(collectionName)).thenReturn(mongoCollection);
    when(mongoClient.getDatabase(databaseName)).thenReturn(mongoDatabase);

    final Optional<MongoUtil.CollectionStatistics> statistics = MongoUtil.getCollectionStatistics(mongoClient, configuredAirbyteStream);

    assertFalse(statistics.isPresent());
  }

  @Test
  void testGetCollectionStatisticsEmptyResult() {
    final String collectionName = "test-collection";
    final String databaseName = "test-database";
    final List<Map<String, Object>> collStatsList = List.of(Map.of());
    final MongoCursor<Document> cursor = mock(MongoCursor.class);
    final AggregateIterable<Document> aggregateIterable = mock(AggregateIterable.class);
    final MongoCollection mongoCollection = mock(MongoCollection.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
    final MongoClient mongoClient = mock(MongoClient.class);

    final AirbyteStream stream = new AirbyteStream().withName(collectionName).withNamespace(databaseName);
    final ConfiguredAirbyteStream configuredAirbyteStream = new ConfiguredAirbyteStream().withStream(stream);

    when(cursor.hasNext()).thenReturn(true);
    when(cursor.next()).thenReturn(new Document(collStatsList.get(0)));
    when(aggregateIterable.cursor()).thenReturn(cursor);
    when(mongoCollection.aggregate(any())).thenReturn(aggregateIterable);
    when(mongoDatabase.getCollection(collectionName)).thenReturn(mongoCollection);
    when(mongoClient.getDatabase(databaseName)).thenReturn(mongoDatabase);

    final Optional<MongoUtil.CollectionStatistics> statistics = MongoUtil.getCollectionStatistics(mongoClient, configuredAirbyteStream);

    assertFalse(statistics.isPresent());
  }

  @Test
  void testGetCollectionStatisticsException() {
    final String collectionName = "test-collection";
    final String databaseName = "test-database";
    final MongoClient mongoClient = mock(MongoClient.class);

    final AirbyteStream stream = new AirbyteStream().withName(collectionName).withNamespace(databaseName);
    final ConfiguredAirbyteStream configuredAirbyteStream = new ConfiguredAirbyteStream().withStream(stream);

    when(mongoClient.getDatabase(databaseName)).thenThrow(new IllegalArgumentException("test"));

    final Optional<MongoUtil.CollectionStatistics> statistics = MongoUtil.getCollectionStatistics(mongoClient, configuredAirbyteStream);

    assertFalse(statistics.isPresent());
  }

}
