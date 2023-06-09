/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.csv;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.buffered_stream_consumer.RecordSizeEstimator;
import io.airbyte.integrations.destination.record_buffer.BaseSerializedBuffer;
import io.airbyte.integrations.destination.record_buffer.BufferCreateFunction;
import io.airbyte.integrations.destination.record_buffer.BufferStorage;
import io.airbyte.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.integrations.destination.s3.util.CompressionType;
import io.airbyte.integrations.destination_async.AirbyteFileUtils;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.Callable;

import lombok.extern.slf4j.Slf4j;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.QuoteMode;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Slf4j
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

  @Override
  protected void writeRecord(final AirbyteRecordMessage record) throws IOException {
    csvPrinter.printRecord(csvSheetGenerator.getDataRow(UUID.randomUUID(), record));
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

  public static void main (final String[] args) throws Exception {
    final CsvSerializedBuffer writer;
    final var list = generateRecords(100_000L);
    log.info("RT mem before processing CSV writer {}", AirbyteFileUtils.byteCountToDisplaySize(
            Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory()));
    try {
      writer = new CsvSerializedBuffer(
              new FileBuffer(CsvSerializedBuffer.CSV_GZ_SUFFIX),
              new StagingDatabaseCsvSheetGenerator(),
              true);

      // reassign as lambdas require references to be final.
      list.forEach(record -> {
        try {
          // todo (cgardens) - most writers just go ahead and re-serialize the contents of the record message.
          // we should either just pass the raw string or at least have a way to do that and create a default
          // impl that maintains backwards compatible behavior.
          writer.accept(Jsons.deserialize(record.getSerialized(), AirbyteMessage.class).getRecord());
        } catch (final Exception e) {
          throw new RuntimeException(e);
        }
      });
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
    log.info("RT mem after processing CSV writer {}", AirbyteFileUtils.byteCountToDisplaySize(
            Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory()));
    writer.flush();
    log.info("RT mem after flushing CSV writer {}", AirbyteFileUtils.byteCountToDisplaySize(
            Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory()));
  }

  private static List<PartialAirbyteMessage> generateRecords(final long targetSizeInBytes) {
    final List<PartialAirbyteMessage> output = Lists.newArrayList();
    final String SCHEMA_NAME = "schema";
    final String STREAM_NAME = "stream_name";
    long bytesCounter = 0;
    for (int i = 0;; i++) {
      final JsonNode payload =
              Jsons.jsonNode(ImmutableMap.of("id", RandomStringUtils.randomAlphabetic(7), "name", "human " + String.format("%8d", i)));
      final long sizeInBytes = RecordSizeEstimator.getStringByteSize(payload);
      bytesCounter += sizeInBytes;
      final PartialAirbyteMessage airbyteMessage = new PartialAirbyteMessage()
              .withType(AirbyteMessage.Type.RECORD)
              .withRecord(new PartialAirbyteRecordMessage()
                      .withStream(STREAM_NAME)
                      .withNamespace(SCHEMA_NAME))
              .withSerialized(Jsons.serialize(new AirbyteMessage()
                      .withType(AirbyteMessage.Type.RECORD)
                      .withRecord(new AirbyteRecordMessage()
                              .withStream(STREAM_NAME)
                              .withNamespace(SCHEMA_NAME)
                              .withData(payload)
                              .withEmittedAt(Instant.now().toEpochMilli()))));
      if (bytesCounter > targetSizeInBytes) {
        break;
      } else {
        output.add(airbyteMessage);
      }
    }
    return output;
  }

}
