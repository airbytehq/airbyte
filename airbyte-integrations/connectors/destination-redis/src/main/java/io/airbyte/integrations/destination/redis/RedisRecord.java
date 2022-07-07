/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redis;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.Instant;

public class RedisRecord {

  public static final String ID_PROPERTY = "_airbyte_ab_id";

  public static final String DATA_PROPERTY = "_airbyte_data";

  public static final String TIMESTAMP_PROPERTY = "_airbyte_emitted_at";

  @JsonProperty(ID_PROPERTY)
  private Long id;

  @JsonProperty(DATA_PROPERTY)
  private String data;

  @JsonProperty(TIMESTAMP_PROPERTY)
  private Instant timestamp;

  public RedisRecord() {

  }

  public RedisRecord(Long id, String data, Instant timestamp) {
    this.id = id;
    this.data = data;
    this.timestamp = timestamp;
  }

  public Long getId() {
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
    return "RedisRecord{" +
        "id=" + id +
        ", data='" + data + '\'' +
        ", timestamp=" + timestamp +
        '}';
  }

}
