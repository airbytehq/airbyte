/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import io.airbyte.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.integrations.destination_async.buffers.StreamAwareQueue.MessageWithMeta;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.integrations.destination_async.state.GlobalAsyncStateManager;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

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

  private static final Logger LOGGER = LoggerFactory.getLogger(MemoryAwareMessageBatch.class);
  private final List<MessageWithMeta> batch;

  private final long sizeInBytes;
  private final GlobalMemoryManager memoryManager;
  private final GlobalAsyncStateManager stateManager;

  public MemoryAwareMessageBatch(final List<MessageWithMeta> batch,
                                 final long sizeInBytes,
                                 final GlobalMemoryManager memoryManager,
                                 final GlobalAsyncStateManager stateManager) {
    this.batch = batch;
    this.sizeInBytes = sizeInBytes;
    this.memoryManager = memoryManager;
    this.stateManager = stateManager;
  }

  public long getSizeInBytes() {
    return sizeInBytes;
  }

  public List<MessageWithMeta> getData() {
    return batch;
  }

  @Override
  public void close() throws Exception {
    memoryManager.free(sizeInBytes);
  }

  /**
   * For the batch, marks all the states that have now been flushed. Also returns states that can be
   * flushed. This method is descriptrive, it assumes that whatever consumes the state messages emits
   * them, internally it purges the states it returns. message that it can.
   * <p>
   *
   * @return list of states that can be flushed
   */
  public List<PartialAirbyteMessage> flushStates(final Map<Long, Long> stateIdToCount) {
    stateIdToCount.forEach(stateManager::decrement);
    return stateManager.flushStates();
  }

}
