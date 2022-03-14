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
import java.net.URISyntaxException;
import org.apache.commons.compress.compressors.gzip.GzipCompressorOutputStream;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class BaseRecordBufferImplementation implements RecordBufferImplementation {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseRecordBufferImplementation.class);

  private final RecordBufferStorage bufferStorage;
  private final CountingOutputStream byteCounter;
  private final GzipCompressorOutputStream compressedBuffer;

  private InputStream inputStream;
  private boolean isClosed;

  protected BaseRecordBufferImplementation(final RecordBufferStorage bufferStorage, final boolean withCompression) throws Exception {
    this.bufferStorage = bufferStorage;
    byteCounter = new CountingOutputStream(bufferStorage.getOutputStream());
    compressedBuffer = new GzipCompressorOutputStream(byteCounter);
    if (withCompression) {
      createWriter(compressedBuffer);
    } else {
      createWriter(byteCounter);
    }
    inputStream = null;
    isClosed = false;
  }

  protected abstract void createWriter(OutputStream outputStream) throws IOException, URISyntaxException;

  protected abstract void writeRecord(AirbyteRecordMessage recordMessage) throws IOException;

  protected abstract void closeWriter() throws IOException;

  @Override
  public Long accept(final AirbyteRecordMessage recordMessage) throws Exception {
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
      // we need to close the gzip stream to finish compression and write trailer data.
      compressedBuffer.close();
      bufferStorage.close();
      inputStream = convertToInputStream();
      LOGGER.info("Finished writing data to {} ({})", getFilename(), FileUtils.byteCountToDisplaySize(byteCounter.getCount()));
    }
  }

  @Override
  public Long getCount() {
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

  public Long getMaxTotalBufferSizeInBytes() {
    return bufferStorage.getMaxTotalBufferSizeInBytes();
  }

  public Long getMaxPerStreamBufferSizeInBytes() {
    return bufferStorage.getMaxPerStreamBufferSizeInBytes();
  }

  public int getMaxConcurrentStreamsInBuffer() {
    return bufferStorage.getMaxConcurrentStreamsInBuffer();
  }

}
