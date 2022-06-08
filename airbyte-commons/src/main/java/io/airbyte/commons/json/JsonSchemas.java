/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.json;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreIterators;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.Set;
import java.util.function.BiConsumer;
import java.util.function.BiFunction;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;

// todo (cgardens) - we need the ability to identify jsonschemas that Airbyte considers invalid for
// a connector (e.g. "not" keyword).
@Slf4j
public class JsonSchemas {

  private static final String JSON_SCHEMA_ENUM_KEY = "enum";
  private static final String JSON_SCHEMA_TYPE_KEY = "type";
  private static final String JSON_SCHEMA_PROPERTIES_KEY = "properties";
  private static final String JSON_SCHEMA_ITEMS_KEY = "items";

  // all JSONSchema types.
  private static final String ARRAY_TYPE = "array";
  private static final String OBJECT_TYPE = "object";
  private static final String STRING_TYPE = "string";
  private static final String NUMBER_TYPE = "number";
  private static final String BOOLEAN_TYPE = "boolean";
  private static final String NULL_TYPE = "null";
  private static final String ONE_OF_TYPE = "oneOf";
  private static final String ALL_OF_TYPE = "allOf";
  private static final String ANY_OF_TYPE = "anyOf";

  private static final String ARRAY_JSON_PATH = "[]";

  private static final Set<String> COMPOSITE_KEYWORDS = Set.of(ONE_OF_TYPE, ALL_OF_TYPE, ANY_OF_TYPE);

  /**
   * JsonSchema supports to ways of declaring type. `type: "string"` and `type: ["null", "string"]`.
   * This method will mutate a JsonNode with a type field so that the output type is the array
   * version.
   *
   * @param jsonNode - a json object with children that contain types.
   */
  public static void mutateTypeToArrayStandard(final JsonNode jsonNode) {
    if (jsonNode.get(JSON_SCHEMA_TYPE_KEY) != null && !jsonNode.get(JSON_SCHEMA_TYPE_KEY).isArray()) {
      final JsonNode type = jsonNode.get(JSON_SCHEMA_TYPE_KEY);
      ((ObjectNode) jsonNode).putArray(JSON_SCHEMA_TYPE_KEY).add(type);
    }
  }

