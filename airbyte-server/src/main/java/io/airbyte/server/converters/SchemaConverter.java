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

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.text.Names;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Spliterators;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

/**
 * Convert classes between io.airbyte.protocol.models and io.airbyte.api.model
 */
public class SchemaConverter {

  public static io.airbyte.api.model.AirbyteStream convertTo(final io.airbyte.protocol.models.AirbyteStream stream) {
    return new io.airbyte.api.model.AirbyteStream()
        .name(stream.getName())
        .jsonSchema(stream.getJsonSchema())
        .supportedSyncModes(Enums.convertListTo(stream.getSupportedSyncModes(), io.airbyte.api.model.SyncMode.class))
        .sourceDefinedCursor(stream.getSourceDefinedCursor())
        .defaultCursorField(stream.getDefaultCursorField());
  }

  public static io.airbyte.protocol.models.AirbyteStream convertTo(final io.airbyte.api.model.AirbyteStream stream) {
    return new io.airbyte.protocol.models.AirbyteStream()
        .withName(stream.getName())
        .withJsonSchema(stream.getJsonSchema())
        .withSupportedSyncModes(Enums.convertListTo(stream.getSupportedSyncModes(), io.airbyte.protocol.models.SyncMode.class))
        .withSourceDefinedCursor(stream.getSourceDefinedCursor())
        .withDefaultCursorField(stream.getDefaultCursorField());
  }

  private static io.airbyte.api.model.AirbyteStreamField convertTo(io.airbyte.protocol.models.ConfiguredAirbyteStreamField fields) {
    // TODO
    return null;
  }

  private static io.airbyte.protocol.models.ConfiguredAirbyteStreamField convertTo(io.airbyte.api.model.AirbyteStreamField airbyteStreamField) {
    // TODO
    return null;
  }

  public static io.airbyte.api.model.AirbyteCatalog convertTo(final io.airbyte.protocol.models.AirbyteCatalog catalog) {
    return new io.airbyte.api.model.AirbyteCatalog()
        .streams(catalog.getStreams()
            .stream()
            .map(s -> new io.airbyte.api.model.AirbyteStreamAndConfiguration()
                .stream(SchemaConverter.convertTo(s))
                ._configuration(getDefaultAirbyteStreamConfiguration(s)))
            .collect(Collectors.toList()));
  }

  public static io.airbyte.api.model.AirbyteCatalog convertTo(final io.airbyte.protocol.models.ConfiguredAirbyteCatalog catalog) {
    final List<io.airbyte.api.model.AirbyteStreamAndConfiguration> streams = catalog.getStreams()
        .stream()
        .map(configuredStream -> {
          final io.airbyte.api.model.AirbyteStreamConfiguration configuration = new io.airbyte.api.model.AirbyteStreamConfiguration()
              .syncMode(Enums.convertTo(configuredStream.getSyncMode(), io.airbyte.api.model.SyncMode.class))
              .cursorField(configuredStream.getCursorField())
              .aliasName(Names.toAlphanumericAndUnderscore(configuredStream.getStream().getName()))
              .fields(configuredStream.getFields().stream().map(SchemaConverter::convertTo).collect(Collectors.toList()))
              .selected(true);
          return new io.airbyte.api.model.AirbyteStreamAndConfiguration()
              .stream(convertTo(configuredStream.getStream()))
              ._configuration(configuration);
        })
        .collect(Collectors.toList());
    return new io.airbyte.api.model.AirbyteCatalog().streams(streams);
  }

  public static io.airbyte.protocol.models.ConfiguredAirbyteCatalog convertTo(final io.airbyte.api.model.AirbyteCatalog catalog) {
    final List<io.airbyte.protocol.models.ConfiguredAirbyteStream> streams = catalog.getStreams()
        .stream()
        .filter(s -> s.getConfiguration().getSelected())
        .map(s -> new io.airbyte.protocol.models.ConfiguredAirbyteStream()
            .withStream(convertTo(s.getStream()))
            .withSyncMode(Enums.convertTo(s.getConfiguration().getSyncMode(), io.airbyte.protocol.models.SyncMode.class))
            .withCursorField(s.getConfiguration().getCursorField())
            .withAliasName(s.getConfiguration().getAliasName())
            .withFields(s.getConfiguration().getFields().stream().map(SchemaConverter::convertTo).collect(Collectors.toList())))
        .collect(Collectors.toList());
    return new io.airbyte.protocol.models.ConfiguredAirbyteCatalog()
        .withStreams(streams);
  }

