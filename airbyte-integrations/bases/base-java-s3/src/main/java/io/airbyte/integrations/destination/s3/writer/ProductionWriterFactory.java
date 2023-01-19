/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.writer;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.avro.AvroConstants;
import io.airbyte.integrations.destination.s3.avro.JsonToAvroSchemaConverter;
import io.airbyte.integrations.destination.s3.avro.S3AvroWriter;
import io.airbyte.integrations.destination.s3.csv.S3CsvWriter;
import io.airbyte.integrations.destination.s3.jsonl.S3JsonlWriter;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetWriter;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.Timestamp;
import org.apache.avro.Schema;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ProductionWriterFactory implements S3WriterFactory {

  protected static final Logger LOGGER = LoggerFactory.getLogger(ProductionWriterFactory.class);

  @Override
  public DestinationFileWriter create(final S3DestinationConfig config,
                                      final AmazonS3 s3Client,
                                      final ConfiguredAirbyteStream configuredStream,
                                      final Timestamp uploadTimestamp)
      throws Exception {
    final S3Format format = config.getFormatConfig().getFormat();

    if (format == S3Format.AVRO || format == S3Format.PARQUET) {
      final AirbyteStream stream = configuredStream.getStream();
      LOGGER.info("Json schema for stream {}: {}", stream.getName(), stream.getJsonSchema());

      final JsonToAvroSchemaConverter schemaConverter = new JsonToAvroSchemaConverter();
      final Schema avroSchema = schemaConverter.getAvroSchema(stream.getJsonSchema(), stream.getName(), stream.getNamespace());

      LOGGER.info("Avro schema for stream {}: {}", stream.getName(), avroSchema.toString(false));

      if (format == S3Format.AVRO) {
        return new S3AvroWriter(config, s3Client, configuredStream, uploadTimestamp, avroSchema, AvroConstants.JSON_CONVERTER);
      } else {
        return new S3ParquetWriter(config, s3Client, configuredStream, uploadTimestamp, avroSchema, AvroConstants.JSON_CONVERTER);
      }
    }

    if (format == S3Format.CSV) {
      return new S3CsvWriter.Builder(config, s3Client, configuredStream, uploadTimestamp).build();
    }

    if (format == S3Format.JSONL) {
      return new S3JsonlWriter(config, s3Client, configuredStream, uploadTimestamp);
    }

    throw new RuntimeException("Unexpected S3 destination format: " + format);
  }

}
