/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static io.airbyte.integrations.source.mssql.MssqlSource.IS_COMPRESSED;
import static io.airbyte.integrations.source.mssql.MssqlSource.MSSQL_CDC_OFFSET;
import static io.airbyte.integrations.source.mssql.MssqlSource.MSSQL_DB_HISTORY;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.cdk.integrations.debezium.CdcSavedInfoFetcher;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage.SchemaHistory;
import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState;
import java.util.Optional;

public class MssqlCdcSavedInfoFetcher implements CdcSavedInfoFetcher {

  private final JsonNode savedOffset;
  private final JsonNode savedSchemaHistory;
  private final boolean isSavedSchemaHistoryCompressed;

  protected MssqlCdcSavedInfoFetcher(final CdcState savedState) {
    final boolean savedStatePresent = savedState != null && savedState.getState() != null;
    this.savedOffset = savedStatePresent ? savedState.getState().get(MSSQL_CDC_OFFSET) : null;

    ObjectMapper mapper = new ObjectMapper();
    try {
      this.savedSchemaHistory = mapper.readTree("{\"source\":{\"server\":\"test\",\"database\":\"test\"},\"position\":{\"commit_lsn\":\"0000093b:0000f520:0003\",\"snapshot\":true,\"snapshot_completed\":false},\"ts_ms\":1704740663018,\"databaseName\":\"test\",\"schemaName\":\"dbo\",\"tableChanges\":[{\"type\":\"CREATE\",\"id\":\"\\\"test\\\".\\\"dbo\\\".\\\"NewTable\\\"\",\"table\":{\"defaultCharsetName\":null,\"primaryKeyColumnNames\":[],\"columns\":[{\"name\":\"id\",\"jdbcType\":12,\"typeName\":\"varchar\",\"typeExpression\":\"varchar\",\"charsetName\":null,\"length\":100,\"position\":1,\"optional\":true,\"autoIncremented\":false,\"generated\":false,\"comment\":null,\"hasDefaultValue\":true,\"enumValues\":[]},{\"name\":\"bin\",\"jdbcType\":-2,\"typeName\":\"binary\",\"typeExpression\":\"binary\",\"charsetName\":null,\"length\":100,\"position\":2,\"optional\":true,\"autoIncremented\":false,\"generated\":false,\"comment\":null,\"hasDefaultValue\":true,\"enumValues\":[]}],\"attributes\":[]},\"comment\":null}]}");
    } catch (JsonProcessingException e) {
      throw new RuntimeException(e);
    }
    this.isSavedSchemaHistoryCompressed =
        savedStatePresent && savedState.getState().has(IS_COMPRESSED) && savedState.getState().get(IS_COMPRESSED).asBoolean();
  }

  @Override
  public JsonNode getSavedOffset() {
    return savedOffset;
  }

  @Override
  public SchemaHistory<Optional<JsonNode>> getSavedSchemaHistory() {
    return new SchemaHistory<>(Optional.ofNullable(savedSchemaHistory), isSavedSchemaHistoryCompressed);
  }

}
