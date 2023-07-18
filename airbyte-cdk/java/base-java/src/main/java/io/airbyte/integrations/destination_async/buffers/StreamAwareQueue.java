/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.buffers;

import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteMessage;
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
    // if the queue is empty, the time of last message is irrelevant
    if (size() == 0) {
      return Optional.empty();
    }
    return Optional.ofNullable(timeOfLastMessage.get());
  }

  public Optional<MemoryBoundedLinkedBlockingQueue.MemoryItem<MessageWithMeta>> peek() {
    return Optional.ofNullable(memoryAwareQueue.peek());
  }

  public int size() {
    return memoryAwareQueue.size();
  }

  public boolean offer(final PartialAirbyteMessage message, final long messageSizeInBytes, final long stateId) {
    if (memoryAwareQueue.offer(new MessageWithMeta(message, stateId), messageSizeInBytes)) {
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

  public record MessageWithMeta(PartialAirbyteMessage message, long stateId) {}

}
