/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static io.airbyte.integrations.source.mysql.MySqlSource.MYSQL_CDC_OFFSET;
import static io.airbyte.integrations.source.mysql.MySqlSource.MYSQL_DB_HISTORY;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.debezium.CdcSavedInfoFetcher;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import java.util.Optional;

public class MySqlCdcSavedInfoFetcher implements CdcSavedInfoFetcher {

  private final JsonNode savedOffset;
  private final JsonNode savedSchemaHistory;

  protected MySqlCdcSavedInfoFetcher(final CdcState savedState) {
    final boolean savedStatePresent = savedState != null && savedState.getState() != null;
    this.savedOffset = savedStatePresent ? savedState.getState().get(MYSQL_CDC_OFFSET) : null;
    this.savedSchemaHistory = savedStatePresent ? savedState.getState().get(MYSQL_DB_HISTORY) : null;
  }

  @Override
  public JsonNode getSavedOffset() {
    return savedOffset;
  }

  @Override
  public Optional<JsonNode> getSavedSchemaHistory() {
    return Optional.ofNullable(savedSchemaHistory);
  }

}
