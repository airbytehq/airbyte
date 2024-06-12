/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import com.fasterxml.jackson.databind.JsonNode;

/**
 * Represents the global CDC state that is used by Debezium as an offset.
 *
 * @param state The Debezium offset state as a {@link JsonNode}.
 */
public record MongoDbCdcState(JsonNode state, Boolean schema_enforced) {

  public MongoDbCdcState {
    // Ensure that previously saved state with no schema_enforced will migrate to schema_enforced = true
    schema_enforced = schema_enforced == null || schema_enforced;
  }

  public MongoDbCdcState(final JsonNode state) {
    this(state, true);
  }

}
