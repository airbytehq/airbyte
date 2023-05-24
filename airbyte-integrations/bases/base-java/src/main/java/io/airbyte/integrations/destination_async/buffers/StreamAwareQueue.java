/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import io.airbyte.integrations.destination_async.buffers.MemoryBoundedLinkedBlockingQueue.MemoryItem;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.time.Instant;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class StreamAwareQueue {

  private final AtomicReference<Instant> timeOfLastMessage;

  private final MemoryBoundedLinkedBlockingQueue<MessageWithMeta> memoryAwareQueue;

  public StreamAwareQueue(final long maxMemoryUsage) {
    memoryAwareQueue = new MemoryBoundedLinkedBlockingQueue<>(maxMemoryUsage);
    timeOfLastMessage = new AtomicReference<>();
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

  public Optional<MessageWithMeta> peek() {
    return Optional.ofNullable(memoryAwareQueue.peek()).map(MemoryItem::item);
  }

  public int size() {
    return memoryAwareQueue.size();
  }

  public boolean offer(final AirbyteMessage message, final long messageNum, final long stateId) {
    if (memoryAwareQueue.offer(new MessageWithMeta(message, messageNum), stateId)) {
      timeOfLastMessage.set(Instant.now());
      return true;
    } else {
      return false;
    }
  }

  public MemoryBoundedLinkedBlockingQueue.MemoryItem<MessageWithMeta> take() throws InterruptedException {
    return memoryAwareQueue.take();
  }

  public MemoryBoundedLinkedBlockingQueue.MemoryItem<MessageWithMeta> poll() {
    return memoryAwareQueue.poll();
  }

  public MemoryBoundedLinkedBlockingQueue.MemoryItem<MessageWithMeta> poll(final long timeout, final TimeUnit unit) throws InterruptedException {
    return memoryAwareQueue.poll(timeout, unit);
  }

  public record MessageWithMeta(AirbyteMessage message, long stateId) {}

}
