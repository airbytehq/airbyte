/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;
import java.util.UUID;

public class KinesisRecord {

  @JsonProperty("_airbyte_ab_id")
  private UUID id;

  @JsonProperty("_airbyte_data")
  private String data;

  @JsonProperty("_airbyte_emitted_at")
  private Instant timestamp;

  public KinesisRecord() {

  }

  public KinesisRecord(UUID id, String data, Instant timestamp) {
    this.id = id;
    this.data = data;
    this.timestamp = timestamp;
  }

  public static KinesisRecord of(UUID id, String data, Instant timestamp) {
    return new KinesisRecord(id, data, timestamp);
  }

  public UUID getId() {
    return id;
  }

  public String getData() {
    return data;
  }

  public Instant getTimestamp() {
    return timestamp;
  }

  @Override
  public String toString() {
    return "KinesisRecord{" +
        "id=" + id +
        ", data='" + data + '\'' +
        ", timestamp=" + timestamp +
        '}';
  }

}
