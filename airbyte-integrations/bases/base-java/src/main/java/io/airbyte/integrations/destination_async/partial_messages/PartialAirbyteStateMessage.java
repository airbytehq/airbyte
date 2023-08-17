/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.partial_messages;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import java.util.Objects;

public class PartialAirbyteStateMessage {

  @JsonProperty("type")
  private AirbyteStateType type;

  @JsonProperty("stream")
  private PartialAirbyteStreamState stream;

  public PartialAirbyteStateMessage() {}

  @JsonProperty("type")
  public AirbyteStateType getType() {
    return type;
  }

  @JsonProperty("type")
  public void setType(final AirbyteStateType type) {
    this.type = type;
  }

  public PartialAirbyteStateMessage withType(final AirbyteStateType type) {
    this.type = type;
    return this;
  }

  @JsonProperty("stream")
  public PartialAirbyteStreamState getStream() {
    return stream;
  }

  @JsonProperty("stream")
  public void setStream(final PartialAirbyteStreamState stream) {
    this.stream = stream;
  }

  public PartialAirbyteStateMessage withStream(final PartialAirbyteStreamState stream) {
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
    final PartialAirbyteStateMessage that = (PartialAirbyteStateMessage) o;
    return type == that.type && Objects.equals(stream, that.stream);
  }

  @Override
  public int hashCode() {
    return Objects.hash(type, stream);
  }

  @Override
  public String toString() {
    return "PartialAirbyteStateMessage{" +
        "type=" + type +
        ", stream=" + stream +
        '}';
  }

}
