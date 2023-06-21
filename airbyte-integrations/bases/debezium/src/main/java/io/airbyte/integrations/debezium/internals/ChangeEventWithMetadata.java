/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.debezium.engine.ChangeEvent;

public class ChangeEventWithMetadata {

  private final ChangeEvent<String, String> event;
  private final JsonNode eventValueAsJson;
  private final SnapshotMetadata snapshotMetadata;

  public ChangeEventWithMetadata(final ChangeEvent<String, String> event) {
    this.event = event;
    this.eventValueAsJson = Jsons.deserialize(event.value());
    this.snapshotMetadata = SnapshotMetadata.fromString(eventValueAsJson.get("source").get("snapshot").asText());
  }

  public ChangeEvent<String, String> event() {
    return event;
  }

  public JsonNode eventValueAsJson() {
    return eventValueAsJson;
  }

  public boolean isSnapshotEvent() {
    return SnapshotMetadata.isSnapshotEventMetadata(snapshotMetadata);
  }

  public SnapshotMetadata snapshotMetadata() {
    return snapshotMetadata;
  }

}
