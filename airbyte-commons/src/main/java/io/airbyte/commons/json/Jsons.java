/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.json;

import static java.util.Collections.singletonMap;
import static java.util.stream.Collectors.toMap;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.core.util.DefaultPrettyPrinter;
import com.fasterxml.jackson.core.util.Separators;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import com.google.common.base.Charsets;
import com.google.common.base.Preconditions;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.stream.MoreStreams;
import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.Set;
import java.util.function.BiConsumer;
import java.util.stream.Collectors;

@SuppressWarnings({"PMD.AvoidReassigningParameters", "PMD.AvoidCatchingThrowable"})
public class Jsons {

  // Object Mapper is thread-safe
  private static final ObjectMapper OBJECT_MAPPER = MoreMappers.initMapper();

  private static final ObjectMapper YAML_OBJECT_MAPPER = MoreMappers.initYamlMapper(new YAMLFactory());
  private static final ObjectWriter OBJECT_WRITER = OBJECT_MAPPER.writer(new JsonPrettyPrinter());

  public static <T> String serialize(final T object) {
    try {
      return OBJECT_MAPPER.writeValueAsString(object);
    } catch (final JsonProcessingException e) {
      throw new RuntimeException(e);
    }
  }

  public static <T> T deserialize(final String jsonString, final Class<T> klass) {
    try {
      return OBJECT_MAPPER.readValue(jsonString, klass);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static <T> T deserialize(final String jsonString, final TypeReference<T> valueTypeRef) {
    try {
      return OBJECT_MAPPER.readValue(jsonString, valueTypeRef);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static <T> T deserialize(final File file, final Class<T> klass) {
    try {
      return OBJECT_MAPPER.readValue(file, klass);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static <T> T deserialize(final File file, final TypeReference<T> valueTypeRef) {
    try {
      return OBJECT_MAPPER.readValue(file, valueTypeRef);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static <T> T convertValue(final Object object, final Class<T> klass) {
    return OBJECT_MAPPER.convertValue(object, klass);
  }

  public static JsonNode deserialize(final String jsonString) {
    try {
      return OBJECT_MAPPER.readTree(jsonString);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static <T> Optional<T> tryDeserialize(final String jsonString, final Class<T> klass) {
    try {
      return Optional.of(OBJECT_MAPPER.readValue(jsonString, klass));
    } catch (final Throwable e) {
      return Optional.empty();
    }
  }

  public static Optional<JsonNode> tryDeserialize(final String jsonString) {
    try {
      return Optional.of(OBJECT_MAPPER.readTree(jsonString));
    } catch (final Throwable e) {
      return Optional.empty();
    }
  }

  public static <T> JsonNode jsonNode(final T object) {
    return OBJECT_MAPPER.valueToTree(object);
  }

  public static JsonNode jsonNodeFromFile(final File file) throws IOException {
    return YAML_OBJECT_MAPPER.readTree(file);
  }

  public static JsonNode emptyObject() {
    return jsonNode(Collections.emptyMap());
  }

  public static ArrayNode arrayNode() {
    return OBJECT_MAPPER.createArrayNode();
  }

  public static <T> T object(final JsonNode jsonNode, final Class<T> klass) {
    return OBJECT_MAPPER.convertValue(jsonNode, klass);
  }

  public static <T> T object(final JsonNode jsonNode, final TypeReference<T> typeReference) {
    return OBJECT_MAPPER.convertValue(jsonNode, typeReference);
  }

  public static <T> Optional<T> tryObject(final JsonNode jsonNode, final Class<T> klass) {
    try {
      return Optional.of(OBJECT_MAPPER.convertValue(jsonNode, klass));
    } catch (final Exception e) {
      return Optional.empty();
    }
  }

  public static <T> Optional<T> tryObject(final JsonNode jsonNode, final TypeReference<T> typeReference) {
    try {
      return Optional.of(OBJECT_MAPPER.convertValue(jsonNode, typeReference));
    } catch (final Exception e) {
      return Optional.empty();
    }
  }

  @SuppressWarnings("unchecked")
  public static <T> T clone(final T object) {
    return (T) deserialize(serialize(object), object.getClass());
  }

  public static byte[] toBytes(final JsonNode jsonNode) {
    return serialize(jsonNode).getBytes(Charsets.UTF_8);
  }

  /**
   * Use string length as an estimation for byte size, because all ASCII characters are one byte long
   * in UTF-8, and ASCII characters cover most of the use cases. To be more precise, we can convert
   * the string to byte[] and use the length of the byte[]. However, this conversion is expensive in
   * memory consumption. Given that the byte size of the serialized JSON is already an estimation of
   * the actual size of the JSON object, using a cheap operation seems an acceptable compromise.
   */
  public static int getEstimatedByteSize(final JsonNode jsonNode) {
    return serialize(jsonNode).length();
  }

  public static Set<String> keys(final JsonNode jsonNode) {
    if (jsonNode.isObject()) {
      return Jsons.object(jsonNode, new TypeReference<Map<String, Object>>() {}).keySet();
    } else {
      return new HashSet<>();
    }
  }

  public static List<JsonNode> children(final JsonNode jsonNode) {
    return MoreStreams.toStream(jsonNode.elements()).collect(Collectors.toList());
  }

  public static String toPrettyString(final JsonNode jsonNode) {
    try {
      return OBJECT_WRITER.writeValueAsString(jsonNode) + "\n";
    } catch (final JsonProcessingException e) {
      throw new RuntimeException(e);
    }
  }

  public static JsonNode navigateTo(JsonNode node, final List<String> keys) {
    for (final String key : keys) {
      node = node.get(key);
    }
    return node;
  }

  public static void replaceNestedValue(final JsonNode json, final List<String> keys, final JsonNode replacement) {
    replaceNested(json, keys, (node, finalKey) -> node.put(finalKey, replacement));
  }

  public static void replaceNestedString(final JsonNode json, final List<String> keys, final String replacement) {
    replaceNested(json, keys, (node, finalKey) -> node.put(finalKey, replacement));
  }

  public static void replaceNestedInt(final JsonNode json, final List<String> keys, final int replacement) {
    replaceNested(json, keys, (node, finalKey) -> node.put(finalKey, replacement));
  }

  private static void replaceNested(final JsonNode json, final List<String> keys, final BiConsumer<ObjectNode, String> typedReplacement) {
    Preconditions.checkArgument(!keys.isEmpty(), "Must pass at least one key");
    final JsonNode nodeContainingFinalKey = navigateTo(json, keys.subList(0, keys.size() - 1));
    typedReplacement.accept((ObjectNode) nodeContainingFinalKey, keys.get(keys.size() - 1));
  }

  public static Optional<JsonNode> getOptional(final JsonNode json, final String... keys) {
    return getOptional(json, Arrays.asList(keys));
  }

  public static Optional<JsonNode> getOptional(JsonNode json, final List<String> keys) {
    for (final String key : keys) {
      if (json == null) {
        return Optional.empty();
      }

      json = json.get(key);
    }

    return Optional.ofNullable(json);
  }

  public static String getStringOrNull(final JsonNode json, final String... keys) {
    return getStringOrNull(json, Arrays.asList(keys));
  }

  public static String getStringOrNull(final JsonNode json, final List<String> keys) {
    final Optional<JsonNode> optional = getOptional(json, keys);
    return optional.map(JsonNode::asText).orElse(null);
  }

  public static int getIntOrZero(final JsonNode json, final String... keys) {
    return getIntOrZero(json, Arrays.asList(keys));
  }

  public static int getIntOrZero(final JsonNode json, final List<String> keys) {
    final Optional<JsonNode> optional = getOptional(json, keys);
    return optional.map(JsonNode::asInt).orElse(0);
  }

  /**
   * Flattens an ObjectNode, or dumps it into a {null: value} map if it's not an object. When
   * applyFlattenToArray is true, each element in the array will be one entry in the returned map.
   * This behavior is used in the Redshift SUPER type. When it is false, the whole array will be one
   * entry. This is used in the JobTracker.
   */
  @SuppressWarnings("PMD.ForLoopCanBeForeach")
  public static Map<String, Object> flatten(final JsonNode node, final Boolean applyFlattenToArray) {
    if (node.isObject()) {
      final Map<String, Object> output = new HashMap<>();
      for (final Iterator<Entry<String, JsonNode>> it = node.fields(); it.hasNext();) {
        final Entry<String, JsonNode> entry = it.next();
        final String field = entry.getKey();
        final JsonNode value = entry.getValue();
        mergeMaps(output, field, flatten(value, applyFlattenToArray));
      }
      return output;
    } else if (node.isArray() && applyFlattenToArray) {
      final Map<String, Object> output = new HashMap<>();
      final int arrayLen = node.size();
      for (int i = 0; i < arrayLen; i++) {
        final String field = String.format("[%d]", i);
        final JsonNode value = node.get(i);
        mergeMaps(output, field, flatten(value, applyFlattenToArray));
      }
      return output;
    } else {
      final Object value;
      if (node.isBoolean()) {
        value = node.asBoolean();
      } else if (node.isLong()) {
        value = node.asLong();
      } else if (node.isInt()) {
        value = node.asInt();
      } else if (node.isDouble()) {
        value = node.asDouble();
      } else if (node.isValueNode() && !node.isNull()) {
        value = node.asText();
      } else {
        // Fallback handling for e.g. arrays
        value = node.toString();
      }
      return singletonMap(null, value);
    }
  }

  /**
   * Flattens an ObjectNode, or dumps it into a {null: value} map if it's not an object. New usage of
   * this function is best to explicitly declare the intended array mode. This version is provided for
   * backward compatibility.
   */
  public static Map<String, Object> flatten(final JsonNode node) {
    return flatten(node, false);
  }

  /**
   * Prepend all keys in subMap with prefix, then merge that map into originalMap.
   * <p>
   * If subMap contains a null key, then instead it is replaced with prefix. I.e. {null: value} is
   * treated as {prefix: value} when merging into originalMap.
   */
  public static void mergeMaps(final Map<String, Object> originalMap, final String prefix, final Map<String, Object> subMap) {
    originalMap.putAll(subMap.entrySet().stream().collect(toMap(
        e -> {
          final String key = e.getKey();
          if (key != null) {
            return prefix + "." + key;
          } else {
            return prefix;
          }
        },
        Entry::getValue)));
  }

  public static Map<String, String> deserializeToStringMap(JsonNode json) {
    return OBJECT_MAPPER.convertValue(json, new TypeReference<>() {});
  }

  /**
   * By the Jackson DefaultPrettyPrinter prints objects with an extra space as follows: {"name" :
   * "airbyte"}. We prefer {"name": "airbyte"}.
   */
  private static class JsonPrettyPrinter extends DefaultPrettyPrinter {

    // this method has to be overridden because in the superclass it checks that it is an instance of
    // DefaultPrettyPrinter (which is no longer the case in this inherited class).
    @Override
    public DefaultPrettyPrinter createInstance() {
      return new DefaultPrettyPrinter(this);
    }

    // override the method that inserts the extra space.
    @Override
    public DefaultPrettyPrinter withSeparators(final Separators separators) {
      _separators = separators;
      _objectFieldValueSeparatorWithSpaces = separators.getObjectFieldValueSeparator() + " ";
      return this;
    }

  }

}
