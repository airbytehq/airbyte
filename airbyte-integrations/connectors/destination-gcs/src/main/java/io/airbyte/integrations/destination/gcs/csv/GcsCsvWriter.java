/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.csv;

import static io.airbyte.integrations.destination.s3.util.StreamTransferManagerFactory.DEFAULT_PART_SIZE_MB;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.writer.BaseGcsWriter;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.csv.CsvSheetGenerator;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig;
import io.airbyte.integrations.destination.s3.util.StreamTransferManagerFactory;
import io.airbyte.integrations.destination.s3.writer.DestinationFileWriter;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.sql.Timestamp;
import java.util.UUID;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.commons.csv.QuoteMode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class GcsCsvWriter extends BaseGcsWriter implements DestinationFileWriter {

  private static final Logger LOGGER = LoggerFactory.getLogger(GcsCsvWriter.class);

  private final CsvSheetGenerator csvSheetGenerator;
  private final StreamTransferManager uploadManager;
  private final MultiPartOutputStream outputStream;
  private final CSVPrinter csvPrinter;
  private final String gcsFileLocation;
  private final String objectKey;

  public GcsCsvWriter(final GcsDestinationConfig config,
                      final AmazonS3 s3Client,
                      final ConfiguredAirbyteStream configuredStream,
                      final Timestamp uploadTimestamp)
      throws IOException {
    super(config, s3Client, configuredStream);

    final S3CsvFormatConfig formatConfig = (S3CsvFormatConfig) config.getFormatConfig();
    this.csvSheetGenerator = CsvSheetGenerator.Factory.create(configuredStream.getStream().getJsonSchema(), formatConfig);

    final String outputFilename = BaseGcsWriter.getOutputFilename(uploadTimestamp, S3Format.CSV);
    objectKey = String.join("/", outputPrefix, outputFilename);
    gcsFileLocation = String.format("gs://%s/%s", config.getBucketName(), objectKey);

    LOGGER.info("Full GCS path for stream '{}': {}/{}", stream.getName(), config.getBucketName(),
        objectKey);

    this.uploadManager = StreamTransferManagerFactory
        .create(config.getBucketName(), objectKey, s3Client)
        .setPartSize((long) DEFAULT_PART_SIZE_MB)
        .get();
    // We only need one output stream as we only have one input stream. This is reasonably performant.
    this.outputStream = uploadManager.getMultiPartOutputStreams().get(0);
    this.csvPrinter = new CSVPrinter(new PrintWriter(outputStream, true, StandardCharsets.UTF_8),
        CSVFormat.DEFAULT.withQuoteMode(QuoteMode.ALL)
            .withHeader(csvSheetGenerator.getHeaderRow().toArray(new String[0])));
  }

  @Override
  public void write(final UUID id, final AirbyteRecordMessage recordMessage) throws IOException {
    csvPrinter.printRecord(csvSheetGenerator.getDataRow(id, recordMessage));
  }

  @Override
  public void write(final JsonNode formattedData) throws IOException {
    csvPrinter.printRecord(csvSheetGenerator.getDataRow(formattedData));
  }

  @Override
  protected void closeWhenSucceed() throws IOException {
    csvPrinter.close();
    outputStream.close();
    uploadManager.complete();
  }

  @Override
  protected void closeWhenFail() throws IOException {
    csvPrinter.close();
    outputStream.close();
    uploadManager.abort();
  }

  @Override
  public String getFileLocation() {
    return gcsFileLocation;
  }

  public CSVPrinter getCsvPrinter() {
    return csvPrinter;
  }

  @Override
  public S3Format getFileFormat() {
    return S3Format.CSV;
  }

  @Override
  public String getOutputPath() {
    return objectKey;
  }

}
