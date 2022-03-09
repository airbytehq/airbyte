/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * Helper class for Catalog and Stream related operations. Generally only used in tests.
 */
public class CatalogHelpers {

  public static AirbyteCatalog createAirbyteCatalog(final String streamName, final Field... fields) {
    return new AirbyteCatalog().withStreams(Lists.newArrayList(createAirbyteStream(streamName, fields)));
  }

  public static AirbyteStream createAirbyteStream(final String streamName, final Field... fields) {
    // Namespace is null since not all sources set it.
    return createAirbyteStream(streamName, null, Arrays.asList(fields));
  }

  public static AirbyteStream createAirbyteStream(final String streamName, final String namespace, final Field... fields) {
    return createAirbyteStream(streamName, namespace, Arrays.asList(fields));
  }

  public static AirbyteStream createAirbyteStream(final String streamName, final String namespace, final List<Field> fields) {
    return new AirbyteStream().withName(streamName).withNamespace(namespace).withJsonSchema(fieldsToJsonSchema(fields));
  }

  public static ConfiguredAirbyteCatalog createConfiguredAirbyteCatalog(final String streamName, final String namespace, final Field... fields) {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(createConfiguredAirbyteStream(streamName, namespace, fields)));
  }

  public static ConfiguredAirbyteCatalog createConfiguredAirbyteCatalog(final String streamName, final String namespace, final List<Field> fields) {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(createConfiguredAirbyteStream(streamName, namespace, fields)));
  }

  public static ConfiguredAirbyteStream createConfiguredAirbyteStream(final String streamName, final String namespace, final Field... fields) {
    return createConfiguredAirbyteStream(streamName, namespace, Arrays.asList(fields));
  }

  public static ConfiguredAirbyteStream createConfiguredAirbyteStream(final String streamName, final String namespace, final List<Field> fields) {
    return new ConfiguredAirbyteStream()
        .withStream(new AirbyteStream().withName(streamName).withNamespace(namespace).withJsonSchema(fieldsToJsonSchema(fields)))
        .withSyncMode(SyncMode.FULL_REFRESH).withDestinationSyncMode(DestinationSyncMode.OVERWRITE);
  }

  /**
   * Convert a Catalog into a ConfiguredCatalog. This applies minimum default to the Catalog to make
   * it a valid ConfiguredCatalog.
   *
   * @param catalog - Catalog to be converted.
   * @return - ConfiguredCatalog based of off the input catalog.
   */
  public static ConfiguredAirbyteCatalog toDefaultConfiguredCatalog(final AirbyteCatalog catalog) {
    return new ConfiguredAirbyteCatalog()
        .withStreams(catalog.getStreams()
            .stream()
            .map(CatalogHelpers::toDefaultConfiguredStream)
            .collect(Collectors.toList()));
  }

  public static ConfiguredAirbyteStream toDefaultConfiguredStream(final AirbyteStream stream) {
    return new ConfiguredAirbyteStream()
        .withStream(stream)
        .withSyncMode(SyncMode.FULL_REFRESH)
        .withCursorField(new ArrayList<>())
        .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
        .withPrimaryKey(new ArrayList<>());
  }

  public static JsonNode fieldsToJsonSchema(final Field... fields) {
    return fieldsToJsonSchema(Arrays.asList(fields));
  }

  /**
   * Maps a list of fields into a JsonSchema object with names and types. This method will throw if it
   * receives multiple fields with the same name.
   *
   * @param fields fields to map to JsonSchema
   * @return JsonSchema representation of the fields.
   */
  public static JsonNode fieldsToJsonSchema(final List<Field> fields) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("type", "object")
        .put("properties", fields
            .stream()
            .collect(Collectors.toMap(
                Field::getName,
                field -> field.getType().getJsonSchemaTypeMap())))
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
  protected static Set<String> getAllFieldNames(final JsonNode node) {
    final Set<String> allFieldNames = new HashSet<>();

    if (node.has("properties")) {
      final JsonNode properties = node.get("properties");
      final Iterator<String> fieldNames = properties.fieldNames();
      while (fieldNames.hasNext()) {
        final String fieldName = fieldNames.next();
        allFieldNames.add(fieldName);
        final JsonNode fieldValue = properties.get(fieldName);
        if (fieldValue.isObject()) {
          allFieldNames.addAll(getAllFieldNames(fieldValue));
        }
      }
    }

    return allFieldNames;
  }

}
