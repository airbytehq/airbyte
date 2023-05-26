/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import java.util.concurrent.atomic.AtomicLong;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.FileUtils;

/**
 * Responsible for managing global memory across multiple queues in a thread-safe way.
 * <p>
 * This means memory allocation and de-allocation for each queue can be dynamically adjusted
 * according to the overall available memory. Memory blocks are managed in chunks of
 * {@link #BLOCK_SIZE_BYTES}, and the total amount of memory managed is configured at creation time.
 * <p>
 * As a destination has no information about incoming per-stream records, having static non-global
 * queue sizes can cause unnecessary backpressure on a per-stream basis. By providing a dynamic,
 * global view of memory management, this class allows each queue to free and consume memory
 * dynamically, enabling effective sharing of global memory resources across all the queues. and
 * avoiding accidental stream backpressure.
 * <p>
 * This becomes particularly useful in the following scenarios:
 * <ul>
 * <li>1. When the incoming records belong to a single stream. Dynamic allocation ensures this one
 * stream can utilise all memory.</li>
 * <li>2. When the incoming records are from multiple streams, such as with Change Data Capture
 * (CDC). Here, dynamic allocation let us create as many queues as possible, allowing all streams to
 * be processed in parallel without accidental backpressure from unnecessary eager flushing.</li>
 * </ul>
 */
@Slf4j
public class GlobalMemoryManager {

  // In cases where a queue is rapidly expanding, a larger block size allows less allocation calls. On
  // the flip size, a smaller block size allows more granular memory management. Since this overhead
  // is minimal for now, err on a smaller block sizes.
  public static final long BLOCK_SIZE_BYTES = 10 * 1024 * 1024; // 10MB
  private final long maxMemoryBytes;

  private final AtomicLong currentMemoryBytes = new AtomicLong(0);

  public GlobalMemoryManager(final long maxMemoryBytes) {
    this.maxMemoryBytes = maxMemoryBytes;
  }

  public long getMaxMemoryBytes() {
    return maxMemoryBytes;
  }

  public long getCurrentMemoryBytes() {
    return currentMemoryBytes.get();
  }

  /**
   * Requests a block of memory of {@link #BLOCK_SIZE_BYTES}. Return 0 if memory cannot be freed.
   *
   * @return the size of the allocated block, in bytes
   */
  public synchronized long requestMemory() {
    // todo(davin): what happens if the incoming record is larger than 10MB?
    if (currentMemoryBytes.get() >= maxMemoryBytes) {
      return 0L;
    }

    final var freeMem = maxMemoryBytes - currentMemoryBytes.get();
    // Never allocate more than free memory size.
    final var toAllocateBytes = Math.min(freeMem, BLOCK_SIZE_BYTES);
    currentMemoryBytes.addAndGet(toAllocateBytes);

    log.debug("Memory Requested: max: {}, allocated: {}, allocated in this request: {}",
        FileUtils.byteCountToDisplaySize(maxMemoryBytes),
        FileUtils.byteCountToDisplaySize(currentMemoryBytes.get()),
        FileUtils.byteCountToDisplaySize(toAllocateBytes));
    return toAllocateBytes;
  }

  /**
   * Frees a block of memory of the given size. If the amount of memory freed exceeds the current
   * memory allocation, a warning will be logged.
   *
   * @param bytes the size of the block to free, in bytes
   */
  public void free(final long bytes) {
    log.info("Freeing {} bytes..", bytes);
    currentMemoryBytes.addAndGet(-bytes);

    if (currentMemoryBytes.get() < 0) {
      log.warn("Freed more memory than allocated. This should never happen. Please report this bug.");
    }
  }

}
