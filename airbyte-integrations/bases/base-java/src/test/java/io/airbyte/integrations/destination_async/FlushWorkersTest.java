/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.integrations.destination_async.buffers.BufferDequeue;
import io.airbyte.integrations.destination_async.buffers.MemoryAwareMessageBatch;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.integrations.destination_async.state.FlushFailure;
import io.airbyte.integrations.destination_async.state.GlobalAsyncStateManager;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Stream;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class FlushWorkersTest {

  @Test
  void testErrorHandling() throws Exception {
    final AtomicBoolean hasThrownError = new AtomicBoolean(false);
    final var desc = new StreamDescriptor().withName("test");
    final var dequeue = mock(BufferDequeue.class);
    when(dequeue.getBufferedStreams()).thenReturn(Set.of(desc));
    when(dequeue.take(desc, 1000)).thenReturn(new MemoryAwareMessageBatch(List.of(), 10, null, null));
    when(dequeue.getQueueSizeBytes(desc)).thenReturn(Optional.of(10L));
    when(dequeue.getQueueSizeInRecords(desc)).thenAnswer(ignored -> {
      if (hasThrownError.get()) {
        return Optional.of(0L);
      } else {
        return Optional.of(1L);
      }
    });

    final var flushFailure = new FlushFailure();
    final var workers = new FlushWorkers(dequeue, new ErrorOnFlush(hasThrownError), m -> {}, flushFailure, mock(GlobalAsyncStateManager.class));
    workers.start();
    workers.close();

    Assertions.assertTrue(flushFailure.isFailed());
    Assertions.assertEquals(IOException.class, flushFailure.getException().getClass());
  }

  private static class ErrorOnFlush implements DestinationFlushFunction {

    private final AtomicBoolean hasThrownError;

    public ErrorOnFlush(final AtomicBoolean hasThrownError) {
      this.hasThrownError = hasThrownError;
    }

    @Override
    public void flush(final StreamDescriptor desc, final Stream<PartialAirbyteMessage> stream) throws Exception {
      hasThrownError.set(true);
      throw new IOException("Error on flush");
    }

    @Override
    public long getOptimalBatchSizeBytes() {
      return 1000;
    }

  }

}
