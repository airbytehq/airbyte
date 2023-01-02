/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

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
import java.sql.Timestamp;
import java.util.UUID;
import org.apache.avro.Schema;
import org.apache.avro.file.DataFileWriter;
import org.apache.avro.generic.GenericData.Record;
import org.apache.avro.generic.GenericDatumWriter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import tech.allegro.schema.json2avro.converter.JsonAvroConverter;

public class S3AvroWriter extends BaseS3Writer implements DestinationFileWriter {

  protected static final Logger LOGGER = LoggerFactory.getLogger(S3AvroWriter.class);

  private final AvroRecordFactory avroRecordFactory;
  private final StreamTransferManager uploadManager;
  private final MultiPartOutputStream outputStream;
  private final DataFileWriter<Record> dataFileWriter;
  private final String objectKey;
  private final String gcsFileLocation;

  public S3AvroWriter(final S3DestinationConfig config,
                      final AmazonS3 s3Client,
                      final ConfiguredAirbyteStream configuredStream,
                      final Timestamp uploadTimestamp,
                      final Schema schema,
                      final JsonAvroConverter converter)
      throws IOException {
    super(config, s3Client, configuredStream);

    final String outputFilename = determineOutputFilename(S3FilenameTemplateParameterObject
        .builder()
        .timestamp(uploadTimestamp)
        .s3Format(S3Format.AVRO)
        .fileExtension(S3Format.AVRO.getFileExtension())
        .fileNamePattern(config.getFileNamePattern())
        .build());

    objectKey = String.join("/", outputPrefix, outputFilename);

    LOGGER.info("Full S3 path for stream '{}': s3://{}/{}", stream.getName(), config.getBucketName(), objectKey);
    gcsFileLocation = String.format("gs://%s/%s", config.getBucketName(), objectKey);

    this.avroRecordFactory = new AvroRecordFactory(schema, converter);
    this.uploadManager = StreamTransferManagerFactory
        .create(config.getBucketName(), objectKey, s3Client)
        .get();
    // We only need one output stream as we only have one input stream. This is reasonably performant.
    this.outputStream = uploadManager.getMultiPartOutputStreams().get(0);

    final S3AvroFormatConfig formatConfig = (S3AvroFormatConfig) config.getFormatConfig();
    // The DataFileWriter always uses binary encoding.
    // If json encoding is needed in the future, use the GenericDatumWriter directly.
    this.dataFileWriter = new DataFileWriter<>(new GenericDatumWriter<Record>())
        .setCodec(formatConfig.getCodecFactory())
        .create(schema, outputStream);
  }

  @Override
  public void write(final UUID id, final AirbyteRecordMessage recordMessage) throws IOException {
    dataFileWriter.append(avroRecordFactory.getAvroRecord(id, recordMessage));
  }

  @Override
  protected void closeWhenSucceed() throws IOException {
    dataFileWriter.close();
    outputStream.close();
    uploadManager.complete();
  }

  @Override
  protected void closeWhenFail() throws IOException {
    dataFileWriter.close();
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
    return S3Format.AVRO;
  }

  @Override
  public void write(final JsonNode formattedData) throws IOException {
    final Record record = avroRecordFactory.getAvroRecord(formattedData);
    dataFileWriter.append(record);
  }

}
