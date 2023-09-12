/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.debezium.CdcSavedInfoFetcher;
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
  public Optional<JsonNode> getSavedSchemaHistory() {
    return Optional.empty();
  }

}
