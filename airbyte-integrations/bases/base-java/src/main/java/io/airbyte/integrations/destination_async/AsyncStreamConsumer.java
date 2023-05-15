/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

public class AsyncStreamConsumer implements AirbyteMessageConsumer {

  private static final String NON_STREAM_STATE_IDENTIFIER = "GLOBAL";
  private final BufferManagerEnqueue bufferManagerEnqueue;
  private final UploadWorkers uploadWorkers;

  public AsyncStreamConsumer(final BufferManager bufferManager) {
    bufferManagerEnqueue = bufferManager.bufferManagerEnqueue;
    uploadWorkers = new UploadWorkers(bufferManager.bufferManagerDequeue);
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

    Map<StreamDescriptor, LinkedBlockingQueue<AirbyteMessage>> buffers;

    BufferManagerEnqueue bufferManagerEnqueue;
    BufferManagerDequeue bufferManagerDequeue;

    public BufferManager() {
      buffers = new HashMap<>();

    }

  }

  static class BufferManagerEnqueue {

    Map<StreamDescriptor, BlockingQueue<AirbyteMessage>> buffers;

    public BufferManagerEnqueue(final Map<StreamDescriptor, BlockingQueue<AirbyteMessage>> buffers) {
      this.buffers = buffers;
    }

    public void addRecord(final StreamDescriptor streamDescriptor, final AirbyteMessage message) {
      // todo (cgardens) - replace this with fancy logic to make sure we don't oom.
      if (!buffers.containsKey(streamDescriptor)) {
        buffers.put(streamDescriptor, new LinkedBlockingQueue<>());
      }
      buffers.get(streamDescriptor).add(message);
    }

  }

  static class BufferManagerDequeue {

    Map<StreamDescriptor, BlockingQueue<AirbyteMessage>> buffers;

    public BufferManagerDequeue(final Map<StreamDescriptor, BlockingQueue<AirbyteMessage>> buffers) {
      this.buffers = buffers;
    }

    // dequeue
    Map<StreamDescriptor, BlockingQueue<AirbyteMessage>> getBuffers() {
      return new HashMap<>(buffers);
    }

    BlockingQueue<AirbyteMessage> getQueue(final StreamDescriptor streamDescriptor) {
      return buffers.get(streamDescriptor);
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
