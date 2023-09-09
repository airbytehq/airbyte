/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static io.airbyte.integrations.debezium.internals.mysql.MySqlDebeziumStateUtil.IS_COMPRESSED;
import static io.airbyte.integrations.debezium.internals.mysql.MySqlDebeziumStateUtil.MYSQL_CDC_OFFSET;
import static io.airbyte.integrations.debezium.internals.mysql.MySqlDebeziumStateUtil.MYSQL_DB_HISTORY;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.debezium.CdcSavedInfoFetcher;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import java.util.Optional;

public class MySqlCdcSavedInfoFetcher implements CdcSavedInfoFetcher {

  private final JsonNode savedOffset;
  private final JsonNode savedSchemaHistory;
  private final boolean isSavedSchemaHistoryCompressed;

  public MySqlCdcSavedInfoFetcher(final CdcState savedState) {
    final boolean savedStatePresent = savedState != null && savedState.getState() != null;
    this.savedOffset = savedStatePresent ? savedState.getState().get(MYSQL_CDC_OFFSET) : null;
    this.savedSchemaHistory = savedStatePresent ? savedState.getState().get(MYSQL_DB_HISTORY) : null;
    this.isSavedSchemaHistoryCompressed = !savedStatePresent || !savedState.getState().has(IS_COMPRESSED) || savedState.getState().get(IS_COMPRESSED).asBoolean();
  }

  @Override
  public JsonNode getSavedOffset() {
    return savedOffset;
  }

  @Override
  public SchemaHistoryInfo getSavedSchemaHistory() {
    return new SchemaHistoryInfo(Optional.ofNullable(savedSchemaHistory), isSavedSchemaHistoryCompressed, true);
  }

}
