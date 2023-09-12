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
public record MongoDbCdcState(JsonNode state) {}
