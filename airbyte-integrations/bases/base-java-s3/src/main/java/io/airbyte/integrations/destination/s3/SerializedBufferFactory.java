/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import io.airbyte.commons.functional.CheckedBiFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.record_buffer.BufferStorage;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.s3.avro.AvroSerializedBuffer;
import io.airbyte.integrations.destination.s3.avro.S3AvroFormatConfig;
import io.airbyte.integrations.destination.s3.csv.CsvSerializedBuffer;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig;
import io.airbyte.integrations.destination.s3.jsonl.JsonLSerializedBuffer;
import io.airbyte.integrations.destination.s3.jsonl.S3JsonlFormatConfig;
import io.airbyte.integrations.destination.s3.parquet.ParquetSerializedBuffer;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.concurrent.Callable;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SerializedBufferFactory {

  protected static final Logger LOGGER = LoggerFactory.getLogger(SerializedBufferFactory.class);

  /**
   * When running a
   * {@link io.airbyte.integrations.destination.record_buffer.SerializedBufferingStrategy}, it would
   * usually need to instantiate new buffers when flushing data or when it receives data for a
   * brand-new stream. This factory fills this need and @return the function to be called on such
   * events.
   *
   * The factory is responsible for choosing the correct constructor function for a new
   * {@link SerializableBuffer} that handles the correct serialized format of the data. It is
   * configured by composition with another function to create a new {@link BufferStorage} where to
   * store it.
   *
   * This factory determines which {@link S3FormatConfig} to use depending on the user provided @param
   * config, The @param createStorageFunctionWithoutExtension is the constructor function to call when
   * creating a new buffer where to store data. Note that we typically associate which format is being
   * stored in the storage object thanks to its file extension.
   */
  public static CheckedBiFunction<AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> getCreateFunction(final S3DestinationConfig config,
                                                                                                                                             final Function<String, BufferStorage> createStorageFunctionWithoutExtension) {
    final S3FormatConfig formatConfig = config.getFormatConfig();
    LOGGER.info("S3 format config: {}", formatConfig.toString());
    switch (formatConfig.getFormat()) {
      case AVRO -> {
        final Callable<BufferStorage> createStorageFunctionWithExtension =
            () -> createStorageFunctionWithoutExtension.apply(formatConfig.getFileExtension());
        return AvroSerializedBuffer.createFunction((S3AvroFormatConfig) formatConfig, createStorageFunctionWithExtension);
      }
      case CSV -> {
        final Callable<BufferStorage> createStorageFunctionWithExtension =
            () -> createStorageFunctionWithoutExtension.apply(formatConfig.getFileExtension());
        return CsvSerializedBuffer.createFunction((S3CsvFormatConfig) formatConfig, createStorageFunctionWithExtension);
      }
      case JSONL -> {
        final Callable<BufferStorage> createStorageFunctionWithExtension =
            () -> createStorageFunctionWithoutExtension.apply(formatConfig.getFileExtension());
        return JsonLSerializedBuffer.createFunction((S3JsonlFormatConfig) formatConfig, createStorageFunctionWithExtension);
      }
      case PARQUET -> {
        // we can't choose the type of buffer storage with parquet because of how the underlying hadoop
        // library is imposing file usage.
        return ParquetSerializedBuffer.createFunction(config);
      }
      default -> {
        throw new RuntimeException("Unexpected output format: " + Jsons.serialize(config));
      }
    }
  }

}
