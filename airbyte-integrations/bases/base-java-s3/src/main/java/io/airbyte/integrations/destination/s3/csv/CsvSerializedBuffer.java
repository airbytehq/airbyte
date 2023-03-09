/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.csv;

import io.airbyte.commons.functional.CheckedBiFunction;
import io.airbyte.integrations.destination.record_buffer.BaseSerializedBuffer;
import io.airbyte.integrations.destination.record_buffer.BufferStorage;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
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

public class CsvSerializedBuffer extends BaseSerializedBuffer {

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
    this.csvPrinter = null;
    this.csvFormat = CSVFormat.DEFAULT;
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
  protected void createWriter(final OutputStream outputStream) throws IOException {
    csvPrinter = new CSVPrinter(new PrintWriter(outputStream, true, StandardCharsets.UTF_8), csvFormat);
  }

  @Override
  protected void writeRecord(final AirbyteRecordMessage recordMessage) throws IOException {
    csvPrinter.printRecord(csvSheetGenerator.getDataRow(UUID.randomUUID(), recordMessage));
  }

  @Override
  protected void flushWriter() throws IOException {
    csvPrinter.flush();
  }

  @Override
  protected void closeWriter() throws IOException {
    csvPrinter.close();
  }

  public static CheckedBiFunction<AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> createFunction(
                                                                                                                                          final S3CsvFormatConfig config,
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
