/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import io.airbyte.integrations.destination_async.buffers.MemoryBoundedLinkedBlockingQueue.MemoryItem;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.time.Instant;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class StreamAwareQueue {

  private final AtomicReference<Instant> timeOfLastMessage;
  private final AtomicLong minMessageNum;

  private final MemoryBoundedLinkedBlockingQueue<Meta> memoryAwareQueue;

  public StreamAwareQueue(final long maxMemoryUsage) {
    memoryAwareQueue = new MemoryBoundedLinkedBlockingQueue<>(maxMemoryUsage);
    timeOfLastMessage = new AtomicReference<>();
    minMessageNum = new AtomicLong();
  }

  public long getCurrentMemoryUsage() {
    return memoryAwareQueue.getCurrentMemoryUsage();
  }

  public void addMaxMemory(final long maxMemoryUsage) {
    memoryAwareQueue.addMaxMemory(maxMemoryUsage);
  }

  public Optional<Instant> getTimeOfLastMessage() {
    return Optional.ofNullable(timeOfLastMessage.get());
  }

  public long getMinMessageNum() {
    return minMessageNum.get();
  }

  // todo (make sure it gets set on first write).
  public void updateMinMessageNum() {
    if (memoryAwareQueue.peek() != null) {
      minMessageNum.set(memoryAwareQueue.peek().item().messageNum());
    }
  }

  public Optional<Meta> peek() {
    return Optional.ofNullable(memoryAwareQueue.peek()).map(MemoryItem::item);
  }

  public int size() {
    return memoryAwareQueue.size();
  }

  public boolean offer(final AirbyteMessage message, final long messageNum, final long itemSizeInBytes) {
    if (memoryAwareQueue.offer(new Meta(message, messageNum), itemSizeInBytes)) {
      timeOfLastMessage.set(Instant.now());
      return true;
    } else {
      return false;
    }
  }

  public MemoryBoundedLinkedBlockingQueue.MemoryItem<Meta> take() throws InterruptedException {
    return memoryAwareQueue.take();
  }

  public MemoryBoundedLinkedBlockingQueue.MemoryItem<Meta> poll() {
    return memoryAwareQueue.poll();
  }

  public MemoryBoundedLinkedBlockingQueue.MemoryItem<Meta> poll(final long timeout, final TimeUnit unit) throws InterruptedException {
    return memoryAwareQueue.poll(timeout, unit);
  }

  public record Meta(AirbyteMessage message, long messageNum) {}

}
