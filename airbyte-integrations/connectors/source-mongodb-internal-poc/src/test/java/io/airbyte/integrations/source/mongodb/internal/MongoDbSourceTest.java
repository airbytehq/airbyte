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
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
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
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;
import org.bson.Document;
import org.bson.types.ObjectId;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class MongoDbSourceTest {

  private static final String DB_NAME = "airbyte_test";

  private static final String CURSOR_FIELD = "_id";
  private static final String NAME_FIELD = "name";

  private static final String COLLECTION1 = "collection1";
  private static final String COLLECTION2 = "collection2";
  private static final String COLLECTION3 = "collection3";

  private static final ObjectId OBJECT_ID1 = new ObjectId("64c0029d95ad260d69ef28a1");

  private static final String NAME1 = "name1";

  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createAirbyteStream(
              COLLECTION1,
              "database",
              Field.of(CURSOR_FIELD, JsonSchemaType.STRING),
              Field.of(NAME_FIELD, JsonSchemaType.STRING))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.INCREMENTAL)),
      CatalogHelpers.createAirbyteStream(
              COLLECTION2,
              "database",
              Field.of(CURSOR_FIELD, JsonSchemaType.STRING))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.INCREMENTAL)),
      CatalogHelpers.createAirbyteStream(
              COLLECTION3,
              "database",
              Field.of(CURSOR_FIELD, JsonSchemaType.STRING),
              Field.of(NAME_FIELD, JsonSchemaType.STRING))
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH))));

  private static final ConfiguredAirbyteCatalog CONFIGURED_CATALOG = toConfiguredCatalog(CATALOG);

  @Nested
  @DisplayName("Tests with mocked database")
  class MockedDatabaseTests {

    private JsonNode airbyteSourceConfig;
    private MongoClient mongoClient;
    private MongoDbSource source;

    @BeforeEach
    void setup() {
      airbyteSourceConfig = createConfiguration("mongodb://localhost:27017/", Optional.of("replica-set"), Optional.empty(), Optional.empty());
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
    void testDiscoverOperationWithUnexpectedFailure() {
      final String expectedMessage = "This is just a test failure.";
      when(mongoClient.getDatabase(any())).thenThrow(new IllegalArgumentException(expectedMessage));

      assertThrows(IllegalArgumentException.class, () -> source.discover(airbyteSourceConfig));
    }

    @Test
    void testConvertState() {
      final var state1 = Jsons.deserialize(
          "[{\"type\":\"STREAM\",\"stream\":{\"stream_descriptor\":{\"name\":\"test.acceptance_test1\"},\"stream_state\":{\"id\":\"64c0029d95ad260d69ef28a2\"}}}]");
      final var actual = source.convertState(state1);
      assertTrue(actual.containsKey("test.acceptance_test1"), "missing test.acceptance_test1");
      assertEquals("64c0029d95ad260d69ef28a2", actual.get("test.acceptance_test1").id(), "id value does not match");
    }

    @Test
    void testReadKeepsMongoClientOpen() {
      final MongoClient mongoClient = mock(MongoClient.class);
      doReturn(mongoClient).when(source).createMongoClient(airbyteSourceConfig);
      final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
      when(mongoClient.getDatabase(any())).thenReturn(mongoDatabase);
      final MongoCursor<Document> mongoCursor = mock(MongoCursor.class);
      doReturn(mongoCursor).when(source).getRecords(any(), any(), any(), any(), any());

      when(mongoCursor.hasNext()).thenReturn(true, false);
      when(mongoCursor.next()).thenReturn(
          new Document(Map.of(
              CURSOR_FIELD, OBJECT_ID1,
              NAME_FIELD, NAME1)));
      source.read(airbyteSourceConfig, CONFIGURED_CATALOG, null);
      verify(mongoClient, never()).close();
    }

    @Test
    void testReadClosesMongoClient() {
      final MongoClient mongoClient = mock(MongoClient.class);
      doReturn(mongoClient).when(source).createMongoClient(airbyteSourceConfig);
      when(mongoClient.getDatabase(any())).thenThrow(new RuntimeException());
      assertThrows(RuntimeException.class, () -> source.read(airbyteSourceConfig, CONFIGURED_CATALOG, null));
      verify(mongoClient, times(1)).close();
    }
  }

  private static JsonNode createConfiguration(
      final String connectionString,
      final Optional<String> replicaSet,
      final Optional<String> username,
      final Optional<String> password) {
    final Map<String, Object> config = new HashMap<>();
    final Map<String, Object> baseConfig = Map.of(
        MongoConstants.DATABASE_CONFIGURATION_KEY, DB_NAME,
        MongoConstants.CONNECTION_STRING_CONFIGURATION_KEY, connectionString,
        MongoConstants.AUTH_SOURCE_CONFIGURATION_KEY, "admin");

    config.putAll(baseConfig);
    replicaSet.ifPresent( r -> config.put(MongoConstants.REPLICA_SET_CONFIGURATION_KEY, r));
    username.ifPresent(u -> config.put(MongoConstants.USER_CONFIGURATION_KEY, u));
    password.ifPresent(p -> config.put(MongoConstants.PASSWORD_CONFIGURATION_KEY, p));
    return Jsons.deserialize(Jsons.serialize(config));
  }

  private static ConfiguredAirbyteCatalog toConfiguredCatalog(final AirbyteCatalog catalog) {
    return new ConfiguredAirbyteCatalog()
        .withStreams(catalog.getStreams()
            .stream()
            .map(MongoDbSourceTest::toConfiguredStreams)
            .flatMap(List::stream)
            .toList());
  }

  private static List<ConfiguredAirbyteStream> toConfiguredStreams(final AirbyteStream stream) {
    return stream.getSupportedSyncModes().stream().map(syncMode -> new ConfiguredAirbyteStream()
        .withStream(stream)
        .withSyncMode(syncMode)
        .withCursorField(List.of(CURSOR_FIELD))
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
        .withPrimaryKey(new ArrayList<>())).collect(Collectors.toList());
  }
}
