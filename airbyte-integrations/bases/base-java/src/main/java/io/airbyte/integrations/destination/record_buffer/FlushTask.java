package io.airbyte.integrations.destination.record_buffer;

import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.concurrent.Callable;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class FlushTask implements Callable<Void> {
  private static final Logger LOGGER = LoggerFactory.getLogger(FlushTask.class);

  private final FlushBufferFunction flushBufferFunction;
  private final AirbyteStreamNameNamespacePair stream;
  private final SerializableBuffer buffer;

  public FlushTask(final FlushBufferFunction flushBufferFunction, final AirbyteStreamNameNamespacePair stream, final SerializableBuffer buffer) {
    this.flushBufferFunction = flushBufferFunction;
    this.stream = stream;
    this.buffer = buffer;
  }

  @Override
  public Void call() throws Exception {
    LOGGER.info("Flushing buffer of stream {} ({})", stream.getName(), FileUtils.byteCountToDisplaySize(buffer.getByteCount()));
    flushBufferFunction.accept(stream, buffer);
    buffer.close();
    LOGGER.info("Flushing completed for {}", stream.getName());
    return null;
  }
}

