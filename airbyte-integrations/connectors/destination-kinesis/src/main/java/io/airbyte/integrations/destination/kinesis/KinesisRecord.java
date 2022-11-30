/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;
import java.util.UUID;

/**
 * KinesisRecord class for mapping records in the Kinesis stream.
 */
public class KinesisRecord {

  public static final String COLUMN_NAME_AB_ID = "_airbyte_ab_id";
  public static final String COLUMN_NAME_DATA = "_airbyte_data";
  public static final String COLUMN_NAME_EMITTED_AT = "_airbyte_emitted_at";

  @JsonProperty(COLUMN_NAME_AB_ID)
  private UUID id;

  @JsonProperty(COLUMN_NAME_DATA)
  private String data;

  @JsonProperty(COLUMN_NAME_EMITTED_AT)
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
