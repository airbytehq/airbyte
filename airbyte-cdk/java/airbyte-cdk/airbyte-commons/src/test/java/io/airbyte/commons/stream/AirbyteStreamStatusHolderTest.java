/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.stream;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus;
import io.airbyte.protocol.models.v0.AirbyteTraceMessage;
import io.airbyte.protocol.models.v0.AirbyteTraceMessage.Type;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link AirbyteStreamStatusHolder} class.
 */
class AirbyteStreamStatusHolderTest {

  @Test
  void testToTraceMessage() {
    final Double startTime = Long.valueOf(System.currentTimeMillis()).doubleValue();
    final AirbyteStreamNameNamespacePair airbyteStreamNameAndNamespacePair = new AirbyteStreamNameNamespacePair("name", "namespace");
    final AirbyteStreamStatus streamStatus = AirbyteStreamStatus.RUNNING;
    final AirbyteStreamStatusHolder holder = new AirbyteStreamStatusHolder(airbyteStreamNameAndNamespacePair, streamStatus);

    final AirbyteTraceMessage traceMessage = holder.toTraceMessage();
    assertTrue(traceMessage.getEmittedAt() >= startTime);
    assertEquals(Type.STREAM_STATUS, traceMessage.getType());
    assertEquals(streamStatus, traceMessage.getStreamStatus().getStatus());
    assertEquals(new StreamDescriptor()
        .withName(airbyteStreamNameAndNamespacePair.getName())
        .withNamespace(airbyteStreamNameAndNamespacePair.getNamespace()), traceMessage.getStreamStatus().getStreamDescriptor());
  }

  @Test
  void testToTraceMessageWithOptionalData() {
    final Double startTime = Long.valueOf(System.currentTimeMillis()).doubleValue();
    final AirbyteStreamNameNamespacePair airbyteStreamNameAndNamespacePair = new AirbyteStreamNameNamespacePair("name", "namespace");
    final AirbyteStreamStatus streamStatus = AirbyteStreamStatus.COMPLETE;
    final AirbyteStreamStatusHolder holder = new AirbyteStreamStatusHolder(airbyteStreamNameAndNamespacePair, streamStatus);

    final AirbyteTraceMessage traceMessage = holder.toTraceMessage();
    assertTrue(traceMessage.getEmittedAt() >= startTime);
    assertEquals(Type.STREAM_STATUS, traceMessage.getType());
    assertEquals(streamStatus, traceMessage.getStreamStatus().getStatus());
    assertEquals(new StreamDescriptor()
        .withName(airbyteStreamNameAndNamespacePair.getName())
        .withNamespace(airbyteStreamNameAndNamespacePair.getNamespace()), traceMessage.getStreamStatus().getStreamDescriptor());
  }

}
