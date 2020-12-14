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

package io.airbyte.protocol.models;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

public class CatalogHelpers {

  public static AirbyteCatalog createAirbyteCatalog(String streamName, Field... fields) {
    return new AirbyteCatalog().withStreams(Lists.newArrayList(createAirbyteStream(streamName, fields)));
  }

  public static AirbyteStream createAirbyteStream(String streamName, Field... fields) {
    return createAirbyteStream(streamName, Arrays.asList(fields));
  }

  public static AirbyteStream createAirbyteStream(String streamName, List<Field> fields) {
    return new AirbyteStream().withName(streamName).withJsonSchema(fieldsToJsonSchema(fields));
  }

  public static ConfiguredAirbyteCatalog createConfiguredAirbyteCatalog(String streamName, Field... fields) {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(createConfiguredAirbyteStream(streamName, fields)));
  }

  public static ConfiguredAirbyteStream createConfiguredAirbyteStream(String streamName, Field... fields) {
    return createConfiguredAirbyteStream(streamName, Arrays.asList(fields));
  }

  public static ConfiguredAirbyteStream createConfiguredAirbyteStream(String streamName, List<Field> fields) {
    return new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName(streamName).withJsonSchema(fieldsToJsonSchema(fields)));
  }

  public static ConfiguredAirbyteStream createIncrementalConfiguredAirbyteStream(
                                                                                 String streamName,
                                                                                 SyncMode syncMode,
                                                                                 String cursorFieldName,
                                                                                 Field... fields) {
    return createIncrementalConfiguredAirbyteStream(streamName, syncMode, cursorFieldName, Arrays.asList(fields));
  }

  public static ConfiguredAirbyteStream createIncrementalConfiguredAirbyteStream(
                                                                                 String streamName,
                                                                                 SyncMode syncMode,
                                                                                 String cursorFieldName,
                                                                                 List<Field> fields) {
    return new ConfiguredAirbyteStream()
        .withStream(new AirbyteStream()
            .withName(streamName)
            .withSupportedSyncModes(Collections.singletonList(syncMode))
            .withJsonSchema(fieldsToJsonSchema(fields)))
        .withSyncMode(syncMode)
        .withCursorField(Collections.singletonList(cursorFieldName));
  }

  /**
   * Convert a Catalog into a ConfiguredCatalog. This applies minimum default to the Catalog to make
   * it a valid ConfiguredCatalog.
   *
   * @param catalog - Catalog to be converted.
   * @return - ConfiguredCatalog based of off the input catalog.
   */
  public static ConfiguredAirbyteCatalog toDefaultConfiguredCatalog(AirbyteCatalog catalog) {
    return new ConfiguredAirbyteCatalog()
        .withStreams(catalog.getStreams()
            .stream()
            .map(CatalogHelpers::toDefaultConfiguredStream)
            .collect(Collectors.toList()));
  }

  public static ConfiguredAirbyteStream toDefaultConfiguredStream(AirbyteStream stream) {
    return new ConfiguredAirbyteStream()
        .withStream(stream)
        .withSyncMode(SyncMode.FULL_REFRESH)
        .withCursorField(new ArrayList<>());
  }

  public static JsonNode fieldsToJsonSchema(Field... fields) {
    return fieldsToJsonSchema(Arrays.asList(fields));
  }

  public static JsonNode fieldsToJsonSchema(List<Field> fields) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("type", "object")
        .put("properties", fields
            .stream()
            .collect(Collectors.toMap(
                Field::getName,
                field -> ImmutableMap.of("type", field.getTypeAsJsonSchemaString()))))
        .build());
  }

  /**
   * Gets the keys from the top-level properties object in the json schema.
   *
   * @param stream - airbyte stream
   * @return field names
   */
  @SuppressWarnings("unchecked")
  public static Set<String> getTopLevelFieldNames(final ConfiguredAirbyteStream stream) {
    // it is json, so the key has to be a string.
    final Map<String, Object> object = Jsons.object(stream.getStream().getJsonSchema().get("properties"), Map.class);
    return object.keySet();
  }

  /**
   * @param node any json node
   * @return a set of all keys for all objects within the node
   */
  @VisibleForTesting
  protected static Set<String> getAllFieldNames(JsonNode node) {
    Set<String> allFieldNames = new HashSet<>();

    if (node.has("properties")) {
      JsonNode properties = node.get("properties");
      Iterator<String> fieldNames = properties.fieldNames();
      while (fieldNames.hasNext()) {
        String fieldName = fieldNames.next();
        allFieldNames.add(fieldName);
        JsonNode fieldValue = properties.get(fieldName);
        if (fieldValue.isObject()) {
          allFieldNames.addAll(getAllFieldNames(fieldValue));
        }
      }
    }

    return allFieldNames;
  }

}
