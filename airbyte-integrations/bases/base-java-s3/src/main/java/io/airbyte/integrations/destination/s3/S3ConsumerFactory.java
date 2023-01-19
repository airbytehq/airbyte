/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.google.common.base.Preconditions;
import io.airbyte.commons.functional.CheckedBiConsumer;
import io.airbyte.commons.functional.CheckedBiFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnCloseFunction;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.record_buffer.SerializedBufferingStrategy;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.apache.commons.io.FileUtils;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class S3ConsumerFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(S3ConsumerFactory.class);
  private static final DateTime SYNC_DATETIME = DateTime.now(DateTimeZone.UTC);

  public AirbyteMessageConsumer create(final Consumer<AirbyteMessage> outputRecordCollector,
                                       final BlobStorageOperations storageOperations,
                                       final NamingConventionTransformer namingResolver,
                                       final CheckedBiFunction<AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> onCreateBuffer,
                                       final S3DestinationConfig s3Config,
                                       final ConfiguredAirbyteCatalog catalog) {
    final List<WriteConfig> writeConfigs = createWriteConfigs(storageOperations, namingResolver, s3Config, catalog);
    return new BufferedStreamConsumer(
        outputRecordCollector,
        onStartFunction(storageOperations, writeConfigs),
        new SerializedBufferingStrategy(
            onCreateBuffer,
            catalog,
            flushBufferFunction(storageOperations, writeConfigs, catalog)),
        onCloseFunction(storageOperations, writeConfigs),
        catalog,
        storageOperations::isValidData);
  }

  private static List<WriteConfig> createWriteConfigs(final BlobStorageOperations storageOperations,
                                                      final NamingConventionTransformer namingResolver,
                                                      final S3DestinationConfig config,
                                                      final ConfiguredAirbyteCatalog catalog) {
    return catalog.getStreams()
        .stream()
        .map(toWriteConfig(storageOperations, namingResolver, config))
        .collect(Collectors.toList());
  }

  private static Function<ConfiguredAirbyteStream, WriteConfig> toWriteConfig(final BlobStorageOperations storageOperations,
                                                                              final NamingConventionTransformer namingResolver,
                                                                              final S3DestinationConfig s3Config) {
    return stream -> {
      Preconditions.checkNotNull(stream.getDestinationSyncMode(), "Undefined destination sync mode");
      final AirbyteStream abStream = stream.getStream();
      final String namespace = abStream.getNamespace();
      final String streamName = abStream.getName();
      final String bucketPath = s3Config.getBucketPath();
      final String customOutputFormat = String.join("/", bucketPath, s3Config.getPathFormat());
      final String fullOutputPath = storageOperations.getBucketObjectPath(namespace, streamName, SYNC_DATETIME, customOutputFormat);
      final DestinationSyncMode syncMode = stream.getDestinationSyncMode();
      final WriteConfig writeConfig = new WriteConfig(namespace, streamName, bucketPath, customOutputFormat, fullOutputPath, syncMode);
      LOGGER.info("Write config: {}", writeConfig);
      return writeConfig;
    };
  }

  private OnStartFunction onStartFunction(final BlobStorageOperations storageOperations, final List<WriteConfig> writeConfigs) {
    return () -> {
      LOGGER.info("Preparing bucket in destination started for {} streams", writeConfigs.size());
      for (final WriteConfig writeConfig : writeConfigs) {
        if (writeConfig.getSyncMode().equals(DestinationSyncMode.OVERWRITE)) {
          final String namespace = writeConfig.getNamespace();
          final String stream = writeConfig.getStreamName();
          final String outputBucketPath = writeConfig.getOutputBucketPath();
          final String pathFormat = writeConfig.getPathFormat();
          LOGGER.info("Clearing storage area in destination started for namespace {} stream {} bucketObject {} pathFormat {}",
              namespace, stream, outputBucketPath, pathFormat);
          storageOperations.cleanUpBucketObject(namespace, stream, outputBucketPath, pathFormat);
          LOGGER.info("Clearing storage area in destination completed for namespace {} stream {} bucketObject {}", namespace, stream,
              outputBucketPath);
        }
      }
      LOGGER.info("Preparing storage area in destination completed.");
    };
  }

  private static AirbyteStreamNameNamespacePair toNameNamespacePair(final WriteConfig config) {
    return new AirbyteStreamNameNamespacePair(config.getStreamName(), config.getNamespace());
  }

  private CheckedBiConsumer<AirbyteStreamNameNamespacePair, SerializableBuffer, Exception> flushBufferFunction(final BlobStorageOperations storageOperations,
                                                                                                               final List<WriteConfig> writeConfigs,
                                                                                                               final ConfiguredAirbyteCatalog catalog) {
    final Map<AirbyteStreamNameNamespacePair, WriteConfig> pairToWriteConfig =
        writeConfigs.stream()
            .collect(Collectors.toUnmodifiableMap(
                S3ConsumerFactory::toNameNamespacePair, Function.identity()));

    return (pair, writer) -> {
      LOGGER.info("Flushing buffer for stream {} ({}) to storage", pair.getName(), FileUtils.byteCountToDisplaySize(writer.getByteCount()));
      if (!pairToWriteConfig.containsKey(pair)) {
        throw new IllegalArgumentException(
            String.format("Message contained record from a stream %s that was not in the catalog. \ncatalog: %s", pair, Jsons.serialize(catalog)));
      }

      final WriteConfig writeConfig = pairToWriteConfig.get(pair);
      try (writer) {
        writer.flush();
        writeConfig.addStoredFile(storageOperations.uploadRecordsToBucket(
            writer,
            writeConfig.getNamespace(),
            writeConfig.getStreamName(),
            writeConfig.getFullOutputPath()));
      } catch (final Exception e) {
        LOGGER.error("Failed to flush and upload buffer to storage:", e);
        throw new RuntimeException("Failed to upload buffer to storage", e);
      }
    };
  }

  private OnCloseFunction onCloseFunction(final BlobStorageOperations storageOperations,
                                          final List<WriteConfig> writeConfigs) {
    return (hasFailed) -> {
      if (hasFailed) {
        LOGGER.info("Cleaning up destination started for {} streams", writeConfigs.size());
        for (final WriteConfig writeConfig : writeConfigs) {
          storageOperations.cleanUpBucketObject(writeConfig.getFullOutputPath(), writeConfig.getStoredFiles());
          writeConfig.clearStoredFiles();
        }
        LOGGER.info("Cleaning up destination completed.");
      }
    };
  }

}
