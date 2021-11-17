/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;
import java.util.UUID;

/**
 * KinesisRecord class for mapping records in the Kinesis stream.
 */
public class KinesisRecord {

  public static final String ID_PROPERTY = "_airbyte_ab_id";

  public static final String DATA_PROPERTY = "_airbyte_data";

  public static final String TIMESTAMP_PROPERTY = "_airbyte_emitted_at";

  @JsonProperty(ID_PROPERTY)
  private UUID id;

  @JsonProperty(DATA_PROPERTY)
  private String data;

  @JsonProperty(TIMESTAMP_PROPERTY)
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
