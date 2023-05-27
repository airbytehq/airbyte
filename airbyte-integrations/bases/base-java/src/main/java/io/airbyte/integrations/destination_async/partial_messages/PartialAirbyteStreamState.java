/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.partial_messages;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.airbyte.protocol.models.v0.StreamDescriptor;

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

}
