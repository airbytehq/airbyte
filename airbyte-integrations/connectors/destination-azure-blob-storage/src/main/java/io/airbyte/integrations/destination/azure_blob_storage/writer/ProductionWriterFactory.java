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

package io.airbyte.integrations.destination.azure_blob_storage.writer;

import com.azure.storage.blob.specialized.AppendBlobClient;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageDestinationConfig;
import io.airbyte.integrations.destination.azure_blob_storage.AzureBlobStorageFormat;
import io.airbyte.integrations.destination.azure_blob_storage.jsonl.AzureBlobStorageJsonlWriter;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.sql.Timestamp;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ProductionWriterFactory implements AzureBlobStorageWriterFactory {

  protected static final Logger LOGGER = LoggerFactory.getLogger(ProductionWriterFactory.class);

  @Override
  public AzureBlobStorageWriter create(AzureBlobStorageDestinationConfig config,
                                       AppendBlobClient appendBlobClient,
                                       ConfiguredAirbyteStream configuredStream,
                                       Timestamp uploadTimestamp)
      throws Exception {
    AzureBlobStorageFormat format = config.getFormatConfig().getFormat();

    if (format == AzureBlobStorageFormat.AVRO || format == AzureBlobStorageFormat.PARQUET) {
      // AirbyteStream stream = configuredStream.getStream();
      // JsonToAvroSchemaConverter schemaConverter = new JsonToAvroSchemaConverter();
      // Schema avroSchema = schemaConverter.getAvroSchema(stream.getJsonSchema(), stream.getName(),
      // stream.getNamespace(), true);
      // JsonFieldNameUpdater nameUpdater = new
      // JsonFieldNameUpdater(schemaConverter.getStandardizedNames());
      //
      // LOGGER.info("Avro schema for stream {}: {}", stream.getName(), avroSchema.toString(false));
      // if (nameUpdater.hasNameUpdate()) {
      // LOGGER.info("The following field names will be standardized: {}", nameUpdater);
      // }
      //
      // if (format == AzureBlobStorageFormat.AVRO) {
      // return new AzureBlobStorageAvroWriter(config, s3Client, configuredStream, uploadTimestamp,
      // avroSchema, nameUpdater);
      // } else {
      // return new AzureBlobStorageParquetWriter(config, s3Client, configuredStream, uploadTimestamp,
      // avroSchema, nameUpdater);
      // }
      // TODO to implement
      throw new Exception("Not implemented");
    }

    if (format == AzureBlobStorageFormat.CSV) {
      // TODO to implement
      throw new Exception("Not implemented");
      // return new AzureBlobStorageCsvWriter(config, AzureBlobStorageClient, configuredStream, uploadTimestamp);
    }

    if (format == AzureBlobStorageFormat.JSONL) {
      LOGGER.debug("Picked up JSONL format writer");
      return new AzureBlobStorageJsonlWriter(config, appendBlobClient, configuredStream, uploadTimestamp);
    }

    throw new RuntimeException("Unexpected AzureBlobStorage destination format: " + format);
  }

}
