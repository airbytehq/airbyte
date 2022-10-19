/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class FileBuffer implements BufferStorage {

  private static final Logger LOGGER = LoggerFactory.getLogger(FileBuffer.class);

  // The per stream size limit is following recommendations from:
  // https://docs.snowflake.com/en/user-guide/data-load-considerations-prepare.html#general-file-sizing-recommendations
  // "To optimize the number of parallel operations for a load,
  // we recommend aiming to produce data files roughly 100-250 MB (or larger) in size compressed."
  public static final long MAX_PER_STREAM_BUFFER_SIZE_BYTES = 200 * 1024 * 1024; // mb
  // Other than the per-file size limit, we also limit the total size (which would limit how many
  // concurrent streams we can buffer simultaneously too)
  // Since this class is storing data on disk, the buffer size limits below are tied to the
  // necessary disk storage space.
  public static final long MAX_TOTAL_BUFFER_SIZE_BYTES = 1024 * 1024 * 1024; // mb
  // we limit number of stream being buffered simultaneously anyway (limit how many files are
  // stored/open for writing)
  public static final int DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER = 10;

  private final String fileExtension;
  private File tempFile;
  private OutputStream outputStream;
  private final int maxConcurrentStreams;

  public FileBuffer(final String fileExtension) {
    this.fileExtension = fileExtension;
    this.maxConcurrentStreams = DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER;
    tempFile = null;
    outputStream = null;
  }

  public FileBuffer(final String fileExtension, final int maxConcurrentStreams) {
    this.fileExtension = fileExtension;
    this.maxConcurrentStreams = maxConcurrentStreams;
    tempFile = null;
    outputStream = null;
  }

  @Override
  public OutputStream getOutputStream() throws IOException {
    if (outputStream == null || tempFile == null) {
      tempFile = Files.createTempFile(UUID.randomUUID().toString(), fileExtension).toFile();
      outputStream = new BufferedOutputStream(new FileOutputStream(tempFile));
    }
    return outputStream;
  }

  @Override
  public String getFilename() throws IOException {
    return getFile().getName();
  }

  @Override
  public File getFile() throws IOException {
    if (tempFile == null) {
      getOutputStream();
    }
    return tempFile;
  }

  @Override
  public InputStream convertToInputStream() throws IOException {
    return new FileInputStream(getFile());
  }

  @Override
  public void close() throws IOException {
    outputStream.close();
  }

  @Override
  public void deleteFile() throws IOException {
    LOGGER.info("Deleting tempFile data {}", getFilename());
    Files.deleteIfExists(getFile().toPath());
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
    return maxConcurrentStreams;
  }

}
