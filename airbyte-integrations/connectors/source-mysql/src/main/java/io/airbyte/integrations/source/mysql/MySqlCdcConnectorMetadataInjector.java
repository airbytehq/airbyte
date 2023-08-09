/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static io.airbyte.integrations.source.mysql.MySqlSource.CDC_DEFAULT_CURSOR;
import static io.airbyte.integrations.source.mysql.MySqlSource.CDC_LOG_FILE;
import static io.airbyte.integrations.source.mysql.MySqlSource.CDC_LOG_POS;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.integrations.debezium.CdcMetadataInjector;
import io.airbyte.integrations.debezium.internals.mysql.MySqlDebeziumStateUtil.MysqlDebeziumStateAttributes;
import java.time.Instant;
import java.util.concurrent.atomic.AtomicLong;

public class MySqlCdcConnectorMetadataInjector implements CdcMetadataInjector<MysqlDebeziumStateAttributes> {

  private final long emittedAt;
  // This now makes this class stateful. Please make sure to use the same instance within a sync
  private final AtomicLong recordCounter = new AtomicLong(1);
  private static final long ONE_HUNDRED_MILLION = 100_000_000;

  public MySqlCdcConnectorMetadataInjector(final Instant emittedAt) {
    this.emittedAt = emittedAt.getEpochSecond() * ONE_HUNDRED_MILLION;
  }

  @Override
  public void addMetaData(final ObjectNode event, final JsonNode source) {
    event.put(CDC_LOG_FILE, source.get("file").asText());
    event.put(CDC_LOG_POS, source.get("pos").asLong());
    event.put(CDC_DEFAULT_CURSOR, getCdcDefaultCursor());
  }

  @Override
  public void addMetaDataToRowsFetchedOutsideDebezium(final ObjectNode record, final String transactionTimestamp,
      final MysqlDebeziumStateAttributes debeziumStateAttributes) {
    record.put(CDC_UPDATED_AT, transactionTimestamp);
    record.put(CDC_LOG_FILE, debeziumStateAttributes.binlogFilename());
    record.put(CDC_LOG_POS, debeziumStateAttributes.binlogPosition());
    record.put(CDC_DELETED_AT, (String) null);
    record.put(CDC_DEFAULT_CURSOR, getCdcDefaultCursor());
  }

  @Override
  public String namespace(final JsonNode source) {
    return source.get("db").asText();
  }

  private Long getCdcDefaultCursor() {
    return this.emittedAt + recordCounter.getAndIncrement();
  }

}
