/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.core.type.TypeReference;
import com.mongodb.client.AggregateIterable;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.bson.Document;
import org.junit.jupiter.api.Test;

public class MongoUtilTest {

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
    final List<Document> schemaDiscoveryResponses = schemaDiscoveryJsonResponses.stream().map(s -> new Document(s)).collect(Collectors.toList());

    when(cursor.hasNext()).thenReturn(true, true, false);
    when(cursor.next()).thenReturn(schemaDiscoveryResponses.get(0), schemaDiscoveryResponses.get(1));
    when(aggregateIterable.cursor()).thenReturn(cursor);
    when(mongoCollection.aggregate(any())).thenReturn(aggregateIterable);
    when(mongoDatabase.getCollection(any())).thenReturn(mongoCollection);
    when(mongoDatabase.runCommand(any())).thenReturn(authorizedCollectionsResponse);
    when(mongoClient.getDatabase(databaseName)).thenReturn(mongoDatabase);

    final List<AirbyteStream> streams = MongoUtil.getAirbyteStreams(mongoClient, databaseName);
    assertNotNull(streams);
    assertEquals(1, streams.size());
    assertEquals(11, streams.get(0).getJsonSchema().get("properties").size());
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
    final List<Document> schemaDiscoveryResponses = schemaDiscoveryJsonResponses.stream().map(s -> new Document(s)).collect(Collectors.toList());

    when(cursor.hasNext()).thenReturn(true, true, false);
    when(cursor.next()).thenReturn(schemaDiscoveryResponses.get(0), schemaDiscoveryResponses.get(1));
    when(aggregateIterable.cursor()).thenReturn(cursor);
    when(mongoCollection.aggregate(any())).thenReturn(aggregateIterable);
    when(mongoDatabase.getCollection(any())).thenReturn(mongoCollection);
    when(mongoDatabase.runCommand(any())).thenReturn(authorizedCollectionsResponse);
    when(mongoClient.getDatabase(databaseName)).thenReturn(mongoDatabase);

    final List<AirbyteStream> streams = MongoUtil.getAirbyteStreams(mongoClient, databaseName);
    assertNotNull(streams);
    assertEquals(1, streams.size());
    assertEquals(11, streams.get(0).getJsonSchema().get("properties").size());
    assertEquals(JsonSchemaType.NUMBER.getJsonSchemaTypeMap().get("type"),
        streams.get(0).getJsonSchema().get("properties").get("total").get("type").asText());
  }

}
