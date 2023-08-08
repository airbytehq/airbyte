/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.staging;

import static java.util.stream.Collectors.joining;
import static java.util.stream.Collectors.toList;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.integrations.base.TypingAndDedupingFlag;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeOperationValve;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer;
import io.airbyte.integrations.destination.jdbc.WriteConfig;
import io.airbyte.integrations.destination.record_buffer.BufferCreateFunction;
import io.airbyte.integrations.destination.record_buffer.SerializedBufferingStrategy;
import io.airbyte.integrations.destination_async.AsyncStreamConsumer;
import io.airbyte.integrations.destination_async.buffers.BufferManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.function.Function;
import org.joda.time.DateTime;
import org.joda.time.DateTimeZone;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Uses both Factory and Consumer design pattern to create a single point of creation for consuming
 * {@link AirbyteMessage} for processing
 */
public class StagingConsumerFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(StagingConsumerFactory.class);

  // using a random string here as a placeholder for the moment.
  // This would avoid mixing data in the staging area between different syncs (especially if they
  // manipulate streams with similar names)
  // if we replaced the random connection id by the actual connection_id, we'd gain the opportunity to
  // leverage data that was uploaded to stage
  // in a previous attempt but failed to load to the warehouse for some reason (interrupted?) instead.
  // This would also allow other programs/scripts
  // to load (or reload backups?) in the connection's staging area to be loaded at the next sync.
  private static final DateTime SYNC_DATETIME = DateTime.now(DateTimeZone.UTC);
  public static final UUID RANDOM_CONNECTION_ID = UUID.randomUUID();

  public AirbyteMessageConsumer create(final Consumer<AirbyteMessage> outputRecordCollector,
                                       final JdbcDatabase database,
                                       final StagingOperations stagingOperations,
                                       final NamingConventionTransformer namingResolver,
                                       final BufferCreateFunction onCreateBuffer,
                                       final JsonNode config,
                                       final ConfiguredAirbyteCatalog catalog,
                                       final boolean purgeStagingData,
                                       final TypeAndDedupeOperationValve typerDeduperValve,
                                       final TyperDeduper typerDeduper,
                                       final ParsedCatalog parsedCatalog) {
    final List<WriteConfig> writeConfigs = createWriteConfigs(namingResolver, config, catalog, parsedCatalog);
    return new BufferedStreamConsumer(
        outputRecordCollector,
        GeneralStagingFunctions.onStartFunction(database, stagingOperations, writeConfigs, typerDeduper),
        new SerializedBufferingStrategy(
            onCreateBuffer,
            catalog,
            SerialFlush.function(database, stagingOperations, writeConfigs, catalog, typerDeduperValve, typerDeduper)),
        GeneralStagingFunctions.onCloseFunction(database, stagingOperations, writeConfigs, purgeStagingData, typerDeduper),
        catalog,
        stagingOperations::isValidData);
  }

  public SerializedAirbyteMessageConsumer createAsync(final Consumer<AirbyteMessage> outputRecordCollector,
                                                      final JdbcDatabase database,
                                                      final StagingOperations stagingOperations,
                                                      final NamingConventionTransformer namingResolver,
                                                      final JsonNode config,
                                                      final ConfiguredAirbyteCatalog catalog,
                                                      final boolean purgeStagingData,
                                                      TypeAndDedupeOperationValve typerDeduperValve,
                                                      final TyperDeduper typerDeduper,
                                                      final ParsedCatalog parsedCatalog) {
    final List<WriteConfig> writeConfigs = createWriteConfigs(namingResolver, config, catalog, parsedCatalog);
    final var streamDescToWriteConfig = streamDescToWriteConfig(writeConfigs);
    final var flusher = new AsyncFlush(streamDescToWriteConfig, stagingOperations, database, catalog, typerDeduperValve, typerDeduper);
    return new AsyncStreamConsumer(
        outputRecordCollector,
        GeneralStagingFunctions.onStartFunction(database, stagingOperations, writeConfigs, typerDeduper),
        // todo (cgardens) - wrapping the old close function to avoid more code churn.
        () -> GeneralStagingFunctions.onCloseFunction(database, stagingOperations, writeConfigs, purgeStagingData, typerDeduper).accept(false),
        flusher,
        catalog,
        new BufferManager());
  }

  private static Map<StreamDescriptor, WriteConfig> streamDescToWriteConfig(final List<WriteConfig> writeConfigs) {
    final Set<WriteConfig> conflictingStreams = new HashSet<>();
    final Map<StreamDescriptor, WriteConfig> streamDescToWriteConfig = new HashMap<>();
    for (final WriteConfig config : writeConfigs) {
      final StreamDescriptor streamIdentifier = toStreamDescriptor(config);
      if (streamDescToWriteConfig.containsKey(streamIdentifier)) {
        conflictingStreams.add(config);
        final WriteConfig existingConfig = streamDescToWriteConfig.get(streamIdentifier);
        // The first conflicting stream won't have any problems, so we need to explicitly add it here.
        conflictingStreams.add(existingConfig);
      } else {
        streamDescToWriteConfig.put(streamIdentifier, config);
      }
    }
    if (!conflictingStreams.isEmpty()) {
      final String message = String.format(
          "You are trying to write multiple streams to the same table. Consider switching to a custom namespace format using ${SOURCE_NAMESPACE}, or moving one of them into a separate connection with a different stream prefix. Affected streams: %s",
          conflictingStreams.stream().map(config -> config.getNamespace() + "." + config.getStreamName()).collect(joining(", ")));
      throw new ConfigErrorException(message);
    }
    return streamDescToWriteConfig;
  }

  private static StreamDescriptor toStreamDescriptor(final WriteConfig config) {
    return new StreamDescriptor().withName(config.getStreamName()).withNamespace(config.getNamespace());
  }

  /**
   * Creates a list of all {@link WriteConfig} for each stream within a
   * {@link ConfiguredAirbyteCatalog}. Each write config represents the configuration settings for
   * writing to a destination connector
   *
   * @param namingResolver {@link NamingConventionTransformer} used to transform names that are
   *        acceptable by each destination connector
   * @param config destination connector configuration parameters
   * @param catalog {@link ConfiguredAirbyteCatalog} collection of configured
   *        {@link ConfiguredAirbyteStream}
   * @return list of all write configs for each stream in a {@link ConfiguredAirbyteCatalog}
   */
  private static List<WriteConfig> createWriteConfigs(final NamingConventionTransformer namingResolver,
                                                      final JsonNode config,
                                                      final ConfiguredAirbyteCatalog catalog,
                                                      final ParsedCatalog parsedCatalog) {

    return catalog.getStreams().stream().map(toWriteConfig(namingResolver, config, parsedCatalog)).collect(toList());
  }

  private static Function<ConfiguredAirbyteStream, WriteConfig> toWriteConfig(final NamingConventionTransformer namingResolver,
                                                                              final JsonNode config,
                                                                              final ParsedCatalog parsedCatalog) {
    return stream -> {
      Preconditions.checkNotNull(stream.getDestinationSyncMode(), "Undefined destination sync mode");
      final AirbyteStream abStream = stream.getStream();
      final String streamName = abStream.getName();

      final String outputSchema;
      final String tableName;
      if (TypingAndDedupingFlag.isDestinationV2()) {
        final StreamId streamId = parsedCatalog.getStream(abStream.getNamespace(), streamName).id();
        outputSchema = streamId.rawNamespace();
        tableName = streamId.rawName();
      } else {
        outputSchema = getOutputSchema(abStream, config.get("schema").asText(), namingResolver);
        tableName = namingResolver.getRawTableName(streamName);
      }
      final String tmpTableName = namingResolver.getTmpTableName(streamName);
      final DestinationSyncMode syncMode = stream.getDestinationSyncMode();

      final WriteConfig writeConfig =
          new WriteConfig(streamName, abStream.getNamespace(), outputSchema, tmpTableName, tableName, syncMode, SYNC_DATETIME);
      LOGGER.info("Write config: {}", writeConfig);

      return writeConfig;
    };
  }

  private static String getOutputSchema(final AirbyteStream stream,
                                        final String defaultDestSchema,
                                        final NamingConventionTransformer namingResolver) {
    return stream.getNamespace() != null
        ? namingResolver.getNamespace(stream.getNamespace())
        : namingResolver.getNamespace(defaultDestSchema);
  }

}
