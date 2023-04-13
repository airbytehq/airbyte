/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import io.debezium.engine.ChangeEvent;

public record ChangeEventWithMetadata(ChangeEvent<String, String> event, JsonNode eventValueAsJson, boolean isSnapshotEvent) {

}
