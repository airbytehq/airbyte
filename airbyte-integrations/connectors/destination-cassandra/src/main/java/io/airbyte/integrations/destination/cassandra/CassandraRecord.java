/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.cassandra;

import java.time.Instant;
import java.util.UUID;

class CassandraRecord {

  private final UUID id;

  private final String data;

  private final Instant timestamp;

  public CassandraRecord(UUID id, String data, Instant timestamp) {
    this.id = id;
    this.data = data;
    this.timestamp = timestamp;
  }

  static CassandraRecord of(UUID id, String data, Instant timestamp) {
    return new CassandraRecord(id, data, timestamp);
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
    return "CassandraRecord{" +
        "id=" + id +
        ", data='" + data + '\'' +
        ", timestamp=" + timestamp +
        '}';
  }

}
