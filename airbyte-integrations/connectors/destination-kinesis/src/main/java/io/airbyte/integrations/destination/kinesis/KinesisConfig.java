/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.kinesis;

import com.fasterxml.jackson.databind.JsonNode;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Objects;

/*
 * KinesisConfig class for storing immutable configuration for Kinesis.
 */
public class KinesisConfig {

  private final URI endpoint;

  private final String region;

  private final int shardCount;

  private final String accessKey;

  private final String privateKey;

  private final int bufferSize;

  public KinesisConfig(URI endpoint,
                       String region,
                       int shardCount,
                       String accessKey,
                       String privateKey,
                       int bufferSize) {
    this.endpoint = endpoint;
    this.region = region;
    this.shardCount = shardCount;
    this.accessKey = accessKey;
    this.privateKey = privateKey;
    this.bufferSize = bufferSize;
  }

  public KinesisConfig(JsonNode jsonNode) {
    String strend = jsonNode.get("endpoint").asText();
    try {
      this.endpoint = strend != null && !strend.isBlank() ? new URI(strend) : null;
    } catch (URISyntaxException e) {
      throw new UncheckedURISyntaxException(e);
    }
    this.region = jsonNode.get("region").asText();
    this.shardCount = jsonNode.get("shardCount").asInt(5);
    this.accessKey = jsonNode.get("accessKey").asText();
    this.privateKey = jsonNode.get("privateKey").asText();
    this.bufferSize = jsonNode.get("bufferSize").asInt(100);
  }

  public URI getEndpoint() {
    return endpoint;
  }

  public String getRegion() {
    return region;
  }

  public int getShardCount() {
    return shardCount;
  }

  public String getAccessKey() {
    return accessKey;
  }

  public String getPrivateKey() {
    return privateKey;
  }

  public int getBufferSize() {
    return bufferSize;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    KinesisConfig that = (KinesisConfig) o;
    return Objects.equals(endpoint, that.endpoint) && Objects.equals(region, that.region) &&
        accessKey.equals(that.accessKey) && privateKey.equals(that.privateKey);
  }

  @Override
  public int hashCode() {
    return Objects.hash(endpoint, region, accessKey, privateKey);
  }

  static class UncheckedURISyntaxException extends RuntimeException {

    public UncheckedURISyntaxException(Throwable cause) {
      super(cause);
    }

  }

}
