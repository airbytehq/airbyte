/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.cdc;

import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_DELETED_AT;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_UPDATED_AT;
import static io.airbyte.integrations.source.mysql.MySqlSource.CDC_DEFAULT_CURSOR;
import static io.airbyte.integrations.source.mysql.MySqlSource.CDC_LOG_FILE;
import static io.airbyte.integrations.source.mysql.MySqlSource.CDC_LOG_POS;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.integrations.debezium.CdcMetadataInjector;
import io.airbyte.integrations.source.mysql.cdc.MySqlDebeziumStateUtil.MysqlDebeziumStateAttributes;
import java.time.Instant;
import java.util.concurrent.atomic.AtomicLong;

public class MySqlCdcConnectorMetadataInjector implements CdcMetadataInjector<MysqlDebeziumStateAttributes> {

  private final Instant emittedAt;
  final MysqlDebeziumStateAttributes debeziumStateAttributes;

  // This now makes this class stateful. Please make sure to use the same instance within a sync
  private final AtomicLong recordCounter = new AtomicLong(1);
  private static final long ONE_HUNDRED_MILLION = 100_000_000;
  private static MySqlCdcConnectorMetadataInjector mySqlCdcConnectorMetadataInjector;

  private MySqlCdcConnectorMetadataInjector(final Instant emittedAt, final MysqlDebeziumStateAttributes stateAttributes) {
    this.emittedAt = emittedAt;
    this.debeziumStateAttributes = stateAttributes;
  }

  public static MySqlCdcConnectorMetadataInjector getInstance(final Instant emittedAt, final MysqlDebeziumStateAttributes stateAttributes) {
    if (mySqlCdcConnectorMetadataInjector == null) {
      mySqlCdcConnectorMetadataInjector = new MySqlCdcConnectorMetadataInjector(emittedAt, stateAttributes);
    }

    return mySqlCdcConnectorMetadataInjector;
  }

  @Override
  public void addMetaData(final ObjectNode event, final JsonNode source) {
    event.put(CDC_LOG_FILE, source.get("file").asText());
    event.put(CDC_LOG_POS, source.get("pos").asLong());
    event.put(CDC_DEFAULT_CURSOR, getCdcDefaultCursor());
  }

  @Override
  public void addMetaDataToRowsFetchedOutsideDebezium(final ObjectNode record) {
    record.put(CDC_UPDATED_AT, emittedAt.toString());
    record.put(CDC_LOG_FILE, debeziumStateAttributes.binlogFilename());
    record.put(CDC_LOG_POS, debeziumStateAttributes.binlogPosition());
    record.put(CDC_DELETED_AT, (String) null);
    record.put(CDC_DEFAULT_CURSOR, getCdcDefaultCursor());
  }

  @Override
  public String namespace(final JsonNode source) {
    return source.get("db").asText();
  }

  @Override
  public String name(JsonNode source) {
    return source.get("table").asText();
  }

  private Long getCdcDefaultCursor() {
    return this.emittedAt.getEpochSecond() * ONE_HUNDRED_MILLION + this.recordCounter.getAndIncrement();
  }

}
