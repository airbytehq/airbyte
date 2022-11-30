/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Instead of storing buffered data on disk like the {@link FileBuffer}, this {@link BufferStorage}
 * accumulates message data in-memory instead. Thus, a bigger heap size would be required.
 */
public class InMemoryBuffer implements BufferStorage {

  private static final Logger LOGGER = LoggerFactory.getLogger(InMemoryBuffer.class);

  // The per stream size limit is following recommendations from:
  // https://docs.snowflake.com/en/user-guide/data-load-considerations-prepare.html#general-file-sizing-recommendations
  // "To optimize the number of parallel operations for a load,
  // we recommend aiming to produce data files roughly 100-250 MB (or larger) in size compressed."
  public static final long MAX_PER_STREAM_BUFFER_SIZE_BYTES = 200 * 1024 * 1024; // mb
  // Other than the per-file size limit, we also limit the total size (which would limit how many
  // concurrent streams we can buffer simultaneously too)
  // Since this class is storing data in memory, the buffer size limits below are tied to the
  // necessary RAM space.
  public static final long MAX_TOTAL_BUFFER_SIZE_BYTES = 1024 * 1024 * 1024; // mb
  // we limit number of stream being buffered simultaneously anyway
  public static final int MAX_CONCURRENT_STREAM_IN_BUFFER = 100;

  private final String fileExtension;
  private final ByteArrayOutputStream byteBuffer = new ByteArrayOutputStream();
  private File tempFile;
  private String filename;

  public InMemoryBuffer(final String fileExtension) {
    this.fileExtension = fileExtension;
    tempFile = null;
    filename = null;
  }

  @Override
  public OutputStream getOutputStream() {
    return byteBuffer;
  }

  @Override
  public String getFilename() {
    if (filename == null) {
      filename = UUID.randomUUID().toString();
    }
    return filename;
  }

  @Override
  public File getFile() throws IOException {
    if (tempFile == null) {
      tempFile = Files.createTempFile(getFilename(), fileExtension).toFile();
    }
    return tempFile;
  }

  @Override
  public InputStream convertToInputStream() {
    return new ByteArrayInputStream(byteBuffer.toByteArray());
  }

  @Override
  public void close() throws IOException {
    byteBuffer.close();
  }

  @Override
  public void deleteFile() throws IOException {
    if (tempFile != null) {
      LOGGER.info("Deleting tempFile data {}", getFilename());
      Files.deleteIfExists(tempFile.toPath());
    }
  }

  @Override
  public long getMaxTotalBufferSizeInBytes() {
    return MAX_TOTAL_BUFFER_SIZE_BYTES;
  }

  @Override
  public long getMaxPerStreamBufferSizeInBytes() {
    return MAX_PER_STREAM_BUFFER_SIZE_BYTES;
  }

  @Override
  public int getMaxConcurrentStreamsInBuffer() {
    return MAX_CONCURRENT_STREAM_IN_BUFFER;
  }

}
