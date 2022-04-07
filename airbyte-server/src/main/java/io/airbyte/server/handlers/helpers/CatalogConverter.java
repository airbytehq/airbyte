/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers.helpers;

import io.airbyte.api.model.SyncMode;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.text.Names;
import java.util.List;
import java.util.stream.Collectors;
import javax.inject.Singleton;

/**
 * Convert classes between io.airbyte.protocol.models and io.airbyte.api.model
 */
@Singleton
public class CatalogConverter {

  private io.airbyte.api.model.AirbyteStream toApi(final io.airbyte.protocol.models.AirbyteStream stream) {
    return new io.airbyte.api.model.AirbyteStream()
        .jsonSchema(stream.getJsonSchema())
        .name(stream.getName())
        .supportedSyncModes(Enums.convertListTo(stream.getSupportedSyncModes(), io.airbyte.api.model.SyncMode.class))
        .sourceDefinedCursor(stream.getSourceDefinedCursor())
        .defaultCursorField(stream.getDefaultCursorField())
        .sourceDefinedPrimaryKey(stream.getSourceDefinedPrimaryKey())
        .namespace(stream.getNamespace());
  }

  private io.airbyte.protocol.models.AirbyteStream toProtocol(final io.airbyte.api.model.AirbyteStream stream) {
    return new io.airbyte.protocol.models.AirbyteStream()
        .withName(stream.getName())
        .withJsonSchema(stream.getJsonSchema())
        .withSupportedSyncModes(Enums.convertListTo(stream.getSupportedSyncModes(), io.airbyte.protocol.models.SyncMode.class))
        .withSourceDefinedCursor(stream.getSourceDefinedCursor())
        .withDefaultCursorField(stream.getDefaultCursorField())
        .withSourceDefinedPrimaryKey(stream.getSourceDefinedPrimaryKey())
        .withNamespace(stream.getNamespace());
  }

  public io.airbyte.api.model.AirbyteCatalog toApi(final io.airbyte.protocol.models.AirbyteCatalog catalog) {
    return new io.airbyte.api.model.AirbyteCatalog()
        .streams(catalog.getStreams()
            .stream()
            .map(this::toApi)
            .map(s -> new io.airbyte.api.model.AirbyteStreamAndConfiguration()
                .stream(s)
                .config(generateDefaultConfiguration(s)))
            .collect(Collectors.toList()));
  }

  private io.airbyte.api.model.AirbyteStreamConfiguration generateDefaultConfiguration(final io.airbyte.api.model.AirbyteStream stream) {
    final SyncMode syncMode =
        stream.getSupportedSyncModes().size() > 0 ? stream.getSupportedSyncModes().get(0) : io.airbyte.api.model.SyncMode.INCREMENTAL;
    final io.airbyte.api.model.AirbyteStreamConfiguration result = new io.airbyte.api.model.AirbyteStreamConfiguration()
        .aliasName(Names.toAlphanumericAndUnderscore(stream.getName()))
        .cursorField(stream.getDefaultCursorField())
        .destinationSyncMode(io.airbyte.api.model.DestinationSyncMode.APPEND)
        .primaryKey(stream.getSourceDefinedPrimaryKey())
        .selected(true)
        .syncMode(syncMode);
    return result;
  }

  public io.airbyte.api.model.AirbyteCatalog toApi(final io.airbyte.protocol.models.ConfiguredAirbyteCatalog catalog) {
    final List<io.airbyte.api.model.AirbyteStreamAndConfiguration> streams = catalog.getStreams()
        .stream()
        .map(configuredStream -> {
          final io.airbyte.api.model.AirbyteStreamConfiguration configuration = new io.airbyte.api.model.AirbyteStreamConfiguration()
              .cursorField(configuredStream.getCursorField())
              .primaryKey(configuredStream.getPrimaryKey())
              .aliasName(Names.toAlphanumericAndUnderscore(configuredStream.getStream().getName()))
              .destinationSyncMode(Enums.convertTo(configuredStream.getDestinationSyncMode(), io.airbyte.api.model.DestinationSyncMode.class))
              .selected(true)
              .syncMode(Enums.convertTo(configuredStream.getSyncMode(), io.airbyte.api.model.SyncMode.class));
          return new io.airbyte.api.model.AirbyteStreamAndConfiguration()
              .stream(toApi(configuredStream.getStream()))
              .config(configuration);
        })
        .collect(Collectors.toList());
    return new io.airbyte.api.model.AirbyteCatalog()
        .streams(streams);
  }

  public io.airbyte.protocol.models.ConfiguredAirbyteCatalog toProtocol(final io.airbyte.api.model.AirbyteCatalog catalog) {
    final List<io.airbyte.protocol.models.ConfiguredAirbyteStream> streams = catalog.getStreams()
        .stream()
        .filter(s -> s.getConfig().getSelected())
        .map(s -> new io.airbyte.protocol.models.ConfiguredAirbyteStream()
            .withStream(toProtocol(s.getStream()))
            .withSyncMode(Enums.convertTo(s.getConfig().getSyncMode(), io.airbyte.protocol.models.SyncMode.class))
            .withCursorField(s.getConfig().getCursorField())
            .withDestinationSyncMode(Enums.convertTo(s.getConfig().getDestinationSyncMode(),
                io.airbyte.protocol.models.DestinationSyncMode.class))
            .withPrimaryKey(s.getConfig().getPrimaryKey()))
        .collect(Collectors.toList());
    return new io.airbyte.protocol.models.ConfiguredAirbyteCatalog()
        .withStreams(streams);
  }

}
