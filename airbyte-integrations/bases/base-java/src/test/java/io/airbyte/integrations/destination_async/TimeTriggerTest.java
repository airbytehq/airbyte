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
import java.util.function.LongSupplier;

import org.junit.jupiter.api.Test;

public class TimeTriggerTest {

  private static final long START_TIME = 0L;
  private static final long ONE_SECOND_AFTER_START_TIME = 1000L;
  private static final long FIVE_MINUTES_AFTER_SECOND_TIME = 5L * 60L * 1000L + 1001L;

  private static final StreamDescriptor DESC1 = new StreamDescriptor().withName("test1");

  @Test
  void testTimeTrigger() {
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);

    final LongSupplier mockedNowProvider = mock(LongSupplier.class);
    when(mockedNowProvider.getAsLong())
            .thenReturn(START_TIME)
            .thenReturn(ONE_SECOND_AFTER_START_TIME)
            .thenReturn(FIVE_MINUTES_AFTER_SECOND_TIME);

    final DetectStreamToFlush detect = new DetectStreamToFlush(bufferDequeue, null, null, null, mockedNowProvider);
    assertEquals(false, detect.isTimeTriggered(DESC1).getLeft());
    assertEquals(false, detect.isTimeTriggered(DESC1).getLeft());
    assertEquals(true, detect.isTimeTriggered(DESC1).getLeft());
  }

}
