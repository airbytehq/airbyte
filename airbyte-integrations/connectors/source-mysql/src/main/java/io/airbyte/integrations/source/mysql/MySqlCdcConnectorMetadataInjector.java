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

public class MySqlCdcConnectorMetadataInjector implements CdcMetadataInjector<MysqlDebeziumStateAttributes> {

  private final Instant emittedAt;

  public MySqlCdcConnectorMetadataInjector(final Instant emittedAt) {
    this.emittedAt = emittedAt;
  }

  @Override
  public void addMetaData(final ObjectNode event, final JsonNode source) {
    final String cdcDefaultCursor =
        String.format("%s_%s_%s", emittedAt.toString(), source.get("file").asText(), source.get("pos").asText());
    event.put(CDC_LOG_FILE, source.get("file").asText());
    event.put(CDC_LOG_POS, source.get("pos").asLong());
    event.put(CDC_DEFAULT_CURSOR, cdcDefaultCursor);
  }

  @Override
  public void addMetaDataToRowsFetchedOutsideDebezium(final ObjectNode record, final String transactionTimestamp,
      final MysqlDebeziumStateAttributes debeziumStateAttributes) {
    record.put(CDC_UPDATED_AT, transactionTimestamp);
    record.put(CDC_LOG_FILE, debeziumStateAttributes.binlogFilename());
    record.put(CDC_LOG_POS, debeziumStateAttributes.binlogPosition());
    record.put(CDC_DELETED_AT, (String) null);
  }

  @Override
  public String namespace(final JsonNode source) {
    return source.get("db").asText();
  }

}
