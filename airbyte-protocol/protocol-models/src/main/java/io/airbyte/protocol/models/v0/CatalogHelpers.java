/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.protocol.models.v0;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.JsonSchemas;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.transform_models.FieldTransform;
import io.airbyte.protocol.models.v0.transform_models.StreamTransform;
import io.airbyte.protocol.models.v0.transform_models.UpdateFieldSchemaTransform;
import io.airbyte.protocol.models.v0.transform_models.UpdateStreamTransform;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import org.apache.commons.lang3.tuple.Pair;

/**
 * Helper class for Catalog and Stream related operations. Generally only used in tests.
 */
public class CatalogHelpers {

  private static final String ITEMS_KEY = "items";

  public static AirbyteCatalog createAirbyteCatalog(final String streamName,
                                                    final Field... fields) {
    return new AirbyteCatalog().withStreams(
        Lists.newArrayList(createAirbyteStream(streamName, fields)));
  }

  public static AirbyteStream createAirbyteStream(final String streamName, final Field... fields) {
    // Namespace is null since not all sources set it.
    return createAirbyteStream(streamName, null, Arrays.asList(fields));
  }

  public static AirbyteStream createAirbyteStream(final String streamName,
                                                  final String namespace,
                                                  final Field... fields) {
    return createAirbyteStream(streamName, namespace, Arrays.asList(fields));
  }

