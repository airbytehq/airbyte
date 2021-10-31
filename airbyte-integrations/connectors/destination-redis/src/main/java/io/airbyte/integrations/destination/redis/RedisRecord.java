package io.airbyte.integrations.destination.redis;

import java.time.Instant;

public class RedisRecord {

    Long id;

    String data;

    Instant timestamp;

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
}
