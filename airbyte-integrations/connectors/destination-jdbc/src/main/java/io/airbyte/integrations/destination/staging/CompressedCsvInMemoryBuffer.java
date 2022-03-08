/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.staging;

import com.google.common.io.CountingOutputStream;
import io.airbyte.integrations.destination.buffered_stream_consumer.RecordBufferImplementation;
import io.airbyte.integrations.destination.s3.csv.CsvSheetGenerator;
import io.airbyte.integrations.destination.s3.csv.StagingDatabaseCsvSheetGenerator;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.UUID;
import org.apache.commons.compress.compressors.gzip.GzipCompressorOutputStream;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CompressedCsvInMemoryBuffer implements RecordBufferImplementation {

  private static final Logger LOGGER = LoggerFactory.getLogger(CompressedCsvInMemoryBuffer.class);

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

  private final ByteArrayOutputStream byteBuffer;
  private final CountingOutputStream byteCounter;
  private final GzipCompressorOutputStream compressedBuffer;
  private final CSVPrinter csvPrinter;
  private final CsvSheetGenerator csvSheetGenerator;

  private ByteArrayInputStream byteArrayInputStream;
  private String filename;
  private File tempFile;
  private boolean isClosed;

  public CompressedCsvInMemoryBuffer() throws IOException {
    byteBuffer = new ByteArrayOutputStream();
    byteCounter = new CountingOutputStream(byteBuffer);
    compressedBuffer = new GzipCompressorOutputStream(byteCounter);
    csvPrinter = new CSVPrinter(new PrintWriter(compressedBuffer, true, StandardCharsets.UTF_8), CSVFormat.DEFAULT);
    csvSheetGenerator = new StagingDatabaseCsvSheetGenerator();

    byteArrayInputStream = null;
    filename = null;
    tempFile = null;
    isClosed = false;
  }

  @Override
  public Long accept(AirbyteRecordMessage recordMessage) throws Exception {
    if (byteArrayInputStream == null && !isClosed) {
      final long startCount = byteCounter.getCount();
      csvPrinter.printRecord(csvSheetGenerator.getDataRow(UUID.randomUUID(), recordMessage));
      return byteCounter.getCount() - startCount;
    } else {
      throw new IllegalCallerException("Buffer is already closed, it cannot accept more messages");
    }
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
      tempFile = Files.createTempFile(getFilename(), ".csv.gz").toFile();
    }
    return tempFile;
  }

  @Override
  public InputStream getInputStream() {
    return byteArrayInputStream;
  }

  @Override
  public void flush() throws IOException {
    if (byteArrayInputStream == null && !isClosed) {
      csvPrinter.flush();
      csvPrinter.close();
      // we need to close the gzip stream to finish compression and write trailer data.
      compressedBuffer.close();
      byteBuffer.close();
      byteArrayInputStream = new ByteArrayInputStream(byteBuffer.toByteArray());
    }
  }

  @Override
  public Long getCount() {
    return byteCounter.getCount();
  }

  @Override
  public void close() throws Exception {
    if (!isClosed) {
      byteArrayInputStream.close();
      if (tempFile != null) {
        LOGGER.info("Deleting tempFile data {}", tempFile.getName());
        Files.deleteIfExists(tempFile.toPath());
      }
      isClosed = true;
    }
  }

  public static RecordBufferSettings defaultSettings() {
    return new CompressedCsvInMemoryBufferSettings();
  }

  public static class CompressedCsvInMemoryBufferSettings implements RecordBufferSettings {

    @Override
    public RecordBufferImplementation newInstance() throws IOException {
      return new CompressedCsvInMemoryBuffer();
    }

    @Override
    public Long getMaxTotalBufferSizeInBytes() {
      return MAX_TOTAL_BUFFER_SIZE_BYTES;
    }

    @Override
    public Long getMaxPerStreamBufferSizeInBytes() {
      return MAX_PER_STREAM_BUFFER_SIZE_BYTES;
    }

    @Override
    public int getMaxConcurrentStreamsInBuffer() {
      return MAX_CONCURRENT_STREAM_IN_BUFFER;
    }

    @Override
    public String toString() {
      return String.format("%s (Max Total: %s, per stream: %s, #stream: %s)",
          getClass(),
          FileUtils.byteCountToDisplaySize(getMaxTotalBufferSizeInBytes()),
          FileUtils.byteCountToDisplaySize(getMaxPerStreamBufferSizeInBytes()),
          getMaxConcurrentStreamsInBuffer());
    }
  }
}
