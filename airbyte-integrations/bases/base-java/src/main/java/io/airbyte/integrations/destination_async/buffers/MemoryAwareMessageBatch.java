/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import io.airbyte.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.integrations.destination_async.buffers.StreamAwareQueue.Meta;
import io.airbyte.integrations.destination_async.state.AsyncDestinationStateManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Optional;
import java.util.stream.Stream;

/**
 * POJO abstraction representing one discrete buffer read. This allows ergonomics dequeues by
 * {@link io.airbyte.integrations.destination_async.FlushWorkers}.
 * <p>
 * The contained stream **IS EXPECTED to be a BOUNDED** stream. Returning a boundless stream has
 * undefined behaviour.
 * <p>
 * Once done, consumers **MUST** invoke {@link #close()}. As the {@link #batch} has already been
 * retrieved from in-memory buffers, we need to update {@link GlobalMemoryManager} to reflect the
 * freed up memory and avoid memory leaks.
 */
public class MemoryAwareMessageBatch implements AutoCloseable {

  private final StreamDescriptor streamDescriptor;
  private Stream<Meta> batch;
  private final long sizeInBytes;
  private final GlobalMemoryManager memoryManager;
  private final AsyncDestinationStateManager stateManager;
  private final StreamAwareQueue queue; // only here so that we can reset min queue message number.

  private long minMessageNum = 0;
  private long maxMessageNum = 0;

  public MemoryAwareMessageBatch(
                                 final StreamDescriptor streamDescriptor,
                                 final Stream<Meta> batch,
                                 final long sizeInBytes,
                                 final GlobalMemoryManager memoryManager,
                                 final AsyncDestinationStateManager stateManager,
                                 final StreamAwareQueue queue) {
    this.streamDescriptor = streamDescriptor;
    this.batch = batch;
    this.sizeInBytes = sizeInBytes;
    this.memoryManager = memoryManager;
    this.stateManager = stateManager;
    this.queue = queue;
  }

  public Stream<AirbyteMessage> getData() {
    return batch.map(meta -> {
      if (minMessageNum == 0) {
        minMessageNum = meta.messageNum(); // assumes ascending.
      }
      maxMessageNum = meta.messageNum(); // assumes ascending.
      return meta.message();
    });
  }

  @Override
  public void close() throws Exception {
    batch = null;
    memoryManager.free(sizeInBytes);
    queue.updateMinMessageNum();
  }

  public Optional<AirbyteMessage> getState() {
    return stateManager.completeState(streamDescriptor, minMessageNum, maxMessageNum);
  }

}
