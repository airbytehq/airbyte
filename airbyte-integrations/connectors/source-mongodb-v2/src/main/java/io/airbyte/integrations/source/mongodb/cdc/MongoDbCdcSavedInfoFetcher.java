/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.debezium.CdcSavedInfoFetcher;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage;
import java.util.Optional;

/**
 * Implementation of the {@link CdcSavedInfoFetcher} interface for MongoDB.
 */
public class MongoDbCdcSavedInfoFetcher implements CdcSavedInfoFetcher {

  private final MongoDbCdcState savedState;

  public MongoDbCdcSavedInfoFetcher(final MongoDbCdcState savedState) {
    this.savedState = savedState;
  }

  @Override
  public JsonNode getSavedOffset() {
    return savedState.state();
  }

  @Override
  public AirbyteSchemaHistoryStorage.SchemaHistory<Optional<JsonNode>> getSavedSchemaHistory() {
    throw new RuntimeException("Schema history is not relevant for MongoDb");
  }

}
