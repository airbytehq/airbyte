/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.s3.writer;

import com.amazonaws.services.s3.AmazonS3;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.avro.JsonFieldNameUpdater;
import io.airbyte.integrations.destination.s3.avro.JsonToAvroSchemaConverter;
import io.airbyte.integrations.destination.s3.avro.S3AvroWriter;
import io.airbyte.integrations.destination.s3.csv.S3CsvWriter;
import io.airbyte.integrations.destination.s3.jsonl.S3JsonlWriter;
import io.airbyte.integrations.destination.s3.parquet.S3ParquetWriter;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.sql.Timestamp;
import org.apache.avro.Schema;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ProductionWriterFactory implements S3WriterFactory {

  protected static final Logger LOGGER = LoggerFactory.getLogger(ProductionWriterFactory.class);

  @Override
  public S3Writer create(S3DestinationConfig config,
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

      LOGGER.info("Avro schema for stream {}: {}", stream.getName(), avroSchema.toString(false));
      if (nameUpdater.hasNameUpdate()) {
        LOGGER.info("The following field names will be standardized: {}", nameUpdater);
      }

      if (format == S3Format.AVRO) {
        return new S3AvroWriter(config, s3Client, configuredStream, uploadTimestamp, avroSchema, nameUpdater);
      } else {
        return new S3ParquetWriter(config, s3Client, configuredStream, uploadTimestamp, avroSchema, nameUpdater);
      }
    }

    if (format == S3Format.CSV) {
      return new S3CsvWriter(config, s3Client, configuredStream, uploadTimestamp);
    }

    if (format == S3Format.JSONL) {
      return new S3JsonlWriter(config, s3Client, configuredStream, uploadTimestamp);
    }

    throw new RuntimeException("Unexpected S3 destination format: " + format);
  }

}