  private static io.airbyte.api.model.AirbyteStreamConfiguration getDefaultAirbyteStreamConfiguration(io.airbyte.protocol.models.AirbyteStream stream) {
    final List<io.airbyte.api.model.AirbyteStreamField> fields = extractProperties(stream.getJsonSchema())
        .entrySet()
        .stream()
        .map(entry -> {
          final JsonNode node = entry.getValue();
          final String name = entry.getKey().get(0);
          final List<String> path = new ArrayList<>(entry.getKey());
          Collections.reverse(path);
          return new io.airbyte.api.model.AirbyteStreamField()
              .path(String.join(".", path))
              .name(name)
              .aliasName(Names.toAlphanumericAndUnderscore(name))
              .dataType(jsonSchemaTypesToDataType(node.get("type")))
              .isPrimaryKey(false)
              .isNested(path.size() > 1)
              .selected(true);
        })
        .collect(Collectors.toList());
    final io.airbyte.api.model.AirbyteStreamConfiguration result = new io.airbyte.api.model.AirbyteStreamConfiguration()
        .cursorField(stream.getDefaultCursorField())
        .aliasName(Names.toAlphanumericAndUnderscore(stream.getName()))
        .selected(true)
        .fields(fields);
    if (stream.getSupportedSyncModes().size() > 0)
      result.setSyncMode(Enums.convertTo(stream.getSupportedSyncModes().get(0), io.airbyte.api.model.SyncMode.class));
    else
      result.setSyncMode(io.airbyte.api.model.SyncMode.INCREMENTAL);
    return result;
  }

  public static Map<List<String>, JsonNode> extractProperties(final JsonNode root) {
    Map<List<String>, JsonNode> result = new HashMap<>();
    List<String> pathStack = new ArrayList<>();
    // todo (cgardens) - assumes it is json schema type object with properties. not a stellar
    // assumption.
    extractNestedProperties(result, pathStack, root);
    return result;
  }

  private static void extractNestedProperties(Map<List<String>, JsonNode> result, final List<String> pathStack, final JsonNode root) {
    final Iterator<Entry<String, JsonNode>> iterator = root.fields();
    while (iterator.hasNext()) {
      final Entry<String, JsonNode> entry = iterator.next();
      final String name = entry.getKey();
      final JsonNode node = entry.getValue();
      final List<String> path = new ArrayList<>();
      path.add(name);
      path.addAll(pathStack);
      if (node.has("type") && io.airbyte.api.model.DataType.OBJECT != jsonSchemaTypesToDataType(node.get("type"))) {
        result.put(path, node);
      }
      if (!name.equals("type")) {
        extractNestedProperties(result, path, node);
      }
    }
  }

  /**
   * JsonSchema tends to have 2 types for fields one of which is null. The null is pretty irrelevant,
   * so look at types and find the first non-null one and use that.
   *
   * @param node - list of types from jsonschema.
   * @return reduce down to one type which best matches the field's data type
   */
  private static io.airbyte.api.model.DataType jsonSchemaTypesToDataType(JsonNode node) {
    if (node.isTextual()) {
      return io.airbyte.api.model.DataType.valueOf(convertToNumberIfInteger(node.asText().toUpperCase()));
    } else if (node.isArray()) {
      return StreamSupport.stream(Spliterators.spliteratorUnknownSize(node.elements(), 0), false)
          .filter(typeString -> !typeString.asText().equalsIgnoreCase("NULL"))
          .map(typeString -> io.airbyte.api.model.DataType.valueOf(convertToNumberIfInteger(typeString.asText().toUpperCase())))
          .findFirst()
          // todo (cgardens) - or throw?
          .orElse(io.airbyte.api.model.DataType.STRING);
    } else {
      throw new IllegalArgumentException("Unknown jsonschema type:" + Jsons.serialize(node));
    }
  }

  // TODO HACK (jrhizor): convert Integer to Number until we have a more solid typing system
  private static String convertToNumberIfInteger(String type) {
    if (type.equalsIgnoreCase("INTEGER")) {
      return "NUMBER";
    } else {
      return type;
    }
  }

}
