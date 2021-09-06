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

package io.airbyte.commons.json;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.core.util.DefaultPrettyPrinter;
import com.fasterxml.jackson.core.util.Separators;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.base.Charsets;
import com.google.common.base.Preconditions;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.stream.MoreStreams;
import java.io.IOException;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.function.BiConsumer;
import java.util.stream.Collectors;

public class Jsons {

  // Object Mapper is thread-safe
  private static final ObjectMapper OBJECT_MAPPER = MoreMappers.initMapper();
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
    } catch (final IOException e) {
      return Optional.empty();
    }
  }

  public static Optional<JsonNode> tryDeserialize(final String jsonString) {
    try {
      return Optional.of(OBJECT_MAPPER.readTree(jsonString));
    } catch (final IOException e) {
      return Optional.empty();
    }
  }

  public static <T> JsonNode jsonNode(final T object) {
    return OBJECT_MAPPER.valueToTree(object);
  }

  public static JsonNode emptyObject() {
    return jsonNode(Collections.emptyMap());
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

  public static void replaceNestedString(final JsonNode json, final List<String> keys, final String replacement) {
    replaceNested(json, keys, (node, finalKey) -> node.put(finalKey, replacement));
  }

  public static void replaceNestedInt(final JsonNode json, final List<String> keys, final int replacement) {
    replaceNested(json, keys, (node, finalKey) -> node.put(finalKey, replacement));
  }

  private static void replaceNested(final JsonNode json, final List<String> keys, final BiConsumer<ObjectNode, String> typedReplacement) {
    Preconditions.checkArgument(keys.size() > 0, "Must pass at least one key");
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
