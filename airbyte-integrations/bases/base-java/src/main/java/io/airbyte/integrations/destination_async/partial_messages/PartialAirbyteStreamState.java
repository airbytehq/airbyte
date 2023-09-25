/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.partial_messages;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Objects;

public class PartialAirbyteStreamState {

  @JsonProperty("stream_descriptor")
  private StreamDescriptor streamDescriptor;

  public PartialAirbyteStreamState() {
    streamDescriptor = streamDescriptor;
  }

  @JsonProperty("stream_descriptor")
  public StreamDescriptor getStreamDescriptor() {
    return streamDescriptor;
  }

  @JsonProperty("stream_descriptor")
  public void setStreamDescriptor(final StreamDescriptor streamDescriptor) {
    this.streamDescriptor = streamDescriptor;
  }

  public PartialAirbyteStreamState withStreamDescriptor(final StreamDescriptor streamDescriptor) {
    this.streamDescriptor = streamDescriptor;
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
    final PartialAirbyteStreamState that = (PartialAirbyteStreamState) o;
    return Objects.equals(streamDescriptor, that.streamDescriptor);
  }

  @Override
  public int hashCode() {
    return Objects.hash(streamDescriptor);
  }

  @Override
  public String toString() {
    return "PartialAirbyteStreamState{" +
        "streamDescriptor=" + streamDescriptor +
        '}';
  }

}
