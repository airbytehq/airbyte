/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.partial_messages;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.Objects;

public class PartialAirbyteRecordMessage {

  @JsonProperty("namespace")
  private String namespace;
  @JsonProperty("stream")
  private String stream;

  public PartialAirbyteRecordMessage() {}

  @JsonProperty("namespace")
  public String getNamespace() {
    return namespace;
  }

  @JsonProperty("namespace")
  public void setNamespace(final String namespace) {
    this.namespace = namespace;
  }

  public PartialAirbyteRecordMessage withNamespace(final String namespace) {
    this.namespace = namespace;
    return this;
  }

  @JsonProperty("stream")
  public String getStream() {
    return stream;
  }

  @JsonProperty("stream")
  public void setStream(final String stream) {
    this.stream = stream;
  }

  public PartialAirbyteRecordMessage withStream(final String stream) {
    this.stream = stream;
    return this;
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o) {
      return true;
    }
    if (o == null || getClass() != o.getClass()) {
      return false;
    }
    final PartialAirbyteRecordMessage that = (PartialAirbyteRecordMessage) o;
    return Objects.equals(namespace, that.namespace) && Objects.equals(stream, that.stream);
  }

  @Override
  public int hashCode() {
    return Objects.hash(namespace, stream);
  }

  @Override
  public String toString() {
    return "PartialAirbyteRecordMessage{" +
        "namespace='" + namespace + '\'' +
        ", stream='" + stream + '\'' +
        '}';
  }

}
