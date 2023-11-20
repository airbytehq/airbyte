/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.protocol;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.protocol.deser.PartialJsonDeserializer;
import io.airbyte.cdk.protocol.deser.StringIterator;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Map;
import java.util.Objects;

public class PartialAirbyteStreamState {

  StreamDescriptor streamDescriptor;
  String serializedStreamState;

  public static PartialAirbyteStreamState fromJson(final StringIterator message) {
    return PartialJsonDeserializer.parseObject(
        message,
        PartialAirbyteStreamState::new,
        Map.of(
            "stream_descriptor", (streamState) -> streamState.streamDescriptor = streamDescriptorFromJson(message),
            "stream_state", (streamState) -> streamState.serializedStreamState = PartialJsonDeserializer.readSerializedValue(message)));
  }

  public static StreamDescriptor streamDescriptorFromJson(final StringIterator message) {
    return PartialJsonDeserializer.parseObject(
        message,
        StreamDescriptor::new,
        Map.of(
            "name", (streamDescriptor) -> streamDescriptor.setName(PartialJsonDeserializer.readStringValue(message)),
            "namespace", (streamDescriptor) -> streamDescriptor.setNamespace(PartialJsonDeserializer.readStringValue(message))));
  }

  public StreamDescriptor getStreamDescriptor() {
    return streamDescriptor;
  }

  public String getSerializedStreamState() {
    return serializedStreamState;
  }

  public String serialize() {
    String output = "{";
    output += "\"stream_descriptor\": " + Jsons.serialize(streamDescriptor);
    output += ", \"stream_state\": " + serializedStreamState;
    output += "}";
    return output;
  }

  @Override
  public String toString() {
    return "PartialAirbyteStreamState{" +
        "streamDescriptor=" + streamDescriptor +
        ", serializedStreamState='" + serializedStreamState + '\'' +
        '}';
  }

  @Override
  public boolean equals(final Object o) {
    if (this == o)
      return true;
    if (o == null || getClass() != o.getClass())
      return false;

    final PartialAirbyteStreamState that = (PartialAirbyteStreamState) o;

    if (!Objects.equals(streamDescriptor, that.streamDescriptor))
      return false;
    return Objects.equals(serializedStreamState, that.serializedStreamState);
  }

  @Override
  public int hashCode() {
    int result = streamDescriptor != null ? streamDescriptor.hashCode() : 0;
    result = 31 * result + (serializedStreamState != null ? serializedStreamState.hashCode() : 0);
    return result;
  }

  public AirbyteStreamState toFullStreamState() {
    final AirbyteStreamState streamState = new AirbyteStreamState();
    streamState.setStreamDescriptor(streamDescriptor);
    streamState.setStreamState(Jsons.deserializeExact(serializedStreamState));
    return streamState;
  }

  public PartialAirbyteStreamState withStreamDescriptor(final StreamDescriptor streamDescriptor) {
    this.streamDescriptor = streamDescriptor;
    return this;
  }

  public PartialAirbyteStreamState withStreamState(final JsonNode streamState) {
    this.serializedStreamState = Jsons.serialize(streamState);
    return this;
  }

}
