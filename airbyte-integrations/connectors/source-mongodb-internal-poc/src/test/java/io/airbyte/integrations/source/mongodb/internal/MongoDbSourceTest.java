/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.client.AggregateIterable;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;
import com.mongodb.connection.ClusterDescription;
import com.mongodb.connection.ClusterType;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.debezium.internals.DebeziumEventUtils;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteStream;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import org.bson.Document;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class MongoDbSourceTest {

  private static final String DB_NAME = "airbyte_test";

  private JsonNode airbyteSourceConfig;
  private MongoClient mongoClient;
  private MongoDbSource source;

  @BeforeEach
  void setup() {
    airbyteSourceConfig = createConfiguration(Optional.empty(), Optional.empty());
    mongoClient = mock(MongoClient.class);
    source = spy(new MongoDbSource());
    doReturn(mongoClient).when(source).createMongoClient(airbyteSourceConfig);
  }

  @Test
  void testCheckOperation() throws IOException {
    final ClusterDescription clusterDescription = mock(ClusterDescription.class);
    final Document response = Document.parse(MoreResources.readResource("authorized_collections_response.json"));
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);

    when(clusterDescription.getType()).thenReturn(ClusterType.REPLICA_SET);
    when(mongoDatabase.runCommand(any())).thenReturn(response);
    when(mongoClient.getDatabase(any())).thenReturn(mongoDatabase);
    when(mongoClient.getClusterDescription()).thenReturn(clusterDescription);

    final AirbyteConnectionStatus airbyteConnectionStatus = source.check(airbyteSourceConfig);
    assertNotNull(airbyteConnectionStatus);
    assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, airbyteConnectionStatus.getStatus());
  }

  @Test
  void testCheckOperationNoAuthorizedCollections() throws IOException {
    final ClusterDescription clusterDescription = mock(ClusterDescription.class);
    final Document response = Document.parse(MoreResources.readResource("no_authorized_collections_response.json"));
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);

    when(clusterDescription.getType()).thenReturn(ClusterType.REPLICA_SET);
    when(mongoDatabase.runCommand(any())).thenReturn(response);
    when(mongoClient.getDatabase(any())).thenReturn(mongoDatabase);
    when(mongoClient.getClusterDescription()).thenReturn(clusterDescription);

    final AirbyteConnectionStatus airbyteConnectionStatus = source.check(airbyteSourceConfig);
    assertNotNull(airbyteConnectionStatus);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, airbyteConnectionStatus.getStatus());
    assertEquals("Target MongoDB database does not contain any authorized collections.", airbyteConnectionStatus.getMessage());
  }

  @Test
  void testCheckOperationInvalidClusterType() throws IOException {
    final ClusterDescription clusterDescription = mock(ClusterDescription.class);
    final Document response = Document.parse(MoreResources.readResource("authorized_collections_response.json"));
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);

    when(clusterDescription.getType()).thenReturn(ClusterType.STANDALONE);
    when(mongoDatabase.runCommand(any())).thenReturn(response);
    when(mongoClient.getDatabase(any())).thenReturn(mongoDatabase);
    when(mongoClient.getClusterDescription()).thenReturn(clusterDescription);

    final AirbyteConnectionStatus airbyteConnectionStatus = source.check(airbyteSourceConfig);
    assertNotNull(airbyteConnectionStatus);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, airbyteConnectionStatus.getStatus());
    assertEquals("Target MongoDB instance is not a replica set cluster.", airbyteConnectionStatus.getMessage());
  }

  @Test
  void testCheckOperationUnexpectedException() {
    final String expectedMessage = "This is just a test failure.";
    when(mongoClient.getDatabase(any())).thenThrow(new IllegalArgumentException(expectedMessage));

    final AirbyteConnectionStatus airbyteConnectionStatus = source.check(airbyteSourceConfig);
    assertNotNull(airbyteConnectionStatus);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, airbyteConnectionStatus.getStatus());
    assertEquals(expectedMessage, airbyteConnectionStatus.getMessage());
  }

  @Test
  void testDiscoverOperation() throws IOException {
    final AggregateIterable<Document> aggregateIterable = mock(AggregateIterable.class);
    final List<Map<String, Object>> schemaDiscoveryJsonResponses =
        Jsons.deserialize(MoreResources.readResource("schema_discovery_response.json"), new TypeReference<>() {});
    final List<Document> schemaDiscoveryResponses = schemaDiscoveryJsonResponses.stream().map(s -> new Document(s)).collect(Collectors.toList());
    final Document authorizedCollectionsResponse = Document.parse(MoreResources.readResource("authorized_collections_response.json"));
    final MongoCollection mongoCollection = mock(MongoCollection.class);
    final MongoCursor<Document> cursor = mock(MongoCursor.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);

    when(cursor.hasNext()).thenReturn(true, true, false);
    when(cursor.next()).thenReturn(schemaDiscoveryResponses.get(0), schemaDiscoveryResponses.get(1));
    when(aggregateIterable.cursor()).thenReturn(cursor);
    when(mongoCollection.aggregate(any())).thenReturn(aggregateIterable);
    when(mongoDatabase.getCollection(any())).thenReturn(mongoCollection);
    when(mongoDatabase.runCommand(any())).thenReturn(authorizedCollectionsResponse);
    when(mongoClient.getDatabase(any())).thenReturn(mongoDatabase);

    final AirbyteCatalog airbyteCatalog = source.discover(airbyteSourceConfig);

    assertNotNull(airbyteCatalog);
    assertEquals(1, airbyteCatalog.getStreams().size());

    final Optional<AirbyteStream> stream = airbyteCatalog.getStreams().stream().findFirst();
    assertTrue(stream.isPresent());
    assertEquals(DB_NAME, stream.get().getNamespace());
    assertEquals("testCollection", stream.get().getName());
    assertEquals(JsonSchemaType.STRING.getJsonSchemaTypeMap().get("type"),
        stream.get().getJsonSchema().get("properties").get("_id").get("type").asText());
    assertEquals(JsonSchemaType.STRING.getJsonSchemaTypeMap().get("type"),
        stream.get().getJsonSchema().get("properties").get("name").get("type").asText());
    assertEquals(JsonSchemaType.STRING.getJsonSchemaTypeMap().get("type"),
        stream.get().getJsonSchema().get("properties").get("last_updated").get("type").asText());
    assertEquals(JsonSchemaType.NUMBER.getJsonSchemaTypeMap().get("type"),
        stream.get().getJsonSchema().get("properties").get("total").get("type").asText());
    assertEquals(JsonSchemaType.NUMBER.getJsonSchemaTypeMap().get("type"),
        stream.get().getJsonSchema().get("properties").get("price").get("type").asText());
    assertEquals(JsonSchemaType.ARRAY.getJsonSchemaTypeMap().get("type"),
        stream.get().getJsonSchema().get("properties").get("items").get("type").asText());
    assertEquals(JsonSchemaType.OBJECT.getJsonSchemaTypeMap().get("type"),
        stream.get().getJsonSchema().get("properties").get("owners").get("type").asText());
    assertEquals(JsonSchemaType.STRING.getJsonSchemaTypeMap().get("type"),
        stream.get().getJsonSchema().get("properties").get("other").get("type").asText());
    assertEquals(JsonSchemaType.NUMBER.getJsonSchemaTypeMap().get("type"),
        stream.get().getJsonSchema().get("properties").get(DebeziumEventUtils.CDC_LSN).get("type").asText());
    assertEquals(JsonSchemaType.STRING.getJsonSchemaTypeMap().get("type"),
        stream.get().getJsonSchema().get("properties").get(DebeziumEventUtils.CDC_DELETED_AT).get("type").asText());
    assertEquals(JsonSchemaType.STRING.getJsonSchemaTypeMap().get("type"),
        stream.get().getJsonSchema().get("properties").get(DebeziumEventUtils.CDC_UPDATED_AT).get("type").asText());
    assertEquals(true, stream.get().getSourceDefinedCursor());
    assertEquals(List.of(MongoCatalogHelper.DEFAULT_CURSOR_FIELD), stream.get().getDefaultCursorField());
    assertEquals(List.of(List.of(MongoCatalogHelper.DEFAULT_CURSOR_FIELD)), stream.get().getSourceDefinedPrimaryKey());
    assertEquals(MongoCatalogHelper.SUPPORTED_SYNC_MODES, stream.get().getSupportedSyncModes());
  }

  @Test
  void testDiscoverOperationWithUnexpectedFailure() throws IOException {
    final String expectedMessage = "This is just a test failure.";
    when(mongoClient.getDatabase(any())).thenThrow(new IllegalArgumentException(expectedMessage));

    assertThrows(IllegalArgumentException.class, () -> source.discover(airbyteSourceConfig));
  }

  @Test
  void testFullRefresh() throws Exception {
    // TODO implement
  }

  @Test
  void testIncrementalRefresh() throws Exception {
    // TODO implement
  }

  private static JsonNode createConfiguration(final Optional<String> username, final Optional<String> password) {
    final Map<String, Object> config = new HashMap<>();
    final Map<String, Object> baseConfig = Map.of(
        MongoConstants.DATABASE_CONFIGURATION_KEY, DB_NAME,
        MongoConstants.CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://localhost:27017/",
        MongoConstants.AUTH_SOURCE_CONFIGURATION_KEY, "admin",
        MongoConstants.REPLICA_SET_CONFIGURATION_KEY, "replica-set");

    config.putAll(baseConfig);
    username.ifPresent(u -> config.put(MongoConstants.USER_CONFIGURATION_KEY, u));
    password.ifPresent(p -> config.put(MongoConstants.PASSWORD_CONFIGURATION_KEY, p));
    return Jsons.deserialize(Jsons.serialize(config));
  }

}
