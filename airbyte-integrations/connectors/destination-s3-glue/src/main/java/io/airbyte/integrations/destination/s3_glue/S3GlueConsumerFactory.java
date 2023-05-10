/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_glue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnCloseFunction;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.integrations.destination.record_buffer.BufferCreateFunction;
import io.airbyte.integrations.destination.record_buffer.FlushBufferFunction;
import io.airbyte.integrations.destination.record_buffer.SerializedBufferingStrategy;
import io.airbyte.integrations.destination.s3.BlobStorageOperations;
import io.airbyte.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.integrations.destination.s3.WriteConfig;
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

public class S3GlueConsumerFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(S3GlueConsumerFactory.class);

  private static final DateTime SYNC_DATETIME = DateTime.now(DateTimeZone.UTC);

  public AirbyteMessageConsumer create(final Consumer<AirbyteMessage> outputRecordCollector,
      final BlobStorageOperations storageOperations,
      final MetastoreOperations metastoreOperations,
      final NamingConventionTransformer namingResolver,
      final BufferCreateFunction onCreateBuffer,
      final S3DestinationConfig s3Config,
      final GlueDestinationConfig glueConfig,
      final ConfiguredAirbyteCatalog catalog) {
    final List<S3GlueWriteConfig> writeConfigs = createWriteConfigs(storageOperations, s3Config, catalog);
    return new BufferedStreamConsumer(
        outputRecordCollector,
        onStartFunction(storageOperations, writeConfigs),
        new SerializedBufferingStrategy(
            onCreateBuffer,
            catalog,
            flushBufferFunction(storageOperations, writeConfigs, catalog)),
        onCloseFunction(storageOperations, metastoreOperations, writeConfigs, glueConfig, s3Config),
        catalog,
        storageOperations::isValidData);
  }

  private static List<S3GlueWriteConfig> createWriteConfigs(final BlobStorageOperations storageOperations,
      final S3DestinationConfig config,
      final ConfiguredAirbyteCatalog catalog) {
    return catalog.getStreams()
        .stream()
        .map(toWriteConfig(storageOperations, config))
        .collect(Collectors.toList());
  }

  private static Function<ConfiguredAirbyteStream, S3GlueWriteConfig> toWriteConfig(
      final BlobStorageOperations storageOperations,
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
      final JsonNode jsonSchema = abStream.getJsonSchema();
      ((ObjectNode) jsonSchema.get("properties")).putPOJO(JavaBaseConstants.COLUMN_NAME_AB_ID, Map.of("type", "string"));
      ((ObjectNode) jsonSchema.get("properties")).putPOJO(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, Map.of("type", "number"));
      final String location = "s3://" + s3Config.getBucketName() + "/" +
          fullOutputPath.substring(0, fullOutputPath.lastIndexOf("/") + 1);
      final S3GlueWriteConfig writeConfig =
          new S3GlueWriteConfig(namespace, streamName, bucketPath, customOutputFormat, fullOutputPath, syncMode,
              jsonSchema, location);
      LOGGER.info("Write config: {}", writeConfig);
      return writeConfig;
    };
  }

  private OnStartFunction onStartFunction(final BlobStorageOperations storageOperations, final List<S3GlueWriteConfig> writeConfigs) {
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

  private FlushBufferFunction flushBufferFunction(
      final BlobStorageOperations storageOperations,
      final List<S3GlueWriteConfig> writeConfigs,
      final ConfiguredAirbyteCatalog catalog) {
    final Map<AirbyteStreamNameNamespacePair, WriteConfig> pairToWriteConfig =
        writeConfigs.stream()
            .collect(Collectors.toUnmodifiableMap(S3GlueConsumerFactory::toNameNamespacePair, Function.identity()));

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
      final MetastoreOperations metastoreOperations,
      final List<S3GlueWriteConfig> writeConfigs,
      GlueDestinationConfig glueDestinationConfig,
      S3DestinationConfig s3DestinationConfig) {
    return (hasFailed) -> {
      if (hasFailed) {
        LOGGER.info("Cleaning up destination started for {} streams", writeConfigs.size());
        for (final WriteConfig writeConfig : writeConfigs) {
          storageOperations.cleanUpBucketObject(writeConfig.getFullOutputPath(), writeConfig.getStoredFiles());
          writeConfig.clearStoredFiles();
        }
        LOGGER.info("Cleaning up destination completed.");
      } else {
        for (final S3GlueWriteConfig writeConfig : writeConfigs) {
          metastoreOperations.upsertTable(glueDestinationConfig.getDatabase(),
              writeConfig.getStreamName(), writeConfig.getLocation(), writeConfig.getJsonSchema(),
              glueDestinationConfig.getSerializationLibrary());
        }
      }
    };
  }

}
