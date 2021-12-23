/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.avro;

import alex.mojaki.s3upload.MultiPartOutputStream;
import alex.mojaki.s3upload.StreamTransferManager;
import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.util.S3StreamTransferManagerHelper;
import io.airbyte.integrations.destination.s3.writer.BaseS3Writer;
import io.airbyte.integrations.destination.s3.writer.S3Writer;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.io.IOException;
import java.sql.Timestamp;
import java.util.UUID;
import org.apache.avro.Schema;
import org.apache.avro.file.DataFileWriter;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericData.Record;
import org.apache.avro.generic.GenericDatumWriter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import tech.allegro.schema.json2avro.converter.JsonAvroConverter;

public class S3AvroWriter extends BaseS3Writer implements S3Writer {

  protected static final Logger LOGGER = LoggerFactory.getLogger(S3AvroWriter.class);

  private final AvroRecordFactory avroRecordFactory;
  private final StreamTransferManager uploadManager;
  private final MultiPartOutputStream outputStream;
  private final DataFileWriter<GenericData.Record> dataFileWriter;
  private final String objectKey;

  public S3AvroWriter(final S3DestinationConfig config,
                      final AmazonS3 s3Client,
                      final ConfiguredAirbyteStream configuredStream,
                      final Timestamp uploadTimestamp,
                      final Schema schema,
                      final JsonAvroConverter converter)
      throws IOException {
    super(config, s3Client, configuredStream);

    final String outputFilename = BaseS3Writer.getOutputFilename(uploadTimestamp, S3Format.AVRO);
    objectKey = String.join("/", outputPrefix, outputFilename);

    LOGGER.info("Full S3 path for stream '{}': s3://{}/{}", stream.getName(), config.getBucketName(), objectKey);

    this.avroRecordFactory = new AvroRecordFactory(schema, converter);
    this.uploadManager = S3StreamTransferManagerHelper.getDefault(
        config.getBucketName(), objectKey, s3Client, config.getFormatConfig().getPartSize());
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

}
