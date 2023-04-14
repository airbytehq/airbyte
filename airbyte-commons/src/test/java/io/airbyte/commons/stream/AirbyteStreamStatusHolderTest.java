/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.stream;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus;
import io.airbyte.protocol.models.v0.AirbyteTraceMessage;
import io.airbyte.protocol.models.v0.AirbyteTraceMessage.Type;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Optional;
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
    final AirbyteStreamStatusHolder holder = new AirbyteStreamStatusHolder(airbyteStreamNameAndNamespacePair, streamStatus, Optional.empty());

    final AirbyteTraceMessage traceMessage = holder.toTraceMessage();
    assertTrue(traceMessage.getEmittedAt() >= startTime);
    assertEquals(Type.STREAM_STATUS, traceMessage.getType());
    assertEquals(streamStatus, traceMessage.getStreamStatus().getStatus());
    assertEquals(new StreamDescriptor()
        .withName(airbyteStreamNameAndNamespacePair.getName())
        .withNamespace(airbyteStreamNameAndNamespacePair.getNamespace()), traceMessage.getStreamStatus().getStreamDescriptor());
    assertNull(traceMessage.getStreamStatus().getSuccess());
  }

  @Test
  void testToTraceMessageWithOptionalData() {
    final Double startTime = Long.valueOf(System.currentTimeMillis()).doubleValue();
    final AirbyteStreamNameNamespacePair airbyteStreamNameAndNamespacePair = new AirbyteStreamNameNamespacePair("name", "namespace");
    final AirbyteStreamStatus streamStatus = AirbyteStreamStatus.STOPPED;
    final Optional<Boolean> success = Optional.of(Boolean.TRUE);
    final AirbyteStreamStatusHolder holder = new AirbyteStreamStatusHolder(airbyteStreamNameAndNamespacePair, streamStatus, success);

    final AirbyteTraceMessage traceMessage = holder.toTraceMessage();
    assertTrue(traceMessage.getEmittedAt() >= startTime);
    assertEquals(Type.STREAM_STATUS, traceMessage.getType());
    assertEquals(streamStatus, traceMessage.getStreamStatus().getStatus());
    assertEquals(new StreamDescriptor()
        .withName(airbyteStreamNameAndNamespacePair.getName())
        .withNamespace(airbyteStreamNameAndNamespacePair.getNamespace()), traceMessage.getStreamStatus().getStreamDescriptor());
    assertEquals(success.get(), traceMessage.getStreamStatus().getSuccess());
  }
}
