/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.source.postgres.PostgresSource.CDC_LSN;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.integrations.debezium.CdcMetadataInjector;

public class PostgresCdcConnectorMetadataInjector implements CdcMetadataInjector {

  @Override
  public void addMetaData(final ObjectNode event, final JsonNode source) {
    final long lsn = source.get("lsn").asLong();
    event.put(CDC_LSN, lsn);
  }

  @Override
  public String namespace(final JsonNode source) {
    return source.get("schema").asText();
  }

}
