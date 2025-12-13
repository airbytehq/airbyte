/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.MongoCommandException;
import com.mongodb.ServerAddress;
import com.mongodb.client.ChangeStreamIterable;
import com.mongodb.client.MongoChangeStreamCursor;
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoDatabase;
import com.mongodb.client.model.Aggregates;
import com.mongodb.client.model.Filters;
import com.mongodb.client.model.changestream.ChangeStreamDocument;
import com.mongodb.connection.ClusterDescription;
import com.mongodb.connection.ClusterType;
import com.mongodb.connection.ServerDescription;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import io.debezium.connector.mongodb.ResumeTokens;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Properties;
import org.bson.BsonDocument;
import org.bson.BsonTimestamp;
import org.bson.conversions.Bson;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class MongoDbDebeziumStateUtilTest {

  private static final String DATABASE = "test-database";
  private static final String DATABASE_1 = "test-database-1";
  private static final String RESUME_TOKEN = "8264BEB9F3000000012B0229296E04";

  private static final AirbyteCatalog SINGLE_DB_CATALOG = new AirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createAirbyteStream(
          "test-collection",
          DATABASE,
          Field.of("id", JsonSchemaType.INTEGER),
          Field.of("string", JsonSchemaType.STRING))
          .withSupportedSyncModes(List.of(SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of("_id")))));

  protected static final ConfiguredAirbyteCatalog SINGLE_DB_CONFIGURED_CATALOG = CatalogHelpers.toDefaultConfiguredCatalog(SINGLE_DB_CATALOG);

  private static final AirbyteCatalog MULTIPLE_DB_CATALOG = new AirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createAirbyteStream(
          "test-collection",
          DATABASE,
          Field.of("id", JsonSchemaType.INTEGER),
          Field.of("string", JsonSchemaType.STRING))
          .withSupportedSyncModes(List.of(SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of("_id"))),
      CatalogHelpers.createAirbyteStream(
          "test-collection-1",
          DATABASE_1,
          Field.of("id", JsonSchemaType.INTEGER),
          Field.of("name", JsonSchemaType.STRING))
          .withSupportedSyncModes(List.of(SyncMode.INCREMENTAL))
          .withSourceDefinedPrimaryKey(List.of(List.of("_id")))));

  List<ConfiguredAirbyteStream> database1Streams = CatalogHelpers.toDefaultConfiguredCatalog(MULTIPLE_DB_CATALOG).getStreams()
      .stream().filter(stream -> stream.getStream().getNamespace().equals(DATABASE))
      .toList();

  List<ConfiguredAirbyteStream> database2Streams = CatalogHelpers.toDefaultConfiguredCatalog(MULTIPLE_DB_CATALOG).getStreams().stream()
      .filter(stream -> stream.getStream().getNamespace().equals(DATABASE_1))
      .toList();

  final List<Bson> SINGLE_DB_PIPELINE = Collections.singletonList(Aggregates.match(
      Filters.or(List.of(
          Filters.and(
              Filters.eq("ns.db", DATABASE),
              Filters.in("ns.coll", List.of("test-collection")))))));

  private final List<Bson> MULTIPLE_DB_PIPELINE = Collections.singletonList(Aggregates.match(
      Filters.or(List.of(
          Filters.and(
              Filters.eq("ns.db", DATABASE),
              Filters.in("ns.coll", List.of("test-collection"))),
          Filters.and(
              Filters.eq("ns.db", DATABASE_1),
              Filters.in("ns.coll", "test-collection-1"))))));

  private MongoDbDebeziumStateUtil mongoDbDebeziumStateUtil;

  @BeforeEach
  void setup() {
    mongoDbDebeziumStateUtil = new MongoDbDebeziumStateUtil();
  }

  @Test
  void testConstructInitialDebeziumState() {
    final String database = DATABASE;
    final String resumeToken = RESUME_TOKEN;
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(resumeToken);
    final ServerDescription serverDescription = mock(ServerDescription.class);
    final ClusterDescription clusterDescription = mock(ClusterDescription.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final Properties baseProperties = new Properties();

    final JsonNode config = Jsons.jsonNode(Map.of(
        MongoDbDebeziumConstants.Configuration.CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://host:12345/",
        MongoDbDebeziumConstants.Configuration.DATABASE_CONFIGURATION_KEY, database));

    when(clusterDescription.getServerDescriptions()).thenReturn(List.of(serverDescription));
    when(clusterDescription.getType()).thenReturn(ClusterType.REPLICA_SET);
    when(mongoClient.getClusterDescription()).thenReturn(clusterDescription);

    final JsonNode initialState = mongoDbDebeziumStateUtil.constructInitialDebeziumState(resumeTokenDocument,
        config.get(MongoDbDebeziumConstants.Configuration.CONNECTION_STRING_CONFIGURATION_KEY).asText());

    assertNotNull(initialState);
    assertEquals(1, initialState.size());
    final BsonTimestamp timestamp = ResumeTokens.getTimestamp(resumeTokenDocument);
    final JsonNode offsetState = initialState.fields().next().getValue();
    assertEquals(resumeToken, Jsons.deserialize(offsetState.asText()).get(MongoDbDebeziumConstants.OffsetState.VALUE_RESUME_TOKEN).asText());
    assertEquals(timestamp.getTime(), Jsons.deserialize(offsetState.asText()).get(MongoDbDebeziumConstants.OffsetState.VALUE_SECONDS).asInt());
    assertEquals(timestamp.getInc(), Jsons.deserialize(offsetState.asText()).get(MongoDbDebeziumConstants.OffsetState.VALUE_INCREMENT).asInt());

    final Optional<BsonDocument> parsedOffset =
        mongoDbDebeziumStateUtil.savedOffset(
            baseProperties,
            SINGLE_DB_CONFIGURED_CATALOG,
            initialState,
            config);
    assertTrue(parsedOffset.isPresent());
    assertEquals(resumeToken, parsedOffset.get().get("_data").asString().getValue());
  }

  @Test
  void testOffsetDataFormat() {
    final JsonNode offsetState = MongoDbDebeziumStateUtil.formatState("mongodb://host:12345/", RESUME_TOKEN);

    assertNotNull(offsetState);
    final String expectedNormalized = MongoDbDebeziumPropertiesManager.normalizeToDebeziumFormat("mongodb://host:12345/");
    assertEquals("[\"" + expectedNormalized + "\",{\""
        + MongoDbDebeziumConstants.OffsetState.KEY_SERVER_ID + "\":\"" + expectedNormalized + "\"}]", offsetState.fieldNames().next());
  }

  @Test
  void testIsResumeTokenValidSingleDb() {
    final BsonDocument resumeToken = ResumeTokens.fromData(RESUME_TOKEN);

    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);

    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeToken);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);
    when(changeStreamIterable.resumeAfter(resumeToken)).thenReturn(changeStreamIterable);
    when(mongoClient.getDatabase(DATABASE)).thenReturn(mongoDatabase);
    when(mongoDatabase.watch(SINGLE_DB_PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);
    assertTrue(
        mongoDbDebeziumStateUtil.isValidResumeToken(resumeToken, mongoClient, List.of(DATABASE), List.of(SINGLE_DB_CONFIGURED_CATALOG.getStreams())));
  }

  @Test
  void testIsResumeTokenValidMultipleDb() {
    final BsonDocument resumeToken = ResumeTokens.fromData(RESUME_TOKEN);

    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);

    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeToken);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);
    when(changeStreamIterable.resumeAfter(resumeToken)).thenReturn(changeStreamIterable);
    when(mongoClient.watch(MULTIPLE_DB_PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);
    assertTrue(mongoDbDebeziumStateUtil.isValidResumeToken(resumeToken, mongoClient, List.of(DATABASE, DATABASE_1),
        List.of(database1Streams, database2Streams)));
  }

  @Test
  void testIsResumeTokenInvalidSingleDb() {
    final BsonDocument resumeToken = ResumeTokens.fromData(RESUME_TOKEN);

    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);

    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);

    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeToken);
    when(changeStreamIterable.cursor()).thenThrow(new MongoCommandException(new BsonDocument(), new ServerAddress()));
    when(changeStreamIterable.resumeAfter(resumeToken)).thenReturn(changeStreamIterable);
    when(mongoClient.getDatabase(DATABASE)).thenReturn(mongoDatabase);
    when(mongoDatabase.watch(SINGLE_DB_PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);
    assertFalse(
        mongoDbDebeziumStateUtil.isValidResumeToken(resumeToken, mongoClient, List.of(DATABASE), List.of(SINGLE_DB_CONFIGURED_CATALOG.getStreams())));
  }

  @Test
  void testIsResumeTokenInvalidMultipleDb() {
    final BsonDocument resumeToken = ResumeTokens.fromData(RESUME_TOKEN);

    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);

    final MongoClient mongoClient = mock(MongoClient.class);
    final MongoDatabase mongoDatabase = mock(MongoDatabase.class);

    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeToken);
    when(changeStreamIterable.cursor()).thenThrow(new MongoCommandException(new BsonDocument(), new ServerAddress()));
    when(changeStreamIterable.resumeAfter(resumeToken)).thenReturn(changeStreamIterable);
    when(mongoClient.watch(MULTIPLE_DB_PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);
    when(mongoClient.watch(MULTIPLE_DB_PIPELINE, BsonDocument.class)).thenReturn(changeStreamIterable);
    assertFalse(mongoDbDebeziumStateUtil.isValidResumeToken(resumeToken, mongoClient, List.of(DATABASE, DATABASE_1),
        List.of(database1Streams, database2Streams)));
  }

}
