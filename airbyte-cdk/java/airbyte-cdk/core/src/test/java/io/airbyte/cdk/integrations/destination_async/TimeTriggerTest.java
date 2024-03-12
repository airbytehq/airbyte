/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination_async;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.cdk.integrations.destination_async.buffers.BufferDequeue;
import java.time.Clock;
import org.junit.jupiter.api.Test;

public class TimeTriggerTest {

  private static final long NOW_MS = System.currentTimeMillis();
  private static final long ONE_SEC = 1000L;
  private static final long FIVE_MIN = 5 * 60 * 1000;

  @Test
  void testTimeTrigger() {
    final BufferDequeue bufferDequeue = mock(BufferDequeue.class);

    final Clock mockedNowProvider = mock(Clock.class);
    when(mockedNowProvider.millis())
        .thenReturn(NOW_MS);

    final DetectStreamToFlush detect = new DetectStreamToFlush(bufferDequeue, null, null, null, mockedNowProvider);
    assertEquals(false, detect.isTimeTriggered(NOW_MS).getLeft());
    assertEquals(false, detect.isTimeTriggered(NOW_MS - ONE_SEC).getLeft());
    assertEquals(true, detect.isTimeTriggered(NOW_MS - FIVE_MIN).getLeft());
  }

}
