/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.functional.CheckedBiConsumer;
import io.airbyte.commons.functional.CheckedBiFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.sentry.AirbyteSentry;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnCloseFunction;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.integrations.destination.record_buffer.SerializableBuffer;
import io.airbyte.integrations.destination.record_buffer.SerializedBufferingStrategy;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
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
  private static final String DEFAULT_PATH_FORMAT = "${NAMESPACE}/${STREAM_NAME}";

  private static final DateTime SYNC_DATETIME = DateTime.now(DateTimeZone.UTC);

  public AirbyteMessageConsumer create(final Consumer<AirbyteMessage> outputRecordCollector,
                                       final BlobStorageOperations storageOperations,
                                       final NamingConventionTransformer namingResolver,
                                       final CheckedBiFunction<AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> onCreateBuffer,
                                       final JsonNode config,
                                       final ConfiguredAirbyteCatalog catalog) {
    final List<WriteConfig> writeConfigs = createWriteConfigs(namingResolver, config, catalog);
    return new BufferedStreamConsumer(
        outputRecordCollector,
        onStartFunction(storageOperations, writeConfigs),
        new SerializedBufferingStrategy(onCreateBuffer, catalog,
            flushBufferFunction(storageOperations, writeConfigs, catalog)),
        onCloseFunction(storageOperations, writeConfigs),
        catalog,
        storageOperations::isValidData);
  }

  private static List<WriteConfig> createWriteConfigs(final NamingConventionTransformer namingResolver,
                                                      final JsonNode config,
                                                      final ConfiguredAirbyteCatalog catalog) {

    return catalog.getStreams().stream().map(toWriteConfig(namingResolver, config)).collect(Collectors.toList());
  }

  private static Function<ConfiguredAirbyteStream, WriteConfig> toWriteConfig(final NamingConventionTransformer namingResolver,
                                                                              final JsonNode config) {
    return stream -> {
      Preconditions.checkNotNull(stream.getDestinationSyncMode(), "Undefined destination sync mode");
      final AirbyteStream abStream = stream.getStream();

      final String outputNamespace = getOutputNamespace(abStream, config.get("s3_bucket_path").asText(), namingResolver);

      final String streamName = abStream.getName();
      final String outputBucket = namingResolver.getRawTableName(streamName);
      final DestinationSyncMode syncMode = stream.getDestinationSyncMode();
      final String customOutputFormat = config.has("path_format") ? config.get("path_format").asText() : DEFAULT_PATH_FORMAT;

      final WriteConfig writeConfig =
          new WriteConfig(streamName, abStream.getNamespace(), outputNamespace, outputBucket, syncMode, SYNC_DATETIME, customOutputFormat);
      LOGGER.info("Write config: {}", writeConfig);

      return writeConfig;
    };
  }

  private static String getOutputNamespace(final AirbyteStream stream,
                                           final String defaultDestNamespace,
                                           final NamingConventionTransformer namingResolver) {
    return stream.getNamespace() != null
        ? namingResolver.getIdentifier(stream.getNamespace())
        : namingResolver.getIdentifier(defaultDestNamespace);
  }

  private OnStartFunction onStartFunction(final BlobStorageOperations storageOperations, final List<WriteConfig> writeConfigs) {
    return () -> {
      LOGGER.info("Preparing bucket in destination started for {} streams", writeConfigs.size());
      for (final WriteConfig writeConfig : writeConfigs) {
        final String namespace = writeConfig.getOutputNamespace();
        final String stream = writeConfig.getStreamName();
        final String outputBucketName = storageOperations.getBucketObjectName(namespace, writeConfig.getOutputBucket());
        final String outputBucketPath = storageOperations.getBucketObjectPath(namespace, writeConfig.getOutputBucket(),
            writeConfig.getWriteDatetime(), writeConfig.getCustomOutputFormat());

        LOGGER.info("Preparing storage area in destination started for namespace {} stream {}: bucket: {}", namespace, stream, outputBucketPath);

        AirbyteSentry.executeWithTracing("PrepareStreamStorage",
            () -> storageOperations.createBucketObjectIfNotExists(outputBucketName),
            Map.of("namespace", namespace, "stream", stream, "storage", outputBucketPath));

        LOGGER.info("Preparing storage area in destination completed for namespace {} stream {}", namespace, stream);
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
            String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s", Jsons.serialize(catalog)));
      }

      final WriteConfig writeConfig = pairToWriteConfig.get(pair);
      final String namespace = writeConfig.getOutputNamespace();
      final String outputBucketName = storageOperations.getBucketObjectName(namespace, writeConfig.getOutputBucket());
      final String outputBucketPath = storageOperations.getBucketObjectPath(namespace, writeConfig.getOutputBucket(), writeConfig.getWriteDatetime(),
          writeConfig.getCustomOutputFormat());
      try (writer) {
        writer.flush();
        writeConfig.addStoredFile(storageOperations.uploadRecordsToBucket(writer, namespace, outputBucketName, outputBucketPath));
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
          storageOperations.cleanUpBucketObject(writeConfig.getOutputBucket(), writeConfig.getStoredFiles());
          writeConfig.clearStoredFiles();
        }
        LOGGER.info("Cleaning up destination completed.");
      }
    };
  }

}
