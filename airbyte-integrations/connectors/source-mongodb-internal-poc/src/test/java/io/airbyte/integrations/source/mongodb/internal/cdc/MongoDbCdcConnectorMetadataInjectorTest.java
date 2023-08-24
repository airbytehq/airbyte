/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.cdc;

import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcConnectorMetadataInjector.CDC_DEFAULT_CURSOR;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants;
import java.time.Instant;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import org.bson.BsonTimestamp;
import org.junit.jupiter.api.Test;

class MongoDbCdcConnectorMetadataInjectorTest {

  @Test
  void testAddingMetadata() {
    final Long emittedAtConverted = 1L;
    final BsonTimestamp expected = new BsonTimestamp(
        Long.valueOf(TimeUnit.MILLISECONDS.toSeconds(System.currentTimeMillis())).intValue(),
        1);
    final ObjectNode event = Jsons.emptyObject().withObject("");
    final Map<String, Object> sourceData = Map.of(
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_COLLECTION, "test-collection",
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_DB, "test-database",
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_TIMESTAMP_MS, TimeUnit.SECONDS.toMillis(expected.getTime()),
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_ORDER, expected.getInc());

    final MongoDbCdcConnectorMetadataInjector metadataInjector = new MongoDbCdcConnectorMetadataInjector(emittedAtConverted);
    metadataInjector.addMetaData(event, Jsons.jsonNode(sourceData));

    assertEquals(expected.getValue(), event.get(CDC_UPDATED_AT).asLong());
    assertEquals(emittedAtConverted + 1, event.get(CDC_DEFAULT_CURSOR).asLong());
  }

  @Test
  void testAddingMetadataToRowsFetchedOutsideDebezium() {
    final Long emittedAtConverted = 1L;
    final BsonTimestamp expected = new BsonTimestamp(
        Long.valueOf(TimeUnit.MILLISECONDS.toSeconds(System.currentTimeMillis())).intValue(),
        1);
    final String transactionTimestamp = Instant.now().toString();
    final ObjectNode record = Jsons.emptyObject().withObject("");

    final MongoDbCdcConnectorMetadataInjector metadataInjector = new MongoDbCdcConnectorMetadataInjector(emittedAtConverted);
    metadataInjector.addMetaDataToRowsFetchedOutsideDebezium(record, transactionTimestamp, expected);

    assertEquals(transactionTimestamp, record.get(CDC_UPDATED_AT).asText());
    assertEquals("null", record.get(CDC_DELETED_AT).asText());
    assertEquals(emittedAtConverted + 1, record.get(CDC_DEFAULT_CURSOR).asLong());
  }

  @Test
  void testGetNamespaceFromSource() {
    final String databaseName = "test-database";
    final BsonTimestamp expected = new BsonTimestamp(
        Long.valueOf(TimeUnit.MILLISECONDS.toSeconds(System.currentTimeMillis())).intValue(),
        1);
    final Map<String, Object> sourceData = Map.of(
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_COLLECTION, "test-collection",
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_DB, databaseName,
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_TIMESTAMP_MS, TimeUnit.SECONDS.toMillis(expected.getTime()),
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_ORDER, expected.getInc());

    final MongoDbCdcConnectorMetadataInjector metadataInjector = new MongoDbCdcConnectorMetadataInjector(System.currentTimeMillis());
    assertEquals(databaseName, metadataInjector.namespace(Jsons.jsonNode(sourceData)));
  }

}