  public static AirbyteStream createAirbyteStream(final String streamName,
                                                  final String namespace,
                                                  final List<Field> fields) {
    return new AirbyteStream().withName(streamName).withNamespace(namespace)
        .withJsonSchema(fieldsToJsonSchema(fields))
        .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH));
  }

  public static ConfiguredAirbyteCatalog createConfiguredAirbyteCatalog(final String streamName,
                                                                        final String namespace,
                                                                        final Field... fields) {
    return new ConfiguredAirbyteCatalog().withStreams(
        Lists.newArrayList(createConfiguredAirbyteStream(streamName, namespace, fields)));
  }

  public static ConfiguredAirbyteCatalog createConfiguredAirbyteCatalog(final String streamName,
                                                                        final String namespace,
                                                                        final List<Field> fields) {
    return new ConfiguredAirbyteCatalog().withStreams(
        Lists.newArrayList(createConfiguredAirbyteStream(streamName, namespace, fields)));
  }

  public static ConfiguredAirbyteStream createConfiguredAirbyteStream(final String streamName,
                                                                      final String namespace,
                                                                      final Field... fields) {
    return createConfiguredAirbyteStream(streamName, namespace, Arrays.asList(fields));
  }

  public static ConfiguredAirbyteStream createConfiguredAirbyteStream(final String streamName,
                                                                      final String namespace,
                                                                      final List<Field> fields) {
    return new ConfiguredAirbyteStream()
        .withStream(new AirbyteStream().withName(streamName).withNamespace(namespace)
            .withJsonSchema(fieldsToJsonSchema(fields))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH)))
        .withSyncMode(SyncMode.FULL_REFRESH).withDestinationSyncMode(DestinationSyncMode.OVERWRITE);
  }

  /**
   * Converts a {@link ConfiguredAirbyteCatalog} into an {@link AirbyteCatalog}. This is possible
   * because the latter is a subset of the former.
   *
   * @param configuredCatalog - catalog to convert
   * @return - airbyte catalog
   */
  public static AirbyteCatalog configuredCatalogToCatalog(
                                                          final ConfiguredAirbyteCatalog configuredCatalog) {
    return new AirbyteCatalog().withStreams(
        configuredCatalog.getStreams()
            .stream()
            .map(ConfiguredAirbyteStream::getStream)
            .toList());
  }

  /**
   * Extracts {@link StreamDescriptor} for a given {@link AirbyteStream}
   *
   * @param airbyteStream stream
   * @return stream descriptor
   */
  public static StreamDescriptor extractDescriptor(final ConfiguredAirbyteStream airbyteStream) {
    return extractDescriptor(airbyteStream.getStream());
  }

  /**
   * Extracts {@link StreamDescriptor} for a given {@link ConfiguredAirbyteStream}
   *
   * @param airbyteStream stream
   * @return stream descriptor
   */
  public static StreamDescriptor extractDescriptor(final AirbyteStream airbyteStream) {
    return new StreamDescriptor().withName(airbyteStream.getName())
        .withNamespace(airbyteStream.getNamespace());
  }

  /**
   * Extracts {@link StreamDescriptor}s for each stream in a given {@link ConfiguredAirbyteCatalog}
   *
   * @param configuredCatalog catalog
   * @return list of stream descriptors
   */
  public static List<StreamDescriptor> extractStreamDescriptors(
                                                                final ConfiguredAirbyteCatalog configuredCatalog) {
    return extractStreamDescriptors(configuredCatalogToCatalog(configuredCatalog));
  }

  /**
   * Extracts {@link StreamDescriptor}s for each stream with an incremental {@link SyncMode} in a
   * given {@link ConfiguredAirbyteCatalog}
   *
   * @param configuredCatalog catalog
   * @return list of stream descriptors
   */
  public static List<StreamDescriptor> extractIncrementalStreamDescriptors(
                                                                           final ConfiguredAirbyteCatalog configuredCatalog) {
    return configuredCatalog.getStreams()
        .stream()
        .filter(configuredStream -> configuredStream.getSyncMode() == SyncMode.INCREMENTAL)
        .map(configuredStream -> extractDescriptor(configuredStream.getStream()))
        .toList();
  }

  /**
   * Extracts {@link StreamDescriptor}s for each stream in a given {@link AirbyteCatalog}
   *
   * @param catalog catalog
   * @return list of stream descriptors
   */
  public static List<StreamDescriptor> extractStreamDescriptors(final AirbyteCatalog catalog) {
    return catalog.getStreams()
        .stream()
        .map(CatalogHelpers::extractDescriptor)
        .toList();
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
            .toList());
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
                field -> {
                  if (isObjectWithSubFields(field)) {
                    return fieldsToJsonSchema(field.getSubFields());
                  } else {
                    return field.getType().getJsonSchemaTypeMap();
                  }
                })))
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
    final Map<String, Object> object = Jsons.object(
        stream.getStream().getJsonSchema().get("properties"), Map.class);
    return object.keySet();
  }

  /**
   * @param jsonSchema - a JSONSchema node
   * @return a set of all keys for all objects within the node
   */
  @VisibleForTesting
  protected static Set<String> getAllFieldNames(final JsonNode jsonSchema) {
    return getFullyQualifiedFieldNamesWithTypes(jsonSchema)
        .stream()
        .map(Pair::getLeft)
        // only need field name, not fully qualified name
        .map(CatalogHelpers::last)
        .flatMap(Optional::stream)
        .collect(Collectors.toSet());
  }

  /**
   * @return returns empty optional if the list is empty or if the last element in the list is null.
   */
  private static Optional<String> last(final List<String> list) {
    if (list.isEmpty()) {
      return Optional.empty();
    }
    return Optional.ofNullable(list.get(list.size() - 1));
  }

  /**
   * Extracts all fields and their schemas from a JSONSchema. This method returns values in
   * depth-first search preorder. It short circuits at oneOfs--in other words, child fields of a oneOf
   * are not returned.
   *
   * @param jsonSchema - a JSONSchema node
   * @return a list of all keys for all objects within the node. ordered in depth-first search
   *         preorder.
   */
  @VisibleForTesting
  protected static List<Pair<List<String>, JsonNode>> getFullyQualifiedFieldNamesWithTypes(
                                                                                           final JsonNode jsonSchema) {
    // if this were ever a performance issue, it could be replaced with a trie. this seems unlikely
    // however.
    final Set<List<String>> fieldNamesThatAreOneOfs = new HashSet<>();

    return JsonSchemas.traverseJsonSchemaWithCollector(jsonSchema, (node, basicPath) -> {
      final List<String> fieldName = basicPath.stream()
          .map(fieldOrList -> fieldOrList.isList() ? ITEMS_KEY : fieldOrList.getFieldName())
          .toList();
      return Pair.of(fieldName, node);
    })
        .stream()
        // first node is the original object.
        .skip(1)
        .filter(fieldWithSchema -> filterChildrenOfFoneOneOf(fieldWithSchema.getLeft(),
            fieldWithSchema.getRight(), fieldNamesThatAreOneOfs))
        .toList();
  }

  /**
   * Predicate that checks if a field is a CHILD of a oneOf field. If child of a oneOf, returns false.
   * Otherwise, true. This method as side effects. It assumes that it will be run in order on field
   * names returned in depth-first search preoorder. As it encounters oneOfs it adds them to a
   * collection. It then checks if subsequent field names are prefix matches to the field that are
   * oneOfs.
   *
   * @param fieldName - field to investigate
   * @param schema - schema of field
   * @param oneOfFieldNameAccumulator - collection of fields that are oneOfs
   * @return If child of a oneOf, returns false. Otherwise, true.
   */
  private static boolean filterChildrenOfFoneOneOf(final List<String> fieldName,
                                                   final JsonNode schema,
                                                   final Set<List<String>> oneOfFieldNameAccumulator) {
    if (isOneOfField(schema)) {
      oneOfFieldNameAccumulator.add(fieldName);
      // return early because we know it is a oneOf and therefore cannot be a child of a oneOf.
      return true;
    }

    // leverage that nodes are returned in depth-first search preorder. this means the parent field for
    // the oneOf will be present in the list BEFORE any of its children.
    for (final List<String> oneOfFieldName : oneOfFieldNameAccumulator) {
      final String oneOfFieldNameString = String.join(".", oneOfFieldName);
      final String fieldNameString = String.join(".", fieldName);

      if (fieldNameString.startsWith(oneOfFieldNameString)) {
        return false;
      }
    }
    return true;
  }

  private static boolean isOneOfField(final JsonNode schema) {
    return !MoreIterators.toSet(schema.fieldNames()).contains("type");
  }

  private static boolean isObjectWithSubFields(final Field field) {
    return field.getType().equals(JsonSchemaType.OBJECT) && field.getSubFields() != null
        && !field.getSubFields().isEmpty();
  }

  public static StreamDescriptor extractStreamDescriptor(final AirbyteStream airbyteStream) {
    return new StreamDescriptor().withName(airbyteStream.getName())
        .withNamespace(airbyteStream.getNamespace());
  }

  private static Map<StreamDescriptor, AirbyteStream> streamDescriptorToMap(
                                                                            final AirbyteCatalog catalog) {
    return catalog.getStreams()
        .stream()
        .collect(Collectors.toMap(CatalogHelpers::extractStreamDescriptor, s -> s));
  }

  /**
   * Returns difference between two provided catalogs.
   *
   * @param oldCatalog - old catalog
   * @param newCatalog - new catalog
   * @return difference between old and new catalogs
   */
  public static Set<StreamTransform> getCatalogDiff(final AirbyteCatalog oldCatalog,
                                                    final AirbyteCatalog newCatalog,
                                                    final ConfiguredAirbyteCatalog configuredCatalog) {
    final Set<StreamTransform> streamTransforms = new HashSet<>();

    final Map<StreamDescriptor, AirbyteStream> descriptorToStreamOld = streamDescriptorToMap(
        oldCatalog);
    final Map<StreamDescriptor, AirbyteStream> descriptorToStreamNew = streamDescriptorToMap(
        newCatalog);

    Sets.difference(descriptorToStreamOld.keySet(), descriptorToStreamNew.keySet())
        .forEach(descriptor -> streamTransforms.add(
            StreamTransform.createRemoveStreamTransform(descriptor)));
    Sets.difference(descriptorToStreamNew.keySet(), descriptorToStreamOld.keySet())
        .forEach(descriptor -> streamTransforms.add(
            StreamTransform.createAddStreamTransform(descriptor)));
    Sets.intersection(descriptorToStreamOld.keySet(), descriptorToStreamNew.keySet())
        .forEach(descriptor -> {
          final AirbyteStream streamOld = descriptorToStreamOld.get(descriptor);
          final AirbyteStream streamNew = descriptorToStreamNew.get(descriptor);

          final Optional<ConfiguredAirbyteStream> stream = configuredCatalog.getStreams().stream()
              .filter(s -> Objects.equals(s.getStream().getNamespace(), descriptor.getNamespace())
                  && s.getStream().getName().equals(descriptor.getName()))
              .findFirst();

          if (!streamOld.equals(streamNew)) {
            streamTransforms.add(StreamTransform.createUpdateStreamTransform(descriptor,
                getStreamDiff(streamOld, streamNew, stream)));
          }
        });

    return streamTransforms;
  }

  private static UpdateStreamTransform getStreamDiff(final AirbyteStream streamOld,
                                                     final AirbyteStream streamNew,
                                                     final Optional<ConfiguredAirbyteStream> configuredStream) {
    final Set<FieldTransform> fieldTransforms = new HashSet<>();
    final Map<List<String>, JsonNode> fieldNameToTypeOld = getFullyQualifiedFieldNamesWithTypes(
        streamOld.getJsonSchema())
            .stream()
            .collect(
                HashMap::new,
                CatalogHelpers::collectInHashMap,
                CatalogHelpers::combineAccumulator);
    final Map<List<String>, JsonNode> fieldNameToTypeNew = getFullyQualifiedFieldNamesWithTypes(
        streamNew.getJsonSchema())
            .stream()
            .collect(
                HashMap::new,
                CatalogHelpers::collectInHashMap,
                CatalogHelpers::combineAccumulator);

    Sets.difference(fieldNameToTypeOld.keySet(), fieldNameToTypeNew.keySet())
        .forEach(fieldName -> {
          fieldTransforms.add(FieldTransform.createRemoveFieldTransform(fieldName,
              fieldNameToTypeOld.get(fieldName),
              transformBreaksConnection(configuredStream, fieldName)));
        });
    Sets.difference(fieldNameToTypeNew.keySet(), fieldNameToTypeOld.keySet())
        .forEach(fieldName -> fieldTransforms.add(
            FieldTransform.createAddFieldTransform(fieldName, fieldNameToTypeNew.get(fieldName))));
    Sets.intersection(fieldNameToTypeOld.keySet(), fieldNameToTypeNew.keySet())
        .forEach(fieldName -> {
          final JsonNode oldType = fieldNameToTypeOld.get(fieldName);
          final JsonNode newType = fieldNameToTypeNew.get(fieldName);

          if (!oldType.equals(newType)) {
            fieldTransforms.add(FieldTransform.createUpdateFieldTransform(fieldName,
                new UpdateFieldSchemaTransform(oldType, newType)));
          }
        });

    return new UpdateStreamTransform(fieldTransforms);
  }

  @VisibleForTesting
  static final JsonNode DUPLICATED_SCHEMA = Jsons.jsonNode("Duplicated Schema");

  @VisibleForTesting
  static void collectInHashMap(final Map<List<String>, JsonNode> accumulator,
                               final Pair<List<String>, JsonNode> value) {
    if (accumulator.containsKey(value.getKey())) {
      accumulator.put(value.getKey(), DUPLICATED_SCHEMA);
    } else {
      accumulator.put(value.getKey(), value.getValue());
    }
  }

  @VisibleForTesting
  static void combineAccumulator(final Map<List<String>, JsonNode> accumulatorLeft,
                                 final Map<List<String>, JsonNode> accumulatorRight) {
    accumulatorRight.forEach((key, value) -> {
      if (accumulatorLeft.containsKey(key)) {
        accumulatorLeft.put(key, DUPLICATED_SCHEMA);
      } else {
        accumulatorLeft.put(key, value);
      }
    });
  }

  static boolean transformBreaksConnection(final Optional<ConfiguredAirbyteStream> configuredStream,
                                           final List<String> fieldName) {
    if (configuredStream.isEmpty()) {
      return false;
    }

    final ConfiguredAirbyteStream streamConfig = configuredStream.get();

    final SyncMode syncMode = streamConfig.getSyncMode();
    if (SyncMode.INCREMENTAL == syncMode && streamConfig.getCursorField().equals(fieldName)) {
      return true;
    }

    final DestinationSyncMode destinationSyncMode = streamConfig.getDestinationSyncMode();
    if (DestinationSyncMode.APPEND_DEDUP == destinationSyncMode && streamConfig.getPrimaryKey()
        .contains(fieldName)) {
      return true;
    }
    return false;
  }

}
