/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import java.util.concurrent.atomic.AtomicLong;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class GlobalMemoryManager {

  private static final long BLOCK_SIZE_BYTES = 10 * 1024 * 1024; // 10MB
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

  public synchronized long requestMemory() {
    if (currentMemoryBytes.get() >= maxMemoryBytes) {
      return 0L;
    }

    final var freeMem = maxMemoryBytes - currentMemoryBytes.get();
    // Never allocate more than free memory size.
    final var toAllocateBytes = Math.min(freeMem, BLOCK_SIZE_BYTES);
    currentMemoryBytes.addAndGet(toAllocateBytes);

    return toAllocateBytes;
  }

  public void free(final long bytes) {
    currentMemoryBytes.addAndGet(-bytes);

    if (currentMemoryBytes.get() < 0) {
      log.warn("Freed more memory than allocated. This should never happen. Please report this bug.");
    }
  }

}
