/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.mongodb;

import static io.debezium.connector.mongodb.MongoDbConnectorConfig.REPLICA_SETS;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.mongodb.client.ChangeStreamIterable;
import com.mongodb.client.MongoChangeStreamCursor;
import com.mongodb.client.MongoClient;
import com.mongodb.client.model.changestream.ChangeStreamDocument;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.SyncMode;
import io.debezium.connector.mongodb.ResumeTokens;
import java.util.List;
import java.util.Map;
import java.util.OptionalLong;
import java.util.Properties;
import org.bson.BsonDocument;
import org.bson.BsonTimestamp;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;


class MongoDbDebeziumStateUtilTest {

  private static final String DATABASE = "test-database";

  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(List.of(
          CatalogHelpers.createAirbyteStream(
                          "test-collection",
                          DATABASE,
                          Field.of("id", JsonSchemaType.INTEGER),
                          Field.of("string", JsonSchemaType.STRING))
                  .withSupportedSyncModes(List.of(SyncMode.INCREMENTAL))
                  .withSourceDefinedPrimaryKey(List.of(List.of("_id")))));
  protected static final ConfiguredAirbyteCatalog CONFIGURED_CATALOG = CatalogHelpers.toDefaultConfiguredCatalog(CATALOG);

  private MongoDbDebeziumStateUtil mongoDbDebeziumStateUtil;

  @BeforeEach
  void setup() {
    mongoDbDebeziumStateUtil = new MongoDbDebeziumStateUtil();
  }

  @Test
  void testConstructInitialDebeziumState() {
    final String database = DATABASE;
    final String replicaSet = "test_rs";
    final String resumeToken = "8264BEB9F3000000012B0229296E04";
    final BsonDocument resumeTokenDocument = ResumeTokens.fromData(resumeToken);
    final ChangeStreamIterable changeStreamIterable = mock(ChangeStreamIterable.class);
    final MongoChangeStreamCursor<ChangeStreamDocument<BsonDocument>> mongoChangeStreamCursor =
        mock(MongoChangeStreamCursor.class);
    final MongoClient mongoClient = mock(MongoClient.class);
    final Properties baseProperties = new Properties();
    baseProperties.put("connector.class", "io.debezium.connector.mongodb.MongoDbConnector");
    baseProperties.put(REPLICA_SETS.name(), "mongodb://host:12345/?replicaSet=" + replicaSet);

    final JsonNode config = Jsons.jsonNode(Map.of(
            MongoDbDebeziumConstants.Configuration.CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://host:12345/",
            MongoDbDebeziumConstants.Configuration.DATABASE_CONFIGURATION_KEY, database,
            MongoDbDebeziumConstants.Configuration.REPLICA_SET_CONFIGURATION_KEY, replicaSet));

    when(mongoChangeStreamCursor.getResumeToken()).thenReturn(resumeTokenDocument);
    when(changeStreamIterable.cursor()).thenReturn(mongoChangeStreamCursor);
    when(mongoClient.watch(BsonDocument.class)).thenReturn(changeStreamIterable);

    final JsonNode initialState = mongoDbDebeziumStateUtil.constructInitialDebeziumState(mongoClient,
        database, replicaSet);

    assertNotNull(initialState);
    assertEquals(1, initialState.size());
    final BsonTimestamp timestamp = ResumeTokens.getTimestamp(resumeTokenDocument);
    final JsonNode offsetState = initialState.fields().next().getValue();
    assertEquals(resumeToken, Jsons.deserialize(offsetState.asText()).get(MongoDbDebeziumConstants.OffsetState.VALUE_RESUME_TOKEN).asText());
    assertEquals(timestamp.getTime(), Jsons.deserialize(offsetState.asText()).get(MongoDbDebeziumConstants.OffsetState.VALUE_SECONDS).asInt());
    assertEquals(timestamp.getInc(), Jsons.deserialize(offsetState.asText()).get(MongoDbDebeziumConstants.OffsetState.VALUE_INCREMENT).asInt());
    assertEquals("null", Jsons.deserialize(offsetState.asText()).get(MongoDbDebeziumConstants.OffsetState.VALUE_TRANSACTION_ID).asText());

    final OptionalLong parsedOffset =
            mongoDbDebeziumStateUtil.savedOffset(
                    baseProperties,
                    CONFIGURED_CATALOG,
                    initialState,
                    config);
    assertTrue(parsedOffset.isPresent());
    assertNotNull(parsedOffset.getAsLong());
    assertEquals(timestamp.getValue(), parsedOffset.getAsLong());
  }

}
