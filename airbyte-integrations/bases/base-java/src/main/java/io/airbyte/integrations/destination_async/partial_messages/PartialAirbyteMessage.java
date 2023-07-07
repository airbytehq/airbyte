/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.partial_messages;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.util.Objects;

public class PartialAirbyteMessage {

  @JsonProperty("type")
  @JsonPropertyDescription("Message type")
  private AirbyteMessage.Type type;

  @JsonProperty("record")
  private PartialAirbyteRecordMessage record;

  @JsonProperty("state")
  private PartialAirbyteStateMessage state;

  @JsonProperty("serialized")
  private String serialized;

  public PartialAirbyteMessage() {}

  @JsonProperty("type")
  public AirbyteMessage.Type getType() {
    return type;
  }

  @JsonProperty("type")
  public void setType(final AirbyteMessage.Type type) {
    this.type = type;
  }

  public PartialAirbyteMessage withType(final AirbyteMessage.Type type) {
    this.type = type;
    return this;
  }

  @JsonProperty("record")
  public PartialAirbyteRecordMessage getRecord() {
    return record;
  }

  @JsonProperty("record")
  public void setRecord(final PartialAirbyteRecordMessage record) {
    this.record = record;
  }

  public PartialAirbyteMessage withRecord(final PartialAirbyteRecordMessage record) {
    this.record = record;
    return this;
  }

  @JsonProperty("state")
  public PartialAirbyteStateMessage getState() {
    return state;
  }

  @JsonProperty("state")
  public void setState(final PartialAirbyteStateMessage state) {
    this.state = state;
  }

  public PartialAirbyteMessage withState(final PartialAirbyteStateMessage state) {
    this.state = state;
    return this;
  }

  @JsonProperty("serialized")
  public String getSerialized() {
    return serialized;
  }

  @JsonProperty("serialized")
  public void setSerialized(final String serialized) {
    this.serialized = serialized;
  }

  public PartialAirbyteMessage withSerialized(final String serialized) {
    this.serialized = serialized;
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
    final PartialAirbyteMessage that = (PartialAirbyteMessage) o;
    return type == that.type && Objects.equals(record, that.record) && Objects.equals(state, that.state)
        && Objects.equals(serialized, that.serialized);
  }

  @Override
  public int hashCode() {
    return Objects.hash(type, record, state, serialized);
  }

  @Override
  public String toString() {
    return "PartialAirbyteMessage{" +
        "type=" + type +
        ", record=" + record +
        ", state=" + state +
        ", serialized='" + serialized + '\'' +
        '}';
  }

}
