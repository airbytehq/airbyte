/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.integrations.destination_async.buffers.BufferDequeue;
import io.airbyte.integrations.destination_async.buffers.MemoryAwareMessageBatch;
import io.airbyte.integrations.destination_async.state.FlushFailure;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.function.Consumer;
import java.util.stream.Stream;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class FlushWorkersTest {

  @Test
  void testErrorHandling() throws Exception {
    final var desc = new StreamDescriptor().withName("test");
    final var dequeue = mock(BufferDequeue.class);
    when(dequeue.getBufferedStreams()).thenReturn(Set.of(desc));
    when(dequeue.take(desc, 1000)).thenReturn(new MemoryAwareMessageBatch(List.of(), 0, null, null));
    when(dequeue.getQueueSizeInRecords(desc)).thenReturn(Optional.of(1L));
    final var collector = mock(Consumer.class);

    final var flushFailure = new FlushFailure();
    final var workers = new FlushWorkers(dequeue, new ErrorOnFlush(), collector, flushFailure);
    workers.start();
    workers.close();

    Assertions.assertTrue(flushFailure.isFailed().get());
    Assertions.assertEquals(IOException.class, flushFailure.getException().getClass());
  }

  private static class ErrorOnFlush implements DestinationFlushFunction {

    @Override
    public void flush(final StreamDescriptor decs, final Stream<AirbyteMessage> stream) throws Exception {
      throw new IOException("Error on flush");
    }

    @Override
    public long getOptimalBatchSizeBytes() {
      return 1000;
    }

  }

}
