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
import io.airbyte.integrations.destination.s3.avro.JsonFieldNameUpdater;
import io.airbyte.integrations.destination.s3.avro.JsonToAvroSchemaConverter;
import io.airbyte.integrations.destination.s3.writer.S3Writer;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.sql.Timestamp;
import org.apache.avro.Schema;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ProductionWriterFactory implements GcsWriterFactory {

  protected static final Logger LOGGER = LoggerFactory.getLogger(ProductionWriterFactory.class);

  @Override
  public S3Writer create(GcsDestinationConfig config,
                         AmazonS3 s3Client,
                         ConfiguredAirbyteStream configuredStream,
                         Timestamp uploadTimestamp)
      throws Exception {
    S3Format format = config.getFormatConfig().getFormat();

    if (format == S3Format.AVRO || format == S3Format.PARQUET) {
      AirbyteStream stream = configuredStream.getStream();

      JsonToAvroSchemaConverter schemaConverter = new JsonToAvroSchemaConverter();
      Schema avroSchema = schemaConverter.getAvroSchema(stream.getJsonSchema(), stream.getName(), stream.getNamespace(), true);
      JsonFieldNameUpdater nameUpdater = new JsonFieldNameUpdater(schemaConverter.getStandardizedNames());

      LOGGER.info("Paquet schema for stream {}: {}", stream.getName(), avroSchema.toString(false));
      if (nameUpdater.hasNameUpdate()) {
        LOGGER.info("The following field names will be standardized: {}", nameUpdater);
      }

      if (format == S3Format.AVRO) {
        return new GcsAvroWriter(config, s3Client, configuredStream, uploadTimestamp, avroSchema, nameUpdater);
      } else {
        return new GcsParquetWriter(config, s3Client, configuredStream, uploadTimestamp, avroSchema, nameUpdater);
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
