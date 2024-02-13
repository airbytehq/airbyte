/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.staging;

import static io.airbyte.cdk.integrations.destination_async.buffers.BufferManager.MEMORY_LIMIT_RATIO;
import static java.util.stream.Collectors.joining;
import static java.util.stream.Collectors.toList;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.WriteConfig;
import io.airbyte.cdk.integrations.destination_async.AsyncStreamConsumer;
import io.airbyte.cdk.integrations.destination_async.buffers.BufferManager;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.integrations.base.destination.typing_deduping.ParsedCatalog;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeOperationValve;
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduper;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.time.Instant;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.function.Consumer;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Uses both Factory and Consumer design pattern to create a single point of creation for consuming
 * {@link AirbyteMessage} for processing
 */
public class StagingConsumerFactory extends SerialStagingConsumerFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(StagingConsumerFactory.class);

  private static final Instant SYNC_DATETIME = Instant.now();

  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final JdbcDatabase database;
  private final StagingOperations stagingOperations;
  private final NamingConventionTransformer namingResolver;
  private final JsonNode config;
  private final ConfiguredAirbyteCatalog catalog;
  private final boolean purgeStagingData;
  private final TypeAndDedupeOperationValve typerDeduperValve;
  private final TyperDeduper typerDeduper;
  private final ParsedCatalog parsedCatalog;
  private final String defaultNamespace;
  private final boolean useDestinationsV2Columns;

  // Optional fields
  private final Optional<Long> bufferMemoryLimit;
  private final long optimalBatchSizeBytes;

  private StagingConsumerFactory(
                                 final Consumer<AirbyteMessage> outputRecordCollector,
                                 final JdbcDatabase database,
                                 final StagingOperations stagingOperations,
                                 final NamingConventionTransformer namingResolver,
                                 final JsonNode config,
                                 final ConfiguredAirbyteCatalog catalog,
                                 final boolean purgeStagingData,
                                 final TypeAndDedupeOperationValve typerDeduperValve,
                                 final TyperDeduper typerDeduper,
                                 final ParsedCatalog parsedCatalog,
                                 final String defaultNamespace,
                                 final boolean useDestinationsV2Columns,
                                 final Optional<Long> bufferMemoryLimit,
                                 final long optimalBatchSizeBytes) {
    this.outputRecordCollector = outputRecordCollector;
    this.database = database;
    this.stagingOperations = stagingOperations;
    this.namingResolver = namingResolver;
    this.config = config;
    this.catalog = catalog;
    this.purgeStagingData = purgeStagingData;
    this.typerDeduperValve = typerDeduperValve;
    this.typerDeduper = typerDeduper;
    this.parsedCatalog = parsedCatalog;
    this.defaultNamespace = defaultNamespace;
    this.useDestinationsV2Columns = useDestinationsV2Columns;
    this.bufferMemoryLimit = bufferMemoryLimit;
    this.optimalBatchSizeBytes = optimalBatchSizeBytes;
  }

  public static class Builder {

    // Required (?) fields
    // (TODO which of these are _actually_ required, and which have we just coincidentally always
    // provided?)
    private Consumer<AirbyteMessage> outputRecordCollector;
    private JdbcDatabase database;
    private StagingOperations stagingOperations;
    private NamingConventionTransformer namingResolver;
    private JsonNode config;
    private ConfiguredAirbyteCatalog catalog;
    private boolean purgeStagingData;
    private TypeAndDedupeOperationValve typerDeduperValve;
    private TyperDeduper typerDeduper;
    private ParsedCatalog parsedCatalog;
    private String defaultNamespace;
    private boolean useDestinationsV2Columns;

    // Optional fields
    private Optional<Long> bufferMemoryLimit = Optional.empty();
    private long optimalBatchSizeBytes = 50 * 1024 * 1024;

    private Builder() {}

    public Builder setBufferMemoryLimit(final Optional<Long> bufferMemoryLimit) {
      this.bufferMemoryLimit = bufferMemoryLimit;
      return this;
    }

    public Builder setOptimalBatchSizeBytes(final long optimalBatchSizeBytes) {
      this.optimalBatchSizeBytes = optimalBatchSizeBytes;
      return this;
    }

    public StagingConsumerFactory build() {
      return new StagingConsumerFactory(
          outputRecordCollector,
          database,
          stagingOperations,
          namingResolver,
          config,
          catalog,
          purgeStagingData,
          typerDeduperValve,
          typerDeduper,
          parsedCatalog,
          defaultNamespace,
          useDestinationsV2Columns,
          bufferMemoryLimit,
          optimalBatchSizeBytes);
    }

  }

  public static Builder builder(
                                final Consumer<AirbyteMessage> outputRecordCollector,
                                final JdbcDatabase database,
                                final StagingOperations stagingOperations,
                                final NamingConventionTransformer namingResolver,
                                final JsonNode config,
                                final ConfiguredAirbyteCatalog catalog,
                                final boolean purgeStagingData,
                                final TypeAndDedupeOperationValve typerDeduperValve,
                                final TyperDeduper typerDeduper,
                                final ParsedCatalog parsedCatalog,
                                final String defaultNamespace,
                                final boolean useDestinationsV2Columns) {
    final Builder builder = new Builder();
    builder.outputRecordCollector = outputRecordCollector;
    builder.database = database;
    builder.stagingOperations = stagingOperations;
    builder.namingResolver = namingResolver;
    builder.config = config;
    builder.catalog = catalog;
    builder.purgeStagingData = purgeStagingData;
    builder.typerDeduperValve = typerDeduperValve;
    builder.typerDeduper = typerDeduper;
    builder.parsedCatalog = parsedCatalog;
    builder.defaultNamespace = defaultNamespace;
    builder.useDestinationsV2Columns = useDestinationsV2Columns;
    return builder;
  }

  public SerializedAirbyteMessageConsumer createAsync() {
    final List<WriteConfig> writeConfigs = createWriteConfigs(namingResolver, config, catalog, parsedCatalog, useDestinationsV2Columns);
    final var streamDescToWriteConfig = streamDescToWriteConfig(writeConfigs);
    final var flusher = new AsyncFlush(
        streamDescToWriteConfig,
        stagingOperations,
        database,
        catalog,
        typerDeduperValve,
        typerDeduper,
        optimalBatchSizeBytes,
        useDestinationsV2Columns);
    return new AsyncStreamConsumer(
        outputRecordCollector,
        GeneralStagingFunctions.onStartFunction(database, stagingOperations, writeConfigs, typerDeduper),
        // todo (cgardens) - wrapping the old close function to avoid more code churn.
        (hasFailed, streamSyncSummaries) -> {
          try {
            GeneralStagingFunctions.onCloseFunction(
                database,
                stagingOperations,
                writeConfigs,
                purgeStagingData,
                typerDeduper).accept(false, streamSyncSummaries);
          } catch (final Exception e) {
            throw new RuntimeException(e);
          }
        },
        flusher,
        catalog,
        new BufferManager(getMemoryLimit(bufferMemoryLimit)),
        defaultNamespace);
  }

  private static long getMemoryLimit(final Optional<Long> bufferMemoryLimit) {
    return bufferMemoryLimit.orElse((long) (Runtime.getRuntime().maxMemory() * MEMORY_LIMIT_RATIO));
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
                                                      final ParsedCatalog parsedCatalog,
                                                      final boolean useDestinationsV2Columns) {

    return catalog.getStreams().stream().map(toWriteConfig(namingResolver, config, parsedCatalog, useDestinationsV2Columns)).collect(toList());
  }

  private static Function<ConfiguredAirbyteStream, WriteConfig> toWriteConfig(final NamingConventionTransformer namingResolver,
                                                                              final JsonNode config,
                                                                              final ParsedCatalog parsedCatalog,
                                                                              final boolean useDestinationsV2Columns) {
    return stream -> {
      Preconditions.checkNotNull(stream.getDestinationSyncMode(), "Undefined destination sync mode");
      final AirbyteStream abStream = stream.getStream();
      final String streamName = abStream.getName();

      final String outputSchema;
      final String tableName;
      if (useDestinationsV2Columns) {
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
