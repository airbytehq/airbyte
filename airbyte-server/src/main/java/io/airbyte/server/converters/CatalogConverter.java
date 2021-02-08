/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.server.converters;

import io.airbyte.api.model.AirbyteStream;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.text.Names;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.tools.StringUtils;

/**
 * Convert classes between io.airbyte.protocol.models and io.airbyte.api.model
 */
public class CatalogConverter {

  private static io.airbyte.api.model.AirbyteStream toApi(final io.airbyte.protocol.models.AirbyteStream stream) {
    return new io.airbyte.api.model.AirbyteStream()
        .name(stream.getName())
        .namespace(stream.getNamespace())
        .jsonSchema(stream.getJsonSchema())
        .supportedSyncModes(Enums.convertListTo(stream.getSupportedSyncModes(), io.airbyte.api.model.SyncMode.class))
        .sourceDefinedCursor(stream.getSourceDefinedCursor())
        .defaultCursorField(stream.getDefaultCursorField());
  }

  private static io.airbyte.protocol.models.AirbyteStream toProtocol(final io.airbyte.api.model.AirbyteStream stream) {
    return new io.airbyte.protocol.models.AirbyteStream()
        .withName(stream.getName())
        .withNamespace(stream.getNamespace())
        .withJsonSchema(stream.getJsonSchema())
        .withSupportedSyncModes(Enums.convertListTo(stream.getSupportedSyncModes(), io.airbyte.protocol.models.SyncMode.class))
        .withSourceDefinedCursor(stream.getSourceDefinedCursor())
        .withDefaultCursorField(stream.getDefaultCursorField());
  }

  public static io.airbyte.api.model.AirbyteCatalog toApi(final io.airbyte.protocol.models.AirbyteCatalog catalog, final String namespacePrefix) {
    return new io.airbyte.api.model.AirbyteCatalog()
        .streams(catalog.getStreams()
            .stream()
            .map(CatalogConverter::toApi)
            .map(s -> new io.airbyte.api.model.AirbyteStreamAndConfiguration()
                .stream(s)
                .config(generateDefaultConfiguration(s, namespacePrefix)))
            .collect(Collectors.toList()));
  }

  private static io.airbyte.api.model.AirbyteStreamConfiguration generateDefaultConfiguration(final AirbyteStream stream,
                                                                                              final String namespacePrefix) {
    final String namespace = generateDefaultNamespace(namespacePrefix, stream.getNamespace());
    io.airbyte.api.model.AirbyteStreamConfiguration result = new io.airbyte.api.model.AirbyteStreamConfiguration()
        .cursorField(stream.getDefaultCursorField())
        .aliasName(Names.toAlphanumericAndUnderscore(stream.getName()))
        .targetNamespace(namespace)
        .selected(true);
    if (stream.getSupportedSyncModes().size() > 0)
      result.setSyncMode(stream.getSupportedSyncModes().get(0));
    else
      result.setSyncMode(io.airbyte.api.model.SyncMode.INCREMENTAL);
    return result;
  }

  public static String generateDefaultNamespace(String namespacePrefix, String namespace) throws IllegalArgumentException {
    final String result;
    if (!StringUtils.isBlank(namespacePrefix)) {
      namespacePrefix = namespacePrefix.trim();
      if (!StringUtils.isBlank(namespace)) {
        namespace = namespace.trim();
        result = namespacePrefix + '_' + namespace;
      } else {
        result = namespacePrefix;
      }
    } else {
      if (namespace != null) {
        result = namespace.trim();
      } else {
        result = "";
      }
    }
    if (StringUtils.isBlank(result)) {
      throw new IllegalArgumentException("Empty namespace");
    }
    return Names.toAlphanumericAndUnderscore(result);
  }

  public static io.airbyte.api.model.AirbyteCatalog toApi(final io.airbyte.protocol.models.ConfiguredAirbyteCatalog catalog) {
    final List<io.airbyte.api.model.AirbyteStreamAndConfiguration> streams = catalog.getStreams()
        .stream()
        .map(configuredStream -> {
          final io.airbyte.api.model.AirbyteStreamConfiguration configuration = new io.airbyte.api.model.AirbyteStreamConfiguration()
              .syncMode(Enums.convertTo(configuredStream.getSyncMode(), io.airbyte.api.model.SyncMode.class))
              .cursorField(configuredStream.getCursorField())
              .aliasName(configuredStream.getAliasName())
              .targetNamespace(configuredStream.getTargetNamespace())
              .selected(configuredStream.getSelected());
          return new io.airbyte.api.model.AirbyteStreamAndConfiguration()
              .stream(toApi(configuredStream.getStream()))
              .config(configuration);
        })
        .collect(Collectors.toList());
    return new io.airbyte.api.model.AirbyteCatalog().streams(streams);
  }

  public static io.airbyte.protocol.models.ConfiguredAirbyteCatalog toProtocol(final io.airbyte.api.model.AirbyteCatalog catalog) {
    final List<io.airbyte.protocol.models.ConfiguredAirbyteStream> streams = catalog.getStreams()
        .stream()
        .map(s -> new io.airbyte.protocol.models.ConfiguredAirbyteStream()
            .withStream(toProtocol(s.getStream()))
            .withSyncMode(Enums.convertTo(s.getConfig().getSyncMode(), io.airbyte.protocol.models.SyncMode.class))
            .withCursorField(s.getConfig().getCursorField())
            .withAliasName(s.getConfig().getAliasName())
            .withTargetNamespace(s.getConfig().getTargetNamespace())
            .withSelected(s.getConfig().getSelected()))
        .collect(Collectors.toList());
    return new io.airbyte.protocol.models.ConfiguredAirbyteCatalog()
        .withStreams(streams);
  }

}
