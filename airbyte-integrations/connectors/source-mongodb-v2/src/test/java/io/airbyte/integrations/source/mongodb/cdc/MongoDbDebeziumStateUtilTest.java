/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.mockStatic;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.MongoCommandException;
import com.mongodb.ServerAddress;
import com.mongodb.client.ChangeStreamIterable;
import com.mongodb.client.MongoChangeStreamCursor;
import com.mongodb.client.MongoClient;
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
import io.airbyte.protocol.models.v0.SyncMode;
import io.debezium.connector.mongodb.MongoUtils;
import io.debezium.connector.mongodb.ResumeTokens;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Properties;
import org.bson.BsonDocument;
import org.bson.BsonTimestamp;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.MockedStatic;

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

  private Properties createDebeziumProperties(String collectionIncludeList) {
    final Properties debeziumProperties = new Properties();
    debeziumProperties.setProperty("mongodb.connection.string", "mongodb://localhost:27017/");
    debeziumProperties.setProperty("collection.include.list", collectionIncludeList);
    debeziumProperties.setProperty("capture.scope", "deployment");
    debeziumProperties.setProperty("topic.prefix", "test-prefix");
    return debeziumProperties;
  }

  @Test
  void testIsResumeTokenValidSingleDb() {
    final String resumeToken = RESUME_TOKEN;
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(resumeToken);
    final MongoClient mongoClient = mock(MongoClient.class);
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> cursor = mock(MongoChangeStreamCursor.class);
    final Properties debeziumProperties = createDebeziumProperties(DATABASE + ".test-collection");

    when(changeStreamIterable.cursor()).thenReturn(cursor);

    try (MockedStatic<MongoUtils> mockedMongoUtils = mockStatic(MongoUtils.class)) {
      mockedMongoUtils.when(() -> MongoUtils.openChangeStream(any(MongoClient.class), any()))
          .thenReturn(changeStreamIterable);

      final boolean result = mongoDbDebeziumStateUtil.isValidResumeToken(resumeTokenDocument, mongoClient, debeziumProperties);
      assertTrue(result);
    }
  }

  @Test
  void testIsResumeTokenValidMultipleDb() {
    final String resumeToken = RESUME_TOKEN;
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(resumeToken);
    final MongoClient mongoClient = mock(MongoClient.class);
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> cursor = mock(MongoChangeStreamCursor.class);
    final Properties debeziumProperties = createDebeziumProperties(DATABASE + ".test-collection," + DATABASE_1 + ".test-collection-1");

    when(changeStreamIterable.cursor()).thenReturn(cursor);

    try (MockedStatic<MongoUtils> mockedMongoUtils = mockStatic(MongoUtils.class)) {
      mockedMongoUtils.when(() -> MongoUtils.openChangeStream(any(MongoClient.class), any()))
          .thenReturn(changeStreamIterable);

      final boolean result = mongoDbDebeziumStateUtil.isValidResumeToken(resumeTokenDocument, mongoClient, debeziumProperties);
      assertTrue(result);
    }
  }

  @Test
  void testIsResumeTokenInvalidSingleDb() {
    final String resumeToken = RESUME_TOKEN;
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(resumeToken);
    final MongoClient mongoClient = mock(MongoClient.class);
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final Properties debeziumProperties = createDebeziumProperties(DATABASE + ".test-collection");

    // Simulate invalid resume token - MongoDB throws MongoCommandException
    final MongoCommandException mongoException = mock(MongoCommandException.class);
    when(changeStreamIterable.cursor()).thenThrow(mongoException);

    try (MockedStatic<MongoUtils> mockedMongoUtils = mockStatic(MongoUtils.class)) {
      mockedMongoUtils.when(() -> MongoUtils.openChangeStream(any(MongoClient.class), any()))
          .thenReturn(changeStreamIterable);

      final boolean result = mongoDbDebeziumStateUtil.isValidResumeToken(resumeTokenDocument, mongoClient, debeziumProperties);
      assertFalse(result);
    }
  }

  @Test
  void testIsResumeTokenInvalidMultipleDb() {
    final String resumeToken = RESUME_TOKEN;
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(resumeToken);
    final MongoClient mongoClient = mock(MongoClient.class);
    final ChangeStreamIterable<BsonDocument> changeStreamIterable = mock(ChangeStreamIterable.class);
    final Properties debeziumProperties = createDebeziumProperties(DATABASE + ".test-collection," + DATABASE_1 + ".test-collection-1");

    // Simulate invalid resume token - MongoDB throws MongoCommandException
    final MongoCommandException mongoException = mock(MongoCommandException.class);
    when(changeStreamIterable.cursor()).thenThrow(mongoException);

    try (MockedStatic<MongoUtils> mockedMongoUtils = mockStatic(MongoUtils.class)) {
      mockedMongoUtils.when(() -> MongoUtils.openChangeStream(any(MongoClient.class), any()))
          .thenReturn(changeStreamIterable);

      final boolean result = mongoDbDebeziumStateUtil.isValidResumeToken(resumeTokenDocument, mongoClient, debeziumProperties);
      assertFalse(result);
    }
  }

}
