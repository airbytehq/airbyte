/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.csv;

import io.airbyte.integrations.destination.record_buffer.BaseSerializedBuffer;
import io.airbyte.integrations.destination.record_buffer.BufferCreateFunction;
import io.airbyte.integrations.destination.record_buffer.BufferStorage;
import io.airbyte.integrations.destination.s3.util.CompressionType;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.util.UUID;
import java.util.concurrent.Callable;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.QuoteMode;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CsvSerializedBuffer extends BaseSerializedBuffer {

  private static final Logger LOGGER = LoggerFactory.getLogger(CsvSerializedBuffer.class);

  public static final String CSV_GZ_SUFFIX = ".csv.gz";

  private final CsvSheetGenerator csvSheetGenerator;
  private CSVPrinter csvPrinter;
  private CSVFormat csvFormat;

  public CsvSerializedBuffer(final BufferStorage bufferStorage,
                             final CsvSheetGenerator csvSheetGenerator,
                             final boolean compression)
      throws Exception {
    super(bufferStorage);
    this.csvSheetGenerator = csvSheetGenerator;
    csvPrinter = null;
    csvFormat = CSVFormat.DEFAULT;
    // we always want to compress csv files
    withCompression(compression);
  }

  public CsvSerializedBuffer withCsvFormat(final CSVFormat csvFormat) {
    if (csvPrinter == null) {
      this.csvFormat = csvFormat;
      return this;
    }
    throw new RuntimeException("Options should be configured before starting to write");
  }

  @Override
  protected void initWriter(final OutputStream outputStream) throws IOException {
    csvPrinter = new CSVPrinter(new PrintWriter(outputStream, true, StandardCharsets.UTF_8), csvFormat);
  }

  /**
   * TODO: (ryankfu) remove this call within {@link SerializedBufferingStrategy} and move to use
   * recordString
   *
   * @param record AirbyteRecordMessage to be written
   * @throws IOException
   */
  @Override
  protected void writeRecord(final AirbyteRecordMessage record) throws IOException {
    csvPrinter.printRecord(csvSheetGenerator.getDataRow(UUID.randomUUID(), record));
  }

  @Override
  protected void writeRecord(final String recordString, final long emittedAt) throws IOException {
    csvPrinter.printRecord(csvSheetGenerator.getDataRow(UUID.randomUUID(), recordString, emittedAt));
  }

  @Override
  protected void flushWriter() throws IOException {
    // in an async world, it is possible that flush writer gets called even if no records were accepted.
    if (csvPrinter != null) {
      csvPrinter.flush();
    } else {
      LOGGER.warn("Trying to flush but no printer is initialized.");
    }
  }

  @Override
  protected void closeWriter() throws IOException {
    // in an async world, it is possible that flush writer gets called even if no records were accepted.
    if (csvPrinter != null) {
      csvPrinter.close();
    } else {
      LOGGER.warn("Trying to close but no printer is initialized.");
    }
  }

  public static BufferCreateFunction createFunction(final S3CsvFormatConfig config,
                                                    final Callable<BufferStorage> createStorageFunction) {
    return (final AirbyteStreamNameNamespacePair stream, final ConfiguredAirbyteCatalog catalog) -> {
      if (config == null) {
        return new CsvSerializedBuffer(createStorageFunction.call(), new StagingDatabaseCsvSheetGenerator(), true);
      }

      final CsvSheetGenerator csvSheetGenerator = CsvSheetGenerator.Factory.create(catalog.getStreams()
          .stream()
          .filter(s -> s.getStream().getName().equals(stream.getName()) && StringUtils.equals(s.getStream().getNamespace(), stream.getNamespace()))
          .findFirst()
          .orElseThrow(() -> new RuntimeException(String.format("No such stream %s.%s", stream.getNamespace(), stream.getName())))
          .getStream()
          .getJsonSchema(),
          config);
      final CSVFormat csvSettings = CSVFormat.DEFAULT
          .withQuoteMode(QuoteMode.NON_NUMERIC)
          .withHeader(csvSheetGenerator.getHeaderRow().toArray(new String[0]));
      final boolean compression = config.getCompressionType() != CompressionType.NO_COMPRESSION;
      return new CsvSerializedBuffer(createStorageFunction.call(), csvSheetGenerator, compression).withCsvFormat(csvSettings);
    };
  }

}
