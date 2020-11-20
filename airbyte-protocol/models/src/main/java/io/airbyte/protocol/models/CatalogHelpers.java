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
import com.google.common.collect.Multimap;
import com.google.common.collect.Multimaps;
import io.airbyte.commons.json.Jsons;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.lang3.StringUtils;

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
                field -> ImmutableMap.of("type", field.getTypeAsJsonSchemaString()),
                (a, b) -> a)))
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

  /**
   * @param identifier stream name or field name
   * @return if the identifier matches the alphanumeric+underscore requirement for identifiers
   */
  public static boolean isValidIdentifier(String identifier) {
    // todo (cgardens) - remove $ once mailchimp is fixed.
    final String s = identifier.replaceAll("[-_.$]", "");
    return StringUtils.isAlphanumeric(s);
  }

  /**
   * @param catalog airbyte catalog
   * @return list of stream names in the catalog that are invalid
   */
  public static List<String> getInvalidStreamNames(AirbyteCatalog catalog) {
    return getInvalidStreamNames(catalog.getStreams().stream().map(AirbyteStream::getName));
  }

  /**
   * @param catalog configured airbyte catalog
   * @return list of stream names in the catalog that are invalid
   */
  public static List<String> getInvalidStreamNames(ConfiguredAirbyteCatalog catalog) {
    return getInvalidStreamNames(catalog.getStreams().stream().map(ConfiguredAirbyteStream::getStream).map(AirbyteStream::getName));
  }

  private static List<String> getInvalidStreamNames(Stream<String> names) {
    return names
        .filter(streamName -> !isValidIdentifier(streamName))
        .collect(Collectors.toList());
  }

  /**
   * @param catalog airbyte catalog
   * @return multimap of stream names to all invalid field names in that stream
   */
  public static Multimap<String, String> getInvalidFieldNames(AirbyteCatalog catalog) {
    return getInvalidFieldNames(getStreamNameToJsonSchema(catalog));
  }

  /**
   * @param catalog configured airbyte catalog
   * @return multimap of stream names to all invalid field names in that stream
   */
  public static Multimap<String, String> getInvalidFieldNames(ConfiguredAirbyteCatalog catalog) {
    return getInvalidFieldNames(getStreamNameToJsonSchema(catalog));
  }

  private static Map<String, JsonNode> getStreamNameToJsonSchema(AirbyteCatalog catalog) {
    return catalog.getStreams()
        .stream()
        .collect(Collectors.toMap(AirbyteStream::getName, AirbyteStream::getJsonSchema));
  }

  private static Map<String, JsonNode> getStreamNameToJsonSchema(ConfiguredAirbyteCatalog catalog) {
    return catalog.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .collect(Collectors.toMap(AirbyteStream::getName, AirbyteStream::getJsonSchema));
  }

  private static Multimap<String, String> getInvalidFieldNames(Map<String, JsonNode> streamNameToJsonSchema) {
    final Multimap<String, String> streamNameToInvalidFieldNames = Multimaps.newSetMultimap(new HashMap<>(), HashSet::new);

    for (final Map.Entry<String, JsonNode> entry : streamNameToJsonSchema.entrySet()) {
      final Set<String> invalidFieldNames = getAllFieldNames(entry.getValue())
          .stream()
          .filter(streamName -> !isValidIdentifier(streamName))
          .collect(Collectors.toSet());

      streamNameToInvalidFieldNames.putAll(entry.getKey(), invalidFieldNames);
    }

    return streamNameToInvalidFieldNames;
  }

}
