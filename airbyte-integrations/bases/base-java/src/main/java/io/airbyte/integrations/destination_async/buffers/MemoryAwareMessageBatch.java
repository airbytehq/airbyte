/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import com.google.common.base.Preconditions;
import io.airbyte.integrations.destination_async.GlobalMemoryManager;
import io.airbyte.integrations.destination_async.state.AsyncStateManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.List;
import java.util.Optional;
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

  private final StreamDescriptor streamDescriptor;
  private List<AirbyteMessage> batch;
  private final long sizeInBytes;
  private final GlobalMemoryManager memoryManager;
  private final AsyncStateManager stateManager;
  private final long minMessageNum;
  private final long maxMessageNum;

  private boolean hasCommittedState;

  public MemoryAwareMessageBatch(final StreamDescriptor streamDescriptor,
                                 final List<AirbyteMessage> batch,
                                 final long sizeInBytes,
                                 final long minMessageNum,
                                 final long maxMessageNum,
                                 final GlobalMemoryManager memoryManager,
                                 final AsyncStateManager stateManager) {
    this.streamDescriptor = streamDescriptor;
    this.batch = batch;
    this.sizeInBytes = sizeInBytes;
    this.minMessageNum = minMessageNum;
    this.maxMessageNum = maxMessageNum;
    this.memoryManager = memoryManager;
    this.stateManager = stateManager;
    hasCommittedState = false;
    // stateManager.claim(streamDescriptor, maxMessageNum);
  }

  public List<AirbyteMessage> getData() {
    return batch;
  }

  @Override
  public void close() throws Exception {
    if (!hasCommittedState) {
      LOGGER.warn("Batch closed without committing state.");
    }
    batch = null;
    memoryManager.free(sizeInBytes);
  }

  /**
   * For the batch, marks all the states that have now been flushed. Also returns the best state
   * message that it can.
   * <p>
   * This method is destructive! It must called once per batch.
   *
   * @return
   */
  public Optional<AirbyteMessage> commitState() {
    Preconditions.checkArgument(!hasCommittedState, "This method can only be called once.");
    hasCommittedState = true;
    return null;
    // return stateManager.flushStates();
  }

}
