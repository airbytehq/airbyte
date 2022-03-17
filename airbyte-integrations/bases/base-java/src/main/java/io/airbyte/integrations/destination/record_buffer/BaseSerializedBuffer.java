/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import com.google.common.io.CountingOutputStream;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import org.apache.commons.compress.compressors.gzip.GzipCompressorOutputStream;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Base implementation of a {@link SerializableBuffer}. It is composed of a {@link BufferStorage}
 * where the actual data is being stored in a serialized format.
 *
 * Such data format is defined by concrete implementation inheriting from this base abstract class.
 * To do so, necessary methods on handling "writer" methods should be defined. This writer would
 * take care of converting {@link AirbyteRecordMessage} into the serialized form of the data such as
 * it can be stored in the outputStream of the {@link BufferStorage}.
 */
public abstract class BaseSerializedBuffer implements SerializableBuffer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseSerializedBuffer.class);

  private final BufferStorage bufferStorage;
  private final CountingOutputStream byteCounter;

  private boolean useCompression;
  private GzipCompressorOutputStream compressedBuffer;
  private InputStream inputStream;
  private boolean isStarted;
  private boolean isClosed;

  protected BaseSerializedBuffer(final BufferStorage bufferStorage) throws Exception {
    this.bufferStorage = bufferStorage;
    byteCounter = new CountingOutputStream(bufferStorage.getOutputStream());
    useCompression = true;
    compressedBuffer = null;
    inputStream = null;
    isStarted = false;
    isClosed = false;
  }

  /**
   * Initializes the writer objects such that it can now write to the downstream @param outputStream
   */
  protected abstract void createWriter(OutputStream outputStream) throws Exception;

  /**
   * Transform the @param recordMessage into a serialized form of the data and writes it to the
   * registered OutputStream provided when {@link BaseSerializedBuffer#createWriter} was called.
   */
  protected abstract void writeRecord(AirbyteRecordMessage recordMessage) throws IOException;

  /**
   * Stops the writer from receiving new data and prepares it for being finalized and converted into
   * an InputStream to read from instead. This is used when flushing the buffer into some other
   * destination.
   */
  protected abstract void closeWriter() throws IOException;

  public SerializableBuffer withCompression(final boolean useCompression) {
    if (!isStarted) {
      this.useCompression = useCompression;
      return this;
    }
    throw new RuntimeException("Options should be configured before starting to write");
  }

  @Override
  public long accept(final AirbyteRecordMessage recordMessage) throws Exception {
    if (!isStarted) {
      if (useCompression) {
        compressedBuffer = new GzipCompressorOutputStream(byteCounter);
        createWriter(compressedBuffer);
      } else {
        createWriter(byteCounter);
      }
      isStarted = true;
    }
    if (inputStream == null && !isClosed) {
      final long startCount = byteCounter.getCount();
      writeRecord(recordMessage);
      return byteCounter.getCount() - startCount;
    } else {
      throw new IllegalCallerException("Buffer is already closed, it cannot accept more messages");
    }
  }

  public String getFilename() throws IOException {
    return bufferStorage.getFilename();
  }

  public File getFile() throws IOException {
    return bufferStorage.getFile();
  }

  protected InputStream convertToInputStream() throws IOException {
    return bufferStorage.convertToInputStream();
  }

  @Override
  public InputStream getInputStream() {
    return inputStream;
  }

  @Override
  public void flush() throws IOException {
    if (inputStream == null && !isClosed) {
      closeWriter();
      if (compressedBuffer != null) {
        // we need to close the gzip stream to finish compression and write trailer data.
        compressedBuffer.close();
      }
      bufferStorage.close();
      inputStream = convertToInputStream();
      LOGGER.info("Finished writing data to {} ({})", getFilename(), FileUtils.byteCountToDisplaySize(byteCounter.getCount()));
    }
  }

  @Override
  public long getByteCount() {
    return byteCounter.getCount();
  }

  @Override
  public void close() throws Exception {
    if (!isClosed) {
      inputStream.close();
      bufferStorage.deleteFile();
      isClosed = true;
    }
  }

  public long getMaxTotalBufferSizeInBytes() {
    return bufferStorage.getMaxTotalBufferSizeInBytes();
  }

  public long getMaxPerStreamBufferSizeInBytes() {
    return bufferStorage.getMaxPerStreamBufferSizeInBytes();
  }

  public int getMaxConcurrentStreamsInBuffer() {
    return bufferStorage.getMaxConcurrentStreamsInBuffer();
  }

}
