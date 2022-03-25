/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.functional.CheckedBiFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.destination.record_buffer.BufferStorage;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.s3.avro.AvroSerializedBuffer;
import io.airbyte.integrations.destination.s3.avro.S3AvroFormatConfig;
import io.airbyte.integrations.destination.s3.csv.CsvSerializedBuffer;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig;
import io.airbyte.integrations.destination.s3.jsonl.JsonLSerializedBuffer;
import io.airbyte.integrations.destination.s3.jsonl.S3JsonlFormatConfig;
import io.airbyte.integrations.destination.s3.parquet.ParquetSerializedBuffer;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SerializedBufferFactory {

  protected static final Logger LOGGER = LoggerFactory.getLogger(SerializedBufferFactory.class);

  /**
   * When running a {@link io.airbyte.integrations.destination.record_buffer.SerializedBufferingStrategy}, we usually need
   * to instantiate new buffers when flushing data or when we receive data for a brand-new stream. This factory feels this need
   * and @return the function responsible to create a new {@link SerializableBuffer} that handles the correct format using the underlying storage.
   *
   * This factory determines which {@link S3FormatConfig} to use depending on the user provided @param config,
   * The @param createStorageFunction is the constructor function to call when creating a new buffer where to store data.
   * Note that we typically associate which format is being stored in the storage object thanks to its file extension.
   */
  public static CheckedBiFunction<AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> getCreateFunction(final JsonNode config,
                                                                                                                                             final Function<String, BufferStorage> createStorageFunction) {
    final JsonNode formatConfig = config.get("format");
    LOGGER.info("S3 format config: {}", formatConfig.toString());
    final S3Format formatType = S3Format.valueOf(formatConfig.get("format_type").asText().toUpperCase());

    switch (formatType) {
      case AVRO -> {
        return AvroSerializedBuffer.createFunction(new S3AvroFormatConfig(formatConfig), () -> createStorageFunction.apply(".avro"));
      }
      case CSV -> {
        return CsvSerializedBuffer.createFunction(new S3CsvFormatConfig(formatConfig), () -> createStorageFunction.apply(".csv.gz"));
      }
      case JSONL -> {
        return JsonLSerializedBuffer.createFunction(new S3JsonlFormatConfig(formatConfig), () -> createStorageFunction.apply(".json.gz"));
      }
      case PARQUET -> {
        // we can't choose the type of buffer storage with parquet because of how the underlying hadoop library is imposing file usage.
        return ParquetSerializedBuffer.createFunction(S3DestinationConfig.getS3DestinationConfig(config));
      }
      default -> {
        throw new RuntimeException("Unexpected output format: " + Jsons.serialize(config));
      }
    }
  }

}
