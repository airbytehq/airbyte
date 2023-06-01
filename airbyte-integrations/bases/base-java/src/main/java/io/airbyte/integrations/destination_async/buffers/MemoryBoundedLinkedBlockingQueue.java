/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import javax.annotation.Nonnull;
import lombok.extern.slf4j.Slf4j;

/**
 * This class is meant to emulate the behavior of a LinkedBlockingQueue, but instead of being
 * bounded on number of items in the queue, it is bounded by the memory it is allowed to use. The
 * amount of memory it is allowed to use can be resized after it is instantiated.
 * <p>
 * This class intentionally hides the underlying queue inside of it. For this class to work, it has
 * to override each method on a queue that adds or removes records from the queue. The Queue
 * interface has a lot of methods to override, and we don't want to spend the time overriding a lot
 * of methods that won't be used. By hiding the queue, we avoid someone accidentally using a queue
 * method that has not been modified. If you need access to another of the queue methods, pattern
 * match adding the memory tracking as seen in {@link HiddenQueue}, and then delegate to that method
 * from this top-level class.
 *
 * @param <E> type in the queue
 */
@Slf4j
class MemoryBoundedLinkedBlockingQueue<E> {

  private final HiddenQueue<E> hiddenQueue;

  public MemoryBoundedLinkedBlockingQueue(final long maxMemoryUsage) {
    hiddenQueue = new HiddenQueue<>(maxMemoryUsage);
  }

  public long getCurrentMemoryUsage() {
    return hiddenQueue.currentMemoryUsage.get();
  }

  public void addMaxMemory(final long maxMemoryUsage) {
    hiddenQueue.maxMemoryUsage.addAndGet(maxMemoryUsage);
  }

  public int size() {
    return hiddenQueue.size();
  }

  public boolean offer(final E e, final long itemSizeInBytes) {
    return hiddenQueue.offer(e, itemSizeInBytes);
  }

  public MemoryBoundedLinkedBlockingQueue.MemoryItem<E> peek() {
    return hiddenQueue.peek();
  }

  public MemoryBoundedLinkedBlockingQueue.MemoryItem<E> take() throws InterruptedException {
    return hiddenQueue.take();
  }

  public MemoryBoundedLinkedBlockingQueue.MemoryItem<E> poll() {
    return hiddenQueue.poll();
  }

  public MemoryBoundedLinkedBlockingQueue.MemoryItem<E> poll(final long timeout, final TimeUnit unit) throws InterruptedException {
    return hiddenQueue.poll(timeout, unit);
  }

  /**
   * Extends LinkedBlockingQueue so that we can get a LinkedBlockingQueue bounded by memory. Hidden as
   * an inner class, so it doesn't get misused, see top-level javadoc comment.
   *
   * @param <E>
   */
  private static class HiddenQueue<E> extends LinkedBlockingQueue<MemoryBoundedLinkedBlockingQueue.MemoryItem<E>> {

    private final AtomicLong currentMemoryUsage;
    private final AtomicLong maxMemoryUsage;

    public HiddenQueue(final long maxMemoryUsage) {
      currentMemoryUsage = new AtomicLong(0);
      this.maxMemoryUsage = new AtomicLong(maxMemoryUsage);
    }

    public boolean offer(final E e, final long itemSizeInBytes) {
      final long newMemoryUsage = currentMemoryUsage.addAndGet(itemSizeInBytes);
      if (newMemoryUsage <= maxMemoryUsage.get()) {
        final boolean success = super.offer(new MemoryItem<>(e, itemSizeInBytes));
        if (!success) {
          currentMemoryUsage.addAndGet(-itemSizeInBytes);
        }
        log.debug("offer status: {}", success);
        return success;
      } else {
        currentMemoryUsage.addAndGet(-itemSizeInBytes);
        log.debug("offer failed");
        return false;
      }
    }

    @Nonnull
    @Override
    public MemoryBoundedLinkedBlockingQueue.MemoryItem<E> take() throws InterruptedException {
      final MemoryItem<E> memoryItem = super.take();
      currentMemoryUsage.addAndGet(-memoryItem.size());
      return memoryItem;
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

    @Override
    public MemoryBoundedLinkedBlockingQueue.MemoryItem<E> poll(final long timeout, final TimeUnit unit) throws InterruptedException {
      final MemoryItem<E> memoryItem = super.poll(timeout, unit);
      if (memoryItem != null) {
        currentMemoryUsage.addAndGet(-memoryItem.size());
        return memoryItem;
      }
      return null;
    }

  }

  public record MemoryItem<E> (E item, long size) {}

}
