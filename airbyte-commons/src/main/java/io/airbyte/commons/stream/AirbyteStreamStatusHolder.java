/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.stream;

import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus;
import io.airbyte.protocol.models.v0.AirbyteTraceMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;

/**
 * Represents the current status of a stream provided by a source.
 */
public class AirbyteStreamStatusHolder {

  private final AirbyteStreamNameNamespacePair airbyteStream;

  private final AirbyteStreamStatus airbyteStreamStatus;

  public AirbyteStreamStatusHolder(final AirbyteStreamNameNamespacePair airbyteStream,
                                   final AirbyteStreamStatus airbyteStreamStatus) {
    this.airbyteStream = airbyteStream;
    this.airbyteStreamStatus = airbyteStreamStatus;
  }

  public AirbyteTraceMessage toTraceMessage() {
    final AirbyteTraceMessage traceMessage = new AirbyteTraceMessage();
    final AirbyteStreamStatusTraceMessage streamStatusTraceMessage = new AirbyteStreamStatusTraceMessage()
        .withStreamDescriptor(new StreamDescriptor().withName(airbyteStream.getName()).withNamespace(airbyteStream.getNamespace()))
        .withStatus(airbyteStreamStatus);
    return traceMessage.withEmittedAt(Long.valueOf(System.currentTimeMillis()).doubleValue())
        .withStreamStatus(streamStatusTraceMessage)
        .withType(AirbyteTraceMessage.Type.STREAM_STATUS);
  }

}
