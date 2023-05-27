/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.partial_messages;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;
import io.airbyte.protocol.models.v0.AirbyteMessage;

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

}
