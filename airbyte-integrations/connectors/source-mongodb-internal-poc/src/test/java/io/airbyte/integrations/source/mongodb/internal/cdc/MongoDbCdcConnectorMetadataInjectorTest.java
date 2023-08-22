/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.cdc;

import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_LSN;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

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
    final BsonTimestamp expected = new BsonTimestamp(
        Long.valueOf(TimeUnit.MILLISECONDS.toSeconds(System.currentTimeMillis())).intValue(),
        1);
    final ObjectNode event = mock(ObjectNode.class);
    final Map<String, Object> sourceData = Map.of(
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_COLLECTION, "test-collection",
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_DB, "test-database",
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_TIMESTAMP_MS, TimeUnit.SECONDS.toMillis(expected.getTime()),
        MongoDbDebeziumConstants.ChangeEvent.SOURCE_ORDER, expected.getInc());

    final MongoDbCdcConnectorMetadataInjector metadataInjector = new MongoDbCdcConnectorMetadataInjector();
    metadataInjector.addMetaData(event, Jsons.jsonNode(sourceData));

    verify(event, times(1)).put(CDC_LSN, expected.getValue());
  }

  @Test
  void testAddingMetadataToRowsFetchedOutsideDebezium() {
    final BsonTimestamp expected = new BsonTimestamp(
        Long.valueOf(TimeUnit.MILLISECONDS.toSeconds(System.currentTimeMillis())).intValue(),
        1);
    final String transactionTimestamp = Instant.now().toString();
    final ObjectNode record = mock(ObjectNode.class);

    final MongoDbCdcConnectorMetadataInjector metadataInjector = new MongoDbCdcConnectorMetadataInjector();
    metadataInjector.addMetaDataToRowsFetchedOutsideDebezium(record, transactionTimestamp, expected);

    verify(record, times(1)).put(CDC_UPDATED_AT, transactionTimestamp);
    verify(record, times(1)).put(CDC_LSN, expected.getValue());
    verify(record, times(1)).put(CDC_DELETED_AT, (String) null);
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

    final MongoDbCdcConnectorMetadataInjector metadataInjector = new MongoDbCdcConnectorMetadataInjector();
    assertEquals(databaseName, metadataInjector.namespace(Jsons.jsonNode(sourceData)));
  }

}
