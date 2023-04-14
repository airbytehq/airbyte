/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.stream;

import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus;
import io.airbyte.protocol.models.v0.AirbyteTraceMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Optional;

/**
 * Represents the current status of a stream provided by a source.
 */
public class AirbyteStreamStatusHolder {

  private final AirbyteStreamNameNamespacePair airbyteStream;

  private final AirbyteStreamStatus airbyteStreamStatus;

  private final Optional<Boolean> success;

  public AirbyteStreamStatusHolder(final AirbyteStreamNameNamespacePair airbyteStream,
                                   final AirbyteStreamStatus airbyteStreamStatus,
                                   final Optional<Boolean> success) {
    this.airbyteStream = airbyteStream;
    this.airbyteStreamStatus = airbyteStreamStatus;
    this.success = success;
  }

  public AirbyteTraceMessage toTraceMessage() {
    final AirbyteTraceMessage traceMessage = new AirbyteTraceMessage();
    final AirbyteStreamStatusTraceMessage streamStatusTraceMessage = new AirbyteStreamStatusTraceMessage()
        .withStreamDescriptor(new StreamDescriptor().withName(airbyteStream.getName()).withNamespace(airbyteStream.getNamespace()))
        .withStatus(airbyteStreamStatus);
    success.ifPresent(s -> streamStatusTraceMessage.withSuccess(s));
    return traceMessage.withEmittedAt(Long.valueOf(System.currentTimeMillis()).doubleValue()).withStreamStatus(streamStatusTraceMessage)
        .withType(AirbyteTraceMessage.Type.STREAM_STATUS);
  }

}
