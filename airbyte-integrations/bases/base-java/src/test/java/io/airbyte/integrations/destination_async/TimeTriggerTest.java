/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.integrations.destination_async.buffers.BufferDequeue;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.util.Optional;
import java.util.Set;
import org.junit.jupiter.api.Test;

public class TimeTriggerTest {

  public static final Instant NOW = Instant.now();
  public static final Instant FIVE_MIN_AGO = NOW.minusSeconds(60 * 5);

  private static final StreamDescriptor DESC1 = new StreamDescriptor().withName("test1");

  @Test
  void testTimeTrigger() {
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);
    when(bufferDequeue.getBufferedStreams()).thenReturn(Set.of(DESC1));
    when(bufferDequeue.getTimeOfLastRecord(DESC1))
        .thenReturn(Optional.empty())
        .thenReturn(Optional.of(NOW))
        .thenReturn(Optional.of(FIVE_MIN_AGO));

    final DetectStreamToFlush detect = new DetectStreamToFlush(bufferDequeue, null, null, null);
    assertEquals(false, detect.isTimeTriggered(DESC1).getLeft());
    assertEquals(false, detect.isTimeTriggered(DESC1).getLeft());
    assertEquals(true, detect.isTimeTriggered(DESC1).getLeft());
  }

}
