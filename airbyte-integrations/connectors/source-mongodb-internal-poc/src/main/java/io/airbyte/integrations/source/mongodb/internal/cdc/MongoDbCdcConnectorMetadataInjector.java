/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.cdc;

import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_LSN;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.integrations.debezium.CdcMetadataInjector;
import io.airbyte.integrations.debezium.internals.DebeziumEventUtils;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbResumeTokenHelper;
import org.bson.BsonTimestamp;

/**
 * MongoDB specific implementation of the {@link CdcMetadataInjector} that stores the MongoDB resume
 * token timestamp in the {@link DebeziumEventUtils#CDC_LSN} metadata field.
 */
public class MongoDbCdcConnectorMetadataInjector implements CdcMetadataInjector<BsonTimestamp> {

  @Override
  public void addMetaData(final ObjectNode event, final JsonNode source) {
    final BsonTimestamp timestamp = MongoDbResumeTokenHelper.extractTimestampFromSource(source);
    event.put(CDC_LSN, timestamp.getValue());
  }

  @Override
  public void addMetaDataToRowsFetchedOutsideDebezium(final ObjectNode record, final String transactionTimestamp, final BsonTimestamp metadataToAdd) {
    record.put(CDC_UPDATED_AT, transactionTimestamp);
    record.put(CDC_LSN, metadataToAdd.getValue());
    record.put(CDC_DELETED_AT, (String) null);
  }

  @Override
  public String namespace(final JsonNode source) {
    return source.get(MongoDbDebeziumConstants.ChangeEvent.SOURCE_DB).asText();
  }

  @Override
  public String name(JsonNode source) {
    return source.get(MongoDbDebeziumConstants.ChangeEvent.SOURCE_COLLECTION).asText();
  }

}
