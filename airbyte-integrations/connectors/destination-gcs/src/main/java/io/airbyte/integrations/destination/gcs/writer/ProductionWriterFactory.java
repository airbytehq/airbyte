/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs.writer;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.integrations.destination.gcs.avro.GcsAvroWriter;
import io.airbyte.integrations.destination.gcs.csv.GcsCsvWriter;
import io.airbyte.integrations.destination.gcs.jsonl.GcsJsonlWriter;
import io.airbyte.integrations.destination.gcs.parquet.GcsParquetWriter;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.avro.AvroConstants;
import io.airbyte.integrations.destination.s3.avro.JsonToAvroSchemaConverter;
import io.airbyte.integrations.destination.s3.writer.DestinationFileWriter;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.sql.Timestamp;
import org.apache.avro.Schema;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ProductionWriterFactory implements GcsWriterFactory {

  protected static final Logger LOGGER = LoggerFactory.getLogger(ProductionWriterFactory.class);

  @Override
  public DestinationFileWriter create(final GcsDestinationConfig config,
                                      final AmazonS3 s3Client,
                                      final ConfiguredAirbyteStream configuredStream,
                                      final Timestamp uploadTimestamp)
      throws Exception {
    final S3Format format = config.getFormatConfig().getFormat();

    if (format == S3Format.AVRO || format == S3Format.PARQUET) {
      final AirbyteStream stream = configuredStream.getStream();
      LOGGER.info("Json schema for stream {}: {}", stream.getName(), stream.getJsonSchema());

      if (format == S3Format.AVRO) {
        return new GcsAvroWriter(config, s3Client, configuredStream, uploadTimestamp, AvroConstants.JSON_CONVERTER, stream.getJsonSchema());
      } else {
        final JsonToAvroSchemaConverter schemaConverter = new JsonToAvroSchemaConverter();
        final Schema avroSchema = schemaConverter.getAvroSchema(stream.getJsonSchema(), stream.getName(), stream.getNamespace());

        LOGGER.info("Avro schema for stream {}: {}", stream.getName(), avroSchema.toString(false));
        return new GcsParquetWriter(config, s3Client, configuredStream, uploadTimestamp, avroSchema, AvroConstants.JSON_CONVERTER);
      }
    }

    if (format == S3Format.CSV) {
      return new GcsCsvWriter(config, s3Client, configuredStream, uploadTimestamp);
    }

    if (format == S3Format.JSONL) {
      return new GcsJsonlWriter(config, s3Client, configuredStream, uploadTimestamp);
    }

    throw new RuntimeException("Unexpected GCS destination format: " + format);
  }

}
