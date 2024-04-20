/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_DELETED_AT;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_UPDATED_AT;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import java.lang.reflect.Field;
import java.time.Instant;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import org.bson.BsonTimestamp;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class MongoDbCdcConnectorMetadataInjectorTest {

  @BeforeEach
  public void reset() throws NoSuchFieldException, IllegalAccessException {
    Field instance = MongoDbCdcConnectorMetadataInjector.class.getDeclaredField("mongoDbCdcConnectorMetadataInjector");
    instance.setAccessible(true);
    instance.set(null, null);
  }

  @Test
  void testAddingMetadata() {
    final Instant emittedAt = Instant.now();
    final BsonTimestamp expected = new BsonTimestamp(
        Long.valueOf(TimeUnit.MILLISECONDS.toSeconds(System.currentTimeMillis())).intValue(),
        1);
    final ObjectNode event = Jsons.emptyObject().withObject("");
    final Map<String, Object> sourceData = Map.of(
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_COLLECTION, "test-collection",
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_DB, "test-database",
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_TIMESTAMP_MS, TimeUnit.SECONDS.toMillis(expected.getTime()),
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_ORDER, expected.getInc());

    final MongoDbCdcConnectorMetadataInjector metadataInjector = MongoDbCdcConnectorMetadataInjector.getInstance(emittedAt);
    metadataInjector.addMetaData(event, Jsons.jsonNode(sourceData));

    assertEquals((emittedAt.getEpochSecond() * 100_000_000) + 1L, event.get(MongoDbCdcConnectorMetadataInjector.CDC_DEFAULT_CURSOR).asLong());
  }

  @Test
  void testAddingMetadataToRowsFetchedOutsideDebezium() {
    final Instant emittedAt = Instant.now();
    final BsonTimestamp expected = new BsonTimestamp(
        Long.valueOf(TimeUnit.MILLISECONDS.toSeconds(System.currentTimeMillis())).intValue(),
        1);
    final String transactionTimestamp = Instant.now().toString();
    final ObjectNode record = Jsons.emptyObject().withObject("");

    final MongoDbCdcConnectorMetadataInjector metadataInjector = MongoDbCdcConnectorMetadataInjector.getInstance(emittedAt);
    metadataInjector.addMetaDataToRowsFetchedOutsideDebezium(record, transactionTimestamp, expected);

    assertEquals(transactionTimestamp, record.get(CDC_UPDATED_AT).asText());
    assertEquals("null", record.get(CDC_DELETED_AT).asText());
    assertEquals((emittedAt.getEpochSecond() * 100_000_000) + 1L, record.get(MongoDbCdcConnectorMetadataInjector.CDC_DEFAULT_CURSOR).asLong());
  }

  @Test
  void testGetNamespaceFromSource() {
    final Instant emittedAt = Instant.now();
    final String databaseName = "test-database";
    final BsonTimestamp expected = new BsonTimestamp(
        Long.valueOf(TimeUnit.MILLISECONDS.toSeconds(System.currentTimeMillis())).intValue(),
        1);
    final Map<String, Object> sourceData = Map.of(
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_COLLECTION, "test-collection",
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_DB, databaseName,
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_TIMESTAMP_MS, TimeUnit.SECONDS.toMillis(expected.getTime()),
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_ORDER, expected.getInc());

    final MongoDbCdcConnectorMetadataInjector metadataInjector = MongoDbCdcConnectorMetadataInjector.getInstance(emittedAt);

    assertEquals(databaseName, metadataInjector.namespace(Jsons.jsonNode(sourceData)));
  }

}
