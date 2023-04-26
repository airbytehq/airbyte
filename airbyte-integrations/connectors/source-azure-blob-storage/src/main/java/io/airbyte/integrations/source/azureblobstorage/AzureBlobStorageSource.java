/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.azureblobstorage;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.azureblobstorage.format.JsonlAzureBlobStorageOperations;
import io.airbyte.integrations.source.relationaldb.CursorInfo;
import io.airbyte.integrations.source.relationaldb.StateDecoratingIterator;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.integrations.source.relationaldb.state.StateManagerFactory;
import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.List;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AzureBlobStorageSource extends BaseConnector implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(AzureBlobStorageSource.class);

  private final FeatureFlags featureFlags = new EnvVariableFeatureFlags();

  public static void main(final String[] args) throws Exception {
    final Source source = new AzureBlobStorageSource();
    LOGGER.info("starting Source: {}", AzureBlobStorageSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed Source: {}", AzureBlobStorageSource.class);
  }

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    var azureBlobStorageConfig = AzureBlobStorageConfig.createAzureBlobStorageConfig(config);
    try {
      var azureBlobStorageOperations = switch (azureBlobStorageConfig.formatConfig().format()) {
        case JSONL -> new JsonlAzureBlobStorageOperations(azureBlobStorageConfig);
      };
      azureBlobStorageOperations.listBlobs();

      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.SUCCEEDED);
    } catch (Exception e) {
      LOGGER.error("Error while listing Azure Blob Storage blobs with reason: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(AirbyteConnectionStatus.Status.FAILED);
    }

  }

  @Override
  public AirbyteCatalog discover(JsonNode config) {
    var azureBlobStorageConfig = AzureBlobStorageConfig.createAzureBlobStorageConfig(config);

    var azureBlobStorageOperations = switch (azureBlobStorageConfig.formatConfig().format()) {
      case JSONL -> new JsonlAzureBlobStorageOperations(azureBlobStorageConfig);
    };

    JsonNode schema = azureBlobStorageOperations.inferSchema();

    return new AirbyteCatalog()
        .withStreams(List.of(new AirbyteStream()
            .withName(azureBlobStorageConfig.containerName())
            .withJsonSchema(schema)
            .withSourceDefinedCursor(true)
            .withDefaultCursorField(List.of(AzureBlobAdditionalProperties.LAST_MODIFIED))
            .withSupportedSyncModes(List.of(SyncMode.INCREMENTAL, SyncMode.FULL_REFRESH))));
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(JsonNode config, ConfiguredAirbyteCatalog catalog, JsonNode state) {

    final var streamState =
        AzureBlobStorageStateManager.deserializeStreamState(state, featureFlags.useStreamCapableState());

    final StateManager stateManager = StateManagerFactory
        .createStateManager(streamState.airbyteStateType(), streamState.airbyteStateMessages(), catalog);

    var azureBlobStorageConfig = AzureBlobStorageConfig.createAzureBlobStorageConfig(config);
    var azureBlobStorageOperations = switch (azureBlobStorageConfig.formatConfig().format()) {
      case JSONL -> new JsonlAzureBlobStorageOperations(azureBlobStorageConfig);
    };

    // only one stream per connection
    var streamIterators = catalog.getStreams().stream()
        .map(cas -> switch (cas.getSyncMode()) {
        case INCREMENTAL -> readIncremental(azureBlobStorageOperations, cas.getStream(), cas.getCursorField().get(0),
            stateManager);
        case FULL_REFRESH -> readFullRefresh(azureBlobStorageOperations, cas.getStream());
        })
        .toList();

    return AutoCloseableIterators.concatWithEagerClose(streamIterators, AirbyteTraceMessageUtility::emitStreamStatusTrace);

  }

  private AutoCloseableIterator<AirbyteMessage> readIncremental(AzureBlobStorageOperations azureBlobStorageOperations,
                                                                AirbyteStream airbyteStream,
                                                                String cursorField,
                                                                StateManager stateManager) {
    var streamPair = new AirbyteStreamNameNamespacePair(airbyteStream.getName(), airbyteStream.getNamespace());

    Optional<CursorInfo> cursorInfo = stateManager.getCursorInfo(streamPair);

    var messageStream = cursorInfo
        .map(cursor -> {
          var offsetDateTime = cursor.getCursor() != null ? OffsetDateTime.parse(cursor.getCursor()) : null;
          return azureBlobStorageOperations.readBlobs(offsetDateTime);
        })
        .orElse(azureBlobStorageOperations.readBlobs(null))
        .stream()
        .map(jn -> new AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(airbyteStream.getName())
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(jn)));

    final io.airbyte.protocol.models.AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair =
        AirbyteStreamUtils.convertFromAirbyteStream(airbyteStream);

    return AutoCloseableIterators.transform(autoCloseableIterator -> new StateDecoratingIterator(
        autoCloseableIterator,
        stateManager,
        streamPair,
        cursorField,
        cursorInfo.map(CursorInfo::getCursor).orElse(null),
        JsonSchemaPrimitiveUtil.JsonSchemaPrimitive.TIMESTAMP_WITH_TIMEZONE_V1,
        // TODO (itaseski) emit state after every record/blob since they can be sorted in increasing order
        0),
        AutoCloseableIterators.fromStream(messageStream, airbyteStreamNameNamespacePair),
        airbyteStreamNameNamespacePair);
  }

  private AutoCloseableIterator<AirbyteMessage> readFullRefresh(AzureBlobStorageOperations azureBlobStorageOperations,
                                                                AirbyteStream airbyteStream) {

    final io.airbyte.protocol.models.AirbyteStreamNameNamespacePair airbyteStreamNameNamespacePair =
        AirbyteStreamUtils.convertFromAirbyteStream(airbyteStream);

    var messageStream = azureBlobStorageOperations
        .readBlobs(null)
        .stream()
        .map(jn -> new AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(airbyteStream.getName())
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(jn)));

    return AutoCloseableIterators.fromStream(messageStream, airbyteStreamNameNamespacePair);
  }

}
