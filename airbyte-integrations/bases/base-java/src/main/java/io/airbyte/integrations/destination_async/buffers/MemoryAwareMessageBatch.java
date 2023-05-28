/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import io.airbyte.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
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

  private Stream<AirbyteMessage> batch;
  private final long sizeInBytes;
  private final GlobalMemoryManager memoryManager;

  public MemoryAwareMessageBatch(final Stream<AirbyteMessage> batch, final long sizeInBytes, final GlobalMemoryManager memoryManager) {
    this.batch = batch;
    this.sizeInBytes = sizeInBytes;
    this.memoryManager = memoryManager;
  }

  public Stream<AirbyteMessage> getData() {
    return batch;
  }

  @Override
  public void close() throws Exception {
    batch = null;
    memoryManager.free(sizeInBytes);
  }

}
