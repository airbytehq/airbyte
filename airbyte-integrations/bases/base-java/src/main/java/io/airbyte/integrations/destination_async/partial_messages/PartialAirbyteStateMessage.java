/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.partial_messages;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;

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

}