  /*
   * JsonReferenceProcessor relies on all the json in consumes being in a file system (not in a jar).
   * This method copies all the json configs out of the jar into a temporary directory so that
   * JsonReferenceProcessor can find them.
   */
  public static <T> Path prepareSchemas(final String resourceDir, final Class<T> klass) {
    try {
      final List<String> filenames;
      try (final Stream<Path> resources = MoreResources.listResources(klass, resourceDir)) {
        filenames = resources.map(p -> p.getFileName().toString())
            .filter(p -> p.endsWith(".yaml"))
            .collect(Collectors.toList());
      }

      final Path configRoot = Files.createTempDirectory("schemas");
      for (final String filename : filenames) {
        IOs.writeFile(
            configRoot,
            filename,
            MoreResources.readResource(String.format("%s/%s", resourceDir, filename)));
      }

      return configRoot;
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static void traverseJsonSchema(final JsonNode jsonSchemaNode, final BiConsumer<JsonNode, String> consumer) {
    traverseJsonSchemaInternal(jsonSchemaNode, JsonPaths.empty(), consumer);
  }

  /**
   * Traverse a JsonSchema object. At each node, optionally map a value.
   *
   * @param jsonSchema - JsonSchema object to traverse
   * @param mapper - accepts the current node and the path to that node. if it returns an empty
   *        optional, nothing will be collected, otherwise, whatever is returned will be collected and
   *        returned by the final collection.
   * @param <T> - type of objects being collected
   * @return - collection of all items that were collected during the traversal. Returns a { @link
   *         Collection } because there is no order or uniqueness guarantee so neither List nor Set
   *         make sense.
   */
  public static <T> Collection<T> traverseJsonSchemaWithCollector(final JsonNode jsonSchema, final BiFunction<JsonNode, String, Optional<T>> mapper) {
    final List<T> collectors = new ArrayList<>();
    traverseJsonSchema(jsonSchema, (node, path) -> mapper.apply(node, path).ifPresent(collectors::add));
    return collectors;
  }

  /**
   * Traverses a JsonSchema object. It returns the path to each node that meet the provided condition.
   * The paths are return in JsonPath format
   *
   * @param obj - JsonSchema object to traverse
   * @param predicate - predicate to determine if the path for a node should be collected.
   * @return - collection of all paths that were collected during the traversal.
   */
  public static Set<String> collectJsonPathsThatMeetCondition(final JsonNode obj, final Predicate<JsonNode> predicate) {
    return new HashSet<>(traverseJsonSchemaWithCollector(obj, (node, path) -> {
      if (predicate.test(node)) {
        return Optional.of(path);
      } else {
        return Optional.empty();
      }
    }));
  }

  /**
   * Recursive, depth-first implementation of { @link JsonSchemas#traverseJsonSchema(final JsonNode
   * jsonNode, final BiConsumer<JsonNode, List<String>> consumer) }. Takes path as argument so that
   * the path can be passsed to the consumer.
   *
   * @param jsonSchemaNode - jsonschema object to traverse.
   * @param path - path from the first call of traverseJsonSchema to the current node.
   * @param consumer - consumer to be called at each node. it accepts the current node and the path to
   *        the node from the root of the object passed at the root level invocation
   */
  // todo (cgardens) - replace with easier to understand traversal logic from SecretsHelper.
  private static void traverseJsonSchemaInternal(final JsonNode jsonSchemaNode,
                                                 final String path,
                                                 final BiConsumer<JsonNode, String> consumer) {
    if (!jsonSchemaNode.isObject()) {
      throw new IllegalArgumentException(String.format("json schema nodes should always be object nodes. path: %s actual: %s", path, jsonSchemaNode));
    }

    consumer.accept(jsonSchemaNode, path);
    // if type is missing assume object. not official JsonSchema, but it seems to be a common
    // compromise.
    final List<String> nodeTypes = getTypeOrObject(jsonSchemaNode);

    for (final String nodeType : nodeTypes) {
      switch (nodeType) {
        // case BOOLEAN_TYPE, NUMBER_TYPE, STRING_TYPE, NULL_TYPE -> do nothing after consumer.accept above.
        case ARRAY_TYPE -> {
          final String newPath = JsonPaths.appendAppendListSplat(path);
          // hit every node.
          // log.error("array: " + jsonSchemaNode);
          traverseJsonSchemaInternal(jsonSchemaNode.get(JSON_SCHEMA_ITEMS_KEY), newPath, consumer);
        }
        case OBJECT_TYPE -> {
          final Optional<String> comboKeyWordOptional = getKeywordIfComposite(jsonSchemaNode);
          if (jsonSchemaNode.has(JSON_SCHEMA_PROPERTIES_KEY)) {
            for (final Iterator<Entry<String, JsonNode>> it = jsonSchemaNode.get(JSON_SCHEMA_PROPERTIES_KEY).fields(); it.hasNext();) {
              final Entry<String, JsonNode> child = it.next();
              final String newPath = JsonPaths.appendField(path, child.getKey());
              // log.error("obj1: " + jsonSchemaNode);
              traverseJsonSchemaInternal(child.getValue(), newPath, consumer);
            }
          } else if (comboKeyWordOptional.isPresent()) {
            for (final JsonNode arrayItem : jsonSchemaNode.get(comboKeyWordOptional.get())) {
              // log.error("obj2: " + jsonSchemaNode);
              traverseJsonSchemaInternal(arrayItem, path, consumer);
            }
          } else {
            throw new IllegalArgumentException(
                "malformed JsonSchema object type, must have one of the following fields: properties, oneOf, allOf, anyOf in " + jsonSchemaNode);
          }
        }
      }
    }
  }

  /**
   * If the object uses JSONSchema composite functionality (e.g. oneOf, anyOf, allOf), detect it and
   * return which one it is using.
   *
   * @param node - object to detect use of composite functionality.
   * @return the composite functionality being used, if not using composite functionality, empty.
   */
  private static Optional<String> getKeywordIfComposite(final JsonNode node) {
    for (final String keyWord : COMPOSITE_KEYWORDS) {
      if (node.has(keyWord)) {
        return Optional.ofNullable(keyWord);
      }
    }
    return Optional.empty();
  }

  public static List<String> getTypeOrObject(final JsonNode jsonNode) {
    final List<String> types = getType(jsonNode);
    if (types.isEmpty()) {
      return List.of(OBJECT_TYPE);
    } else {
      return types;
    }
  }

  public static List<String> getType(final JsonNode jsonNode) {
    if (jsonNode.has(JSON_SCHEMA_TYPE_KEY)) {
      if (jsonNode.get(JSON_SCHEMA_TYPE_KEY).isArray()) {
        return MoreIterators.toList(jsonNode.get(JSON_SCHEMA_TYPE_KEY).iterator())
            .stream()
            .map(JsonNode::asText)
            .collect(Collectors.toList());
      } else {
        return List.of(jsonNode.get(JSON_SCHEMA_TYPE_KEY).asText());
      }
    }
    if (jsonNode.has(JSON_SCHEMA_ENUM_KEY)) {
      return List.of(STRING_TYPE);
    }
    return Collections.emptyList();
  }

}
