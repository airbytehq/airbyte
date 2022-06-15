/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.integrations.debezium.CdcMetadataInjector;

public class PostgresCdcConnectorMetadataInjector implements CdcMetadataInjector {

  @Override
  public void addMetaData(final ObjectNode event, final JsonNode source) {
    final long lsn = source.get("lsn").asLong();
    event.put(PostgresUtils.CDC_LSN, lsn);
  }

  @Override
  public String namespace(final JsonNode source) {
    return source.get("schema").asText();
  }

}
