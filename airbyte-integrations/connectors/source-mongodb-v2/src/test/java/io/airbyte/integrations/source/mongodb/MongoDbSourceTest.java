/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import static io.airbyte.integrations.source.mongodb.MongoCatalogHelper.DEFAULT_CURSOR_FIELD;
import static io.airbyte.integrations.source.mongodb.MongoConstants.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyBoolean;
import static org.mockito.Mockito.*;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.MongoCredential;
import com.mongodb.MongoSecurityException;
import com.mongodb.client.*;
import com.mongodb.connection.ClusterDescription;
import com.mongodb.connection.ClusterType;
import io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcInitializer;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.util.*;
import org.bson.BsonDocument;
import org.bson.Document;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class MongoDbSourceTest {

  private static final String DB_NAME = "airbyte_test";

  private JsonNode airbyteSourceConfig;
  private JsonNode airbyteSourceConfigWithoutSchema;
  private MongoDbSourceConfig sourceConfig;
  private MongoClient mongoClient;
  private MongoDbCdcInitializer cdcInitializer;
  private MongoDbSource source;

  @BeforeEach
  void setup() {
    airbyteSourceConfig = createConfiguration(Optional.empty(), Optional.empty(), true);
    airbyteSourceConfigWithoutSchema = createConfiguration(Optional.empty(), Optional.empty(), false);

    sourceConfig = new MongoDbSourceConfig(airbyteSourceConfig);
    mongoClient = mock(MongoClient.class);
    cdcInitializer = mock(MongoDbCdcInitializer.class);
    source = spy(new MongoDbSource(cdcInitializer));
    final MongoIterable<String> iterable = mock(MongoIterable.class);

    when(iterable.spliterator()).thenReturn(List.of(DB_NAME).spliterator());
    when(mongoClient.listDatabaseNames()).thenReturn(iterable);
    doReturn(mongoClient).when(source).createMongoClient(sourceConfig);
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
  void testCheckOperationMissingDatabase() throws IOException {
    final ClusterDescription clusterDescription = mock(ClusterDescription.class);
    final Document response = Document.parse(MoreResources.readResource("authorized_collections_response.json"));
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);
    final MongoIterable<String> iterable = mock(MongoIterable.class);

    when(iterable.spliterator()).thenReturn(List.of("other").spliterator());
    when(mongoClient.listDatabaseNames()).thenReturn(iterable);

    when(clusterDescription.getType()).thenReturn(ClusterType.REPLICA_SET);
    when(mongoDatabase.runCommand(any())).thenReturn(response);
    when(mongoClient.getDatabase(any())).thenReturn(mongoDatabase);
    when(mongoClient.getClusterDescription()).thenReturn(clusterDescription);

    final AirbyteConnectionStatus airbyteConnectionStatus = source.check(airbyteSourceConfig);
    assertNotNull(airbyteConnectionStatus);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, airbyteConnectionStatus.getStatus());
  }

  @Test
  void testCheckOperationWithMissingConfiguration() throws IOException {
    final ClusterDescription clusterDescription = mock(ClusterDescription.class);
    final Document response = Document.parse(MoreResources.readResource("authorized_collections_response.json"));
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);

    when(clusterDescription.getType()).thenReturn(ClusterType.REPLICA_SET);
    when(mongoDatabase.runCommand(any())).thenReturn(response);
    when(mongoClient.getDatabase(any())).thenReturn(mongoDatabase);
    when(mongoClient.getClusterDescription()).thenReturn(clusterDescription);

    final AirbyteConnectionStatus airbyteConnectionStatus = source.check(Jsons.jsonNode(Map.of()));
    assertNotNull(airbyteConnectionStatus);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, airbyteConnectionStatus.getStatus());
    assertEquals("Unable to perform connection check operation: Database configuration is missing required 'database_config' property.",
        airbyteConnectionStatus.getMessage());
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
  void testCheckOperationAuthenticationFailure() {
    final ClusterDescription clusterDescription = mock(ClusterDescription.class);

    when(clusterDescription.getType()).thenReturn(ClusterType.REPLICA_SET);
    when(mongoClient.getDatabase(any())).thenThrow(new MongoSecurityException(
        MongoCredential.createCredential("username", DB_NAME, "password".toCharArray()), "test"));
    when(mongoClient.getClusterDescription()).thenReturn(clusterDescription);

    final AirbyteConnectionStatus airbyteConnectionStatus = source.check(airbyteSourceConfig);
    assertNotNull(airbyteConnectionStatus);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, airbyteConnectionStatus.getStatus());
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
    final List<Document> schemaDiscoveryResponses = schemaDiscoveryJsonResponses.stream().map(Document::new).toList();
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
    when(aggregateIterable.allowDiskUse(anyBoolean())).thenReturn(aggregateIterable);

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
        stream.get().getJsonSchema().get("properties").get(DEFAULT_CURSOR_FIELD).get("type").asText());
    assertEquals(JsonSchemaType.STRING.getJsonSchemaTypeMap().get("type"),
        stream.get().getJsonSchema().get("properties").get(DebeziumEventConverter.CDC_DELETED_AT).get("type").asText());
    assertEquals(JsonSchemaType.STRING.getJsonSchemaTypeMap().get("type"),
        stream.get().getJsonSchema().get("properties").get(DebeziumEventConverter.CDC_UPDATED_AT).get("type").asText());
    assertEquals(true, stream.get().getSourceDefinedCursor());
    assertEquals(List.of(DEFAULT_CURSOR_FIELD), stream.get().getDefaultCursorField());
    assertEquals(List.of(List.of(MongoCatalogHelper.DEFAULT_PRIMARY_KEY)), stream.get().getSourceDefinedPrimaryKey());
    assertEquals(MongoCatalogHelper.SUPPORTED_SYNC_MODES, stream.get().getSupportedSyncModes());
    assertEquals(true, stream.get().getIsResumable());
  }

  @Test
  void testDiscoverOperationWithMissingConfiguration() throws IOException {
    final AggregateIterable<Document> aggregateIterable = mock(AggregateIterable.class);
    final List<Map<String, Object>> schemaDiscoveryJsonResponses =
        Jsons.deserialize(MoreResources.readResource("schema_discovery_response.json"), new TypeReference<>() {});
    final List<Document> schemaDiscoveryResponses = schemaDiscoveryJsonResponses.stream().map(Document::new).toList();
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

    assertThrows(IllegalArgumentException.class, () -> source.discover(Jsons.jsonNode(Map.of())));
  }

  @Test
  void testDiscoverOperationWithUnexpectedFailure() {
    final String expectedMessage = "This is just a test failure.";
    when(mongoClient.getDatabase(any())).thenThrow(new IllegalArgumentException(expectedMessage));

    assertThrows(IllegalArgumentException.class, () -> source.discover(airbyteSourceConfig));
  }

  @Test
  void testReadClosesMongoClient() {
    final MongoClient mongoClient = mock(MongoClient.class);
    doReturn(mongoClient).when(source).createMongoClient(sourceConfig);
    when(cdcInitializer.createCdcIterators(any(), any(), any(), any(), any(), any())).thenThrow(new RuntimeException());
    assertThrows(RuntimeException.class, () -> source.read(airbyteSourceConfig, null, null));
    verify(mongoClient, times(1)).close();
  }

  @Test
  void testReadWithMissingConfiguration() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final JsonNode state = mock(JsonNode.class);
    assertThrows(IllegalArgumentException.class, () -> source.read(Jsons.jsonNode(Map.of()), catalog, state));
  }

  @Test
  void testReadKeepsMongoClientOpen() {
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor mongoChangeStreamCursor = mock(MongoChangeStreamCursor.class);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);
    when(mongoClient.watch(BsonDocument.class)).thenReturn(changeStreamIterable);
    when(cdcInitializer.createCdcIterators(any(), any(), any(), any(), any(), any())).thenReturn(Collections.emptyList());
    source.read(airbyteSourceConfigWithoutSchema, new ConfiguredAirbyteCatalog(), null);
    verify(mongoClient, never()).close();
  }

  private static JsonNode createConfiguration(final Optional<String> username, final Optional<String> password, final boolean isSchemaEnforced) {
    final Map<String, Object> baseConfig = Map.of(
        MongoConstants.DATABASE_CONFIGURATION_KEY, DB_NAME,
        MongoConstants.CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://localhost:27017/",
        MongoConstants.AUTH_SOURCE_CONFIGURATION_KEY, "admin",
        MongoConstants.DISCOVER_SAMPLE_SIZE_CONFIGURATION_KEY, DEFAULT_DISCOVER_SAMPLE_SIZE,
        SCHEMA_ENFORCED_CONFIGURATION_KEY, isSchemaEnforced);

    final Map<String, Object> config = new HashMap<>(baseConfig);
    username.ifPresent(u -> config.put(MongoConstants.USERNAME_CONFIGURATION_KEY, u));
    password.ifPresent(p -> config.put(MongoConstants.PASSWORD_CONFIGURATION_KEY, p));
    return Jsons.deserialize(Jsons.serialize(Map.of(DATABASE_CONFIG_CONFIGURATION_KEY, config)));
  }

}
