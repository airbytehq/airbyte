/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static io.airbyte.integrations.source.mssql.MssqlSource.CDC_EVENT_SERIAL_NO;
import static io.airbyte.integrations.source.mssql.MssqlSource.CDC_LSN;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.integrations.debezium.CdcMetadataInjector;

public class MssqlCdcConnectorMetadataInjector implements CdcMetadataInjector {

  @Override
  public void addMetaData(final ObjectNode event, final JsonNode source) {
    final String commitLsn = source.get("commit_lsn").asText();
    final String eventSerialNo = source.get("event_serial_no").asText();
    event.put(CDC_LSN, commitLsn);
    event.put(CDC_EVENT_SERIAL_NO, eventSerialNo);
  }

  @Override
  public String namespace(final JsonNode source) {
    return source.get("schema").asText();
  }

}
