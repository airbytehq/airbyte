/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.cdc;

import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_DELETED_AT;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_LSN;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_UPDATED_AT;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.integrations.debezium.CdcMetadataInjector;

public class PostgresCdcConnectorMetadataInjector implements CdcMetadataInjector<Long> {

  private final String transactionTimestamp;

  private final Long lsn;

  PostgresCdcConnectorMetadataInjector() {
    this.transactionTimestamp = null;
    this.lsn = null;
  }

  public PostgresCdcConnectorMetadataInjector(final String transactionTimestamp, final Long lsn) {
    this.transactionTimestamp = transactionTimestamp;
    this.lsn = lsn;
  }

  @Override
  public void addMetaData(final ObjectNode event, final JsonNode source) {
    final long lsn = source.get("lsn").asLong();
    event.put(CDC_LSN, lsn);
  }

  @Override
  public void addMetaDataToRowsFetchedOutsideDebezium(final ObjectNode record) {
    record.put(CDC_UPDATED_AT, transactionTimestamp);
    record.put(CDC_LSN, lsn);
    record.put(CDC_DELETED_AT, (String) null);
  }

  @Override
  public String namespace(final JsonNode source) {
    return source.get("schema").asText();
  }

  @Override
  public String name(JsonNode source) {
    return source.get("table").asText();
  }

}
