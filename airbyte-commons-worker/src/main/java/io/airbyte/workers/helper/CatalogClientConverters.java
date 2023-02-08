/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.text.Names;
import io.airbyte.protocol.models.AirbyteStream;
import java.util.stream.Collectors;

/**
 * Utilities to convert Catalog protocol to Catalog API client. This class was similar to existing
 * logic in CatalogConverter.java; But code can't be shared because the protocol model is
 * essentially converted to two different api models. Thus, if we need to change logic on either
 * place we have to take care of the other one too.
 */
public class CatalogClientConverters {

  /**
   * Converts a protocol AirbyteCatalog to an OpenAPI client versioned AirbyteCatalog.
   */
  public static io.airbyte.api.client.model.generated.AirbyteCatalog toAirbyteCatalogClientApi(
                                                                                               final io.airbyte.protocol.models.AirbyteCatalog catalog) {
    return new io.airbyte.api.client.model.generated.AirbyteCatalog()
        .streams(catalog.getStreams()
            .stream()
            .map(stream -> toAirbyteStreamClientApi(stream))
            .map(s -> new io.airbyte.api.client.model.generated.AirbyteStreamAndConfiguration()
                .stream(s)
                .config(generateDefaultConfiguration(s)))
            .collect(Collectors.toList()));
  }

  private static io.airbyte.api.client.model.generated.AirbyteStreamConfiguration generateDefaultConfiguration(
                                                                                                               final io.airbyte.api.client.model.generated.AirbyteStream stream) {
    final io.airbyte.api.client.model.generated.AirbyteStreamConfiguration result =
        new io.airbyte.api.client.model.generated.AirbyteStreamConfiguration()
            .aliasName(Names.toAlphanumericAndUnderscore(stream.getName()))
            .cursorField(stream.getDefaultCursorField())
            .destinationSyncMode(io.airbyte.api.client.model.generated.DestinationSyncMode.APPEND)
            .primaryKey(stream.getSourceDefinedPrimaryKey())
            .selected(true);
    if (stream.getSupportedSyncModes().size() > 0) {
      result.setSyncMode(Enums.convertTo(stream.getSupportedSyncModes().get(0),
          io.airbyte.api.client.model.generated.SyncMode.class));
    } else {
      result.setSyncMode(io.airbyte.api.client.model.generated.SyncMode.INCREMENTAL);
    }
    return result;
  }

  private static io.airbyte.api.client.model.generated.AirbyteStream toAirbyteStreamClientApi(
                                                                                              final AirbyteStream stream) {
    return new io.airbyte.api.client.model.generated.AirbyteStream()
        .name(stream.getName())
        .jsonSchema(stream.getJsonSchema())
        .supportedSyncModes(Enums.convertListTo(stream.getSupportedSyncModes(),
            io.airbyte.api.client.model.generated.SyncMode.class))
        .sourceDefinedCursor(stream.getSourceDefinedCursor())
        .defaultCursorField(stream.getDefaultCursorField())
        .sourceDefinedPrimaryKey(stream.getSourceDefinedPrimaryKey())
        .namespace(stream.getNamespace());
  }

}
