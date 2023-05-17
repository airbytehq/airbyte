/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import java.time.Instant;
import java.util.Optional;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class MemoryBoundedLinkedBlockingQueue<E> extends LinkedBlockingQueue<MemoryBoundedLinkedBlockingQueue.MemoryItem<E>> {

  private final AtomicLong currentMemoryUsage;
  private final AtomicLong maxMemoryUsage;

  private final AtomicReference<Instant> timeOfLastMessage;

  public MemoryBoundedLinkedBlockingQueue(final long maxMemoryUsage) {
    currentMemoryUsage = new AtomicLong(0);
    this.maxMemoryUsage = new AtomicLong(maxMemoryUsage);
    timeOfLastMessage = new AtomicReference(null);
  }

  public long getCurrentMemoryUsage() {
    return currentMemoryUsage.get();
  }

  public long getMaxMemoryUsage() {
    return maxMemoryUsage.get();
  }

  public void setMaxMemoryUsage(final long maxMemoryUsage) {
    this.maxMemoryUsage.set(maxMemoryUsage);
  }

  public Optional<Instant> getTimeOfLastMessage() {
    return Optional.ofNullable(timeOfLastMessage.get());
  }

  public boolean offer(final E e, final long itemSizeInBytes) {
    final long newMemoryUsage = currentMemoryUsage.addAndGet(itemSizeInBytes);
    if (newMemoryUsage <= maxMemoryUsage.get()) {
      final boolean success = super.offer(new MemoryItem<>(e, itemSizeInBytes));
      if (!success) {
        currentMemoryUsage.addAndGet(-itemSizeInBytes);
      } else {
        // it succeeded!
        timeOfLastMessage.set(Instant.now());
      }
      log.debug("offer status: {}", success);
      return success;
    } else {
      currentMemoryUsage.addAndGet(-itemSizeInBytes);
      log.debug("offer failed");
      return false;
    }
  }

  @Override
  public MemoryBoundedLinkedBlockingQueue.MemoryItem<E> take() throws InterruptedException {
    final MemoryItem<E> memoryItem = super.take();
    if (memoryItem != null) {
      currentMemoryUsage.addAndGet(-memoryItem.size());
      return memoryItem;
    }
    return null;
  }

  @Override
  public MemoryBoundedLinkedBlockingQueue.MemoryItem<E> poll() {
    final MemoryItem<E> memoryItem = super.poll();
    if (memoryItem != null) {
      currentMemoryUsage.addAndGet(-memoryItem.size());
      return memoryItem;
    }
    return null;
  }

  public record MemoryItem<E> (E item, long size) {}

}
