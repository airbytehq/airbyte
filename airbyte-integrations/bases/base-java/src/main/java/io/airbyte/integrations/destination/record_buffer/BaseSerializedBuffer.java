/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import com.google.common.io.CountingOutputStream;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
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
 * <p>
 * Such data format is defined by concrete implementation inheriting from this base abstract class.
 * To do so, necessary methods on handling "writer" methods should be defined. This writer would
 * take care of converting {@link AirbyteRecordMessage} into the serialized form of the data such as
 * it can be stored in the outputStream of the {@link BufferStorage}.
 */
public abstract class BaseSerializedBuffer implements SerializableBuffer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseSerializedBuffer.class);
  private static final String GZ_SUFFIX = ".gz";

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
  protected abstract void initWriter(OutputStream outputStream) throws Exception;

  /**
   * Transform the @param record into a serialized form of the data and writes it to the registered
   * OutputStream provided when {@link BaseSerializedBuffer#initWriter} was called.
   */
  @Deprecated
  protected abstract void writeRecord(AirbyteRecordMessage record) throws IOException;

  /**
   * TODO: (ryankfu) move destination to use serialized record string instead of passing entire
   * AirbyteRecord
   *
   * @param recordString serialized record
   * @param emittedAt timestamp of the record in milliseconds
   * @throws IOException
   */
  protected void writeRecord(final String recordString, final long emittedAt) throws IOException {
    writeRecord(Jsons.deserialize(recordString, AirbyteRecordMessage.class).withEmittedAt(emittedAt));
  }

  /**
   * Stops the writer from receiving new data and prepares it for being finalized and converted into
   * an InputStream to read from instead. This is used when flushing the buffer into some other
   * destination.
   */
  protected abstract void flushWriter() throws IOException;

  protected abstract void closeWriter() throws IOException;

  public SerializableBuffer withCompression(final boolean useCompression) {
    if (!isStarted) {
      this.useCompression = useCompression;
      return this;
    }
    throw new RuntimeException("Options should be configured before starting to write");
  }

  @Override
  public long accept(final AirbyteRecordMessage record) throws Exception {
    if (!isStarted) {
      if (useCompression) {
        compressedBuffer = new GzipCompressorOutputStream(byteCounter);
        initWriter(compressedBuffer);
      } else {
        initWriter(byteCounter);
      }
      isStarted = true;
    }
    if (inputStream == null && !isClosed) {
      final long startCount = byteCounter.getCount();
      writeRecord(record);
      return byteCounter.getCount() - startCount;
    } else {
      throw new IllegalCallerException("Buffer is already closed, it cannot accept more messages");
    }
  }

  @Override
  public long accept(final String recordString, final long emittedAt) throws Exception {
    if (!isStarted) {
      if (useCompression) {
        compressedBuffer = new GzipCompressorOutputStream(byteCounter);
        initWriter(compressedBuffer);
      } else {
        initWriter(byteCounter);
      }
      isStarted = true;
    }
    if (inputStream == null && !isClosed) {
      final long startCount = byteCounter.getCount();
      writeRecord(recordString, emittedAt);
      return byteCounter.getCount() - startCount;
    } else {
      throw new IllegalCallerException("Buffer is already closed, it cannot accept more messages");
    }
  }

  @Override
  public String getFilename() throws IOException {
    if (useCompression && !bufferStorage.getFilename().endsWith(GZ_SUFFIX)) {
      return bufferStorage.getFilename() + GZ_SUFFIX;
    }
    return bufferStorage.getFilename();
  }

  @Override
  public File getFile() throws IOException {
    if (useCompression && !bufferStorage.getFilename().endsWith(GZ_SUFFIX)) {
      if (bufferStorage.getFile().renameTo(new File(bufferStorage.getFilename() + GZ_SUFFIX))) {
        LOGGER.info("Renaming compressed file to include .gz file extension");
      }
    }
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
      flushWriter();
      if (compressedBuffer != null) {
        LOGGER.debug("Wrapping up compression and write GZIP trailer data.");
        compressedBuffer.flush();
        compressedBuffer.close();
      }
      closeWriter();
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
      // inputStream can be null if the accept method encounters
      // an error before inputStream is initialized
      if (inputStream != null) {
        inputStream.close();
      }
      bufferStorage.deleteFile();
      isClosed = true;
    }
  }

  @Override
  public long getMaxTotalBufferSizeInBytes() {
    return bufferStorage.getMaxTotalBufferSizeInBytes();
  }

  @Override
  public long getMaxPerStreamBufferSizeInBytes() {
    return bufferStorage.getMaxPerStreamBufferSizeInBytes();
  }

  @Override
  public int getMaxConcurrentStreamsInBuffer() {
    return bufferStorage.getMaxConcurrentStreamsInBuffer();
  }

}
