/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.csv;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.template.S3FilenameTemplateParameterObject;
import io.airbyte.integrations.destination.s3.util.StreamTransferManagerFactory;
import io.airbyte.integrations.destination.s3.writer.BaseS3Writer;
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

public class S3CsvWriter extends BaseS3Writer implements DestinationFileWriter {

  private static final Logger LOGGER = LoggerFactory.getLogger(S3CsvWriter.class);

  private final CsvSheetGenerator csvSheetGenerator;
  private final StreamTransferManager uploadManager;
  private final MultiPartOutputStream outputStream;
  private final CSVPrinter csvPrinter;
  private final String objectKey;
  private final String gcsFileLocation;

  private S3CsvWriter(final S3DestinationConfig config,
                      final AmazonS3 s3Client,
                      final ConfiguredAirbyteStream configuredStream,
                      final Timestamp uploadTimestamp,
                      final int uploadThreads,
                      final int queueCapacity,
                      final boolean writeHeader,
                      CSVFormat csvSettings,
                      final CsvSheetGenerator csvSheetGenerator)
      throws IOException {
    super(config, s3Client, configuredStream);

    this.csvSheetGenerator = csvSheetGenerator;

    final String fileSuffix = "_" + UUID.randomUUID();
    final String outputFilename = determineOutputFilename(S3FilenameTemplateParameterObject
        .builder()
        .customSuffix(fileSuffix)
        .s3Format(S3Format.CSV)
        .fileExtension(S3Format.CSV.getFileExtension())
        .fileNamePattern(config.getFileNamePattern())
        .timestamp(uploadTimestamp)
        .build());
    this.objectKey = String.join("/", outputPrefix, outputFilename);

    LOGGER.info("Full S3 path for stream '{}': s3://{}/{}", stream.getName(), config.getBucketName(),
        objectKey);
    gcsFileLocation = String.format("gs://%s/%s", config.getBucketName(), objectKey);

    this.uploadManager = StreamTransferManagerFactory
        .create(config.getBucketName(), objectKey, s3Client)
        .get()
        .numUploadThreads(uploadThreads)
        .queueCapacity(queueCapacity);
    // We only need one output stream as we only have one input stream. This is reasonably performant.
    this.outputStream = uploadManager.getMultiPartOutputStreams().get(0);
    if (writeHeader) {
      csvSettings = csvSettings.withHeader(csvSheetGenerator.getHeaderRow().toArray(new String[0]));
    }
    this.csvPrinter = new CSVPrinter(new PrintWriter(outputStream, true, StandardCharsets.UTF_8), csvSettings);
  }

  public static class Builder {

    private final S3DestinationConfig config;
    private final AmazonS3 s3Client;
    private final ConfiguredAirbyteStream configuredStream;
    private final Timestamp uploadTimestamp;
    private int uploadThreads = StreamTransferManagerFactory.DEFAULT_UPLOAD_THREADS;
    private int queueCapacity = StreamTransferManagerFactory.DEFAULT_QUEUE_CAPACITY;
    private boolean withHeader = true;
    private CSVFormat csvSettings = CSVFormat.DEFAULT.withQuoteMode(QuoteMode.ALL);
    private CsvSheetGenerator csvSheetGenerator;

    public Builder(final S3DestinationConfig config,
                   final AmazonS3 s3Client,
                   final ConfiguredAirbyteStream configuredStream,
                   final Timestamp uploadTimestamp) {
      this.config = config;
      this.s3Client = s3Client;
      this.configuredStream = configuredStream;
      this.uploadTimestamp = uploadTimestamp;
    }

    public Builder uploadThreads(final int uploadThreads) {
      this.uploadThreads = uploadThreads;
      return this;
    }

    public Builder queueCapacity(final int queueCapacity) {
      this.queueCapacity = queueCapacity;
      return this;
    }

    public Builder withHeader(final boolean withHeader) {
      this.withHeader = withHeader;
      return this;
    }

    public Builder csvSettings(final CSVFormat csvSettings) {
      this.csvSettings = csvSettings;
      return this;
    }

    public Builder csvSheetGenerator(final CsvSheetGenerator csvSheetGenerator) {
      this.csvSheetGenerator = csvSheetGenerator;
      return this;
    }

    public S3CsvWriter build() throws IOException {
      if (csvSheetGenerator == null) {
        final S3CsvFormatConfig formatConfig = (S3CsvFormatConfig) config.getFormatConfig();
        csvSheetGenerator = CsvSheetGenerator.Factory.create(configuredStream.getStream().getJsonSchema(), formatConfig);
      }
      return new S3CsvWriter(config,
          s3Client,
          configuredStream,
          uploadTimestamp,
          uploadThreads,
          queueCapacity,
          withHeader,
          csvSettings,
          csvSheetGenerator);
    }

  }

  @Override
  public void write(final UUID id, final AirbyteRecordMessage recordMessage) throws IOException {
    csvPrinter.printRecord(csvSheetGenerator.getDataRow(id, recordMessage));
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
  public String getOutputPath() {
    return objectKey;
  }

  @Override
  public String getFileLocation() {
    return gcsFileLocation;
  }

  @Override
  public S3Format getFileFormat() {
    return S3Format.CSV;
  }

  @Override
  public void write(final JsonNode formattedData) throws IOException {
    csvPrinter.printRecord(csvSheetGenerator.getDataRow(formattedData));
  }

}
