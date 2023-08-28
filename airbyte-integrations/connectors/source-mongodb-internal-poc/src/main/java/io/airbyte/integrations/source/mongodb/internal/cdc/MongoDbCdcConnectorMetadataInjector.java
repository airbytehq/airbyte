/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.cdc;

import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.integrations.debezium.CdcMetadataInjector;
import io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants;
import java.time.Instant;
import java.util.concurrent.atomic.AtomicLong;

/**
 * MongoDB specific implementation of the {@link CdcMetadataInjector} that stores cursor information
 * for MongoDB source event data.
 */
public class MongoDbCdcConnectorMetadataInjector implements CdcMetadataInjector {

  static final String CDC_DEFAULT_CURSOR = "_ab_cdc_cursor";

  private final long emittedAtConverted;

  // This now makes this class stateful. Please make sure to use the same instance within a sync
  private final AtomicLong recordCounter = new AtomicLong(1);
  private static final long ONE_HUNDRED_MILLION = 100_000_000;
  private static MongoDbCdcConnectorMetadataInjector mongoDbCdcConnectorMetadataInjector;

  private MongoDbCdcConnectorMetadataInjector(final Instant emittedAt) {
    this.emittedAtConverted = emittedAt.getEpochSecond() * ONE_HUNDRED_MILLION;
  }

  public static MongoDbCdcConnectorMetadataInjector getInstance(final Instant emittedAt) {
    if (mongoDbCdcConnectorMetadataInjector == null) {
      mongoDbCdcConnectorMetadataInjector = new MongoDbCdcConnectorMetadataInjector(emittedAt);
    }

    return mongoDbCdcConnectorMetadataInjector;
  }

  @Override
  public void addMetaData(final ObjectNode event, final JsonNode source) {
    event.put(CDC_DEFAULT_CURSOR, getCdcDefaultCursor());
  }

  @Override
  public void addMetaDataToRowsFetchedOutsideDebezium(final ObjectNode record, final String transactionTimestamp, final Object ignored) {
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
