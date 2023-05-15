/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.destination.buffered_stream_consumer.RecordSizeEstimator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AsyncStreamConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(AsyncStreamConsumer.class);

  private static final String NON_STREAM_STATE_IDENTIFIER = "GLOBAL";
  private final BufferManagerEnqueue bufferManagerEnqueue;
  private final UploadWorkers uploadWorkers;

  public AsyncStreamConsumer(final BufferManager bufferManager) {
    bufferManagerEnqueue = bufferManager.getBufferManagerEnqueue();
    uploadWorkers = new UploadWorkers(bufferManager.getBufferManagerDequeue());
  }

  @Override
  public void start() throws Exception {
    uploadWorkers.start();
  }

  @Override
  public void accept(final AirbyteMessage message) throws Exception {
    /*
     * intentionally putting extractStream outside the buffer manager so that if in the future we want
     * to try to use a threadpool to partial deserialize to get record type and stream name, we can do
     * it without touching buffer manager.
     */
    extractStream(message)
        .ifPresent(streamDescriptor -> bufferManagerEnqueue.addRecord(streamDescriptor, message));
  }

  @Override
  public void close() throws Exception {
    // assume the closing upload workers will flush all accepted records.
    uploadWorkers.close();
  }

  // todo (cgardens) - handle global state.
  /**
   * Extract the stream from the message, ff the message is a record or state. Otherwise, we don't
   * care.
   *
   * @param message message to extract stream from
   * @return stream descriptor if the message is a record or state, otherwise empty. In the case of
   *         global state messages the stream descriptor is hardcoded
   */
  private static Optional<StreamDescriptor> extractStream(final AirbyteMessage message) {
    if (message.getType() == Type.RECORD) {
      return Optional.of(new StreamDescriptor().withNamespace(message.getRecord().getNamespace()).withName(message.getRecord().getStream()));
    } else if (message.getType() == Type.STATE) {
      if (message.getState().getType() == AirbyteStateType.STREAM) {
        return Optional.of(message.getState().getStream().getStreamDescriptor());
      } else {
        return Optional.of(new StreamDescriptor().withNamespace(NON_STREAM_STATE_IDENTIFIER).withNamespace(NON_STREAM_STATE_IDENTIFIER));
      }
    } else {
      return Optional.empty();
    }
  }

  static class BufferManager {

    Map<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers;

    BufferManagerEnqueue bufferManagerEnqueue;
    BufferManagerDequeue bufferManagerDequeue;

    public BufferManager() {
      buffers = new HashMap<>();
      bufferManagerEnqueue = new BufferManagerEnqueue(buffers);
      bufferManagerDequeue = new BufferManagerDequeue(buffers);
    }

    public BufferManagerEnqueue getBufferManagerEnqueue() {
      return bufferManagerEnqueue;
    }

    public BufferManagerDequeue getBufferManagerDequeue() {
      return bufferManagerDequeue;
    }

  }

  static class BufferManagerEnqueue {

    private final RecordSizeEstimator recordSizeEstimator;
    private final Map<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers;

    public BufferManagerEnqueue(final Map<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers) {
      this.buffers = buffers;
      recordSizeEstimator = new RecordSizeEstimator();
    }

    public void addRecord(final StreamDescriptor streamDescriptor, final AirbyteMessage message) {
      // todo (cgardens) - share the total memory across multiple queues.
      final long availableMemory = (long) (Runtime.getRuntime().maxMemory() * 0.8);
      LOGGER.info("available memory: " + availableMemory);

      // todo (cgardens) - replace this with fancy logic to make sure we don't oom.
      if (!buffers.containsKey(streamDescriptor)) {
        buffers.put(streamDescriptor, new MemoryBoundedLinkedBlockingQueue<>(10)); // todo
      }

      // todo (cgardens) - handle estimating state message size.
      final long messageSize = message.getType() == Type.RECORD ? recordSizeEstimator.getEstimatedByteSize(message.getRecord()) : 1024;
      buffers.get(streamDescriptor).offer(message, messageSize);
    }

  }

  // todo (cgardens) - make all the metadata methods more efficient.
  static class BufferManagerDequeue {

    Map<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers;

    public BufferManagerDequeue(final Map<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> buffers) {
      this.buffers = buffers;
    }

    public Map<StreamDescriptor, MemoryBoundedLinkedBlockingQueue<AirbyteMessage>> getBuffers() {
      return new HashMap<>(buffers);
    }

    public MemoryBoundedLinkedBlockingQueue<AirbyteMessage> getBuffer(final StreamDescriptor streamDescriptor) {
      return buffers.get(streamDescriptor);
    }

    public long getTotalGlobalQueueSizeInMb() {
      return buffers.values().stream().map(MemoryBoundedLinkedBlockingQueue::getCurrentMemoryUsage).mapToLong(Long::longValue).sum();
    }

    public long getQueueSizeInMb(final StreamDescriptor streamDescriptor) {
      return getBuffer(streamDescriptor).getCurrentMemoryUsage();
    }

    public Optional<Instant> getTimeOfLastRecord(final StreamDescriptor streamDescriptor) {
      return getBuffer(streamDescriptor).getTimeOfLastMessage();
    }

  }

  /**
   * In charge of looking for records in queues and efficiently getting those records uploaded.
   */
  static class UploadWorkers implements AutoCloseable {

    private final BufferManagerDequeue bufferManagerDequeue;

    public UploadWorkers(final BufferManagerDequeue bufferManagerDequeue) {
      this.bufferManagerDequeue = bufferManagerDequeue;
    }

    public void start() {

    }

    @Override
    public void close() throws Exception {

    }

  }

}
