/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.cdc;

import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.integrations.debezium.CdcMetadataInjector;
import io.airbyte.integrations.debezium.internals.DebeziumEventUtils;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbResumeTokenHelper;
import org.bson.BsonTimestamp;

import java.util.concurrent.atomic.AtomicLong;

/**
 * MongoDB specific implementation of the {@link CdcMetadataInjector} that stores the MongoDB resume
 * token timestamp in the {@link DebeziumEventUtils#CDC_LSN} metadata field.
 */
public class MongoDbCdcConnectorMetadataInjector implements CdcMetadataInjector<BsonTimestamp> {

  static final String CDC_DEFAULT_CURSOR = "_ab_cdc_cursor";

  private final long emittedAtConverted;

  // This now makes this class stateful. Please make sure to use the same instance within a sync
  private final AtomicLong recordCounter = new AtomicLong(1);

  public MongoDbCdcConnectorMetadataInjector(long emittedAtConverted) {
    this.emittedAtConverted = emittedAtConverted;
  }

  @Override
  public void addMetaData(final ObjectNode event, final JsonNode source) {
    final BsonTimestamp timestamp = MongoDbResumeTokenHelper.extractTimestampFromSource(source);
    event.put(CDC_UPDATED_AT, timestamp.getValue());
    event.put(CDC_DEFAULT_CURSOR, getCdcDefaultCursor());
  }

  @Override
  public void addMetaDataToRowsFetchedOutsideDebezium(final ObjectNode record, final String transactionTimestamp, final BsonTimestamp metadataToAdd) {
    record.put(CDC_UPDATED_AT, transactionTimestamp);
    record.put(CDC_DELETED_AT, (String) null);
    record.put(CDC_DEFAULT_CURSOR, getCdcDefaultCursor());
  }

  @Override
  public String namespace(final JsonNode source) {
    return source.get(MongoDbDebeziumConstants.ChangeEvent.SOURCE_DB).asText();
  }

  @Override
  public String name(JsonNode source) {
    return source.get(MongoDbDebeziumConstants.ChangeEvent.SOURCE_COLLECTION).asText();
  }

  private Long getCdcDefaultCursor() {
    return this.emittedAtConverted + this.recordCounter.getAndIncrement();
  }
}
