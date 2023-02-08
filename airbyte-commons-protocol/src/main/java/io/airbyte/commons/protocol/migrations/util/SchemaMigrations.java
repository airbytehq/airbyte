/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations.util;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map.Entry;
import java.util.function.Consumer;
import java.util.function.Function;

/**
 * Utility class for recursively modifying JsonSchemas. Useful for up/downgrading AirbyteCatalog
 * objects.
 *
 * See {@link io.airbyte.commons.protocol.migrations.v1.SchemaMigrationV1} for example usage.
 */
public class SchemaMigrations {

  /**
   * Generic utility method that recurses through all type declarations in the schema. For each type
   * declaration that are accepted by matcher, mutate them using transformer. For all other type
   * declarations, recurse into their subschemas (if any).
   * <p>
   * Note that this modifies the schema in-place. Callers who need a copy of the old schema should
   * save schema.deepCopy() before calling this method.
   *
   * @param schema The JsonSchema node to walk down
   * @param matcher A function which returns true on any schema node that needs to be transformed
   * @param transformer A function which mutates a schema node
   */
  public static void mutateSchemas(final Function<JsonNode, Boolean> matcher, final Consumer<JsonNode> transformer, final JsonNode schema) {
    if (schema.isBoolean()) {
      // We never want to modify a schema of `true` or `false` (e.g. additionalProperties: true)
      // so just return immediately
      return;
    }
    if (matcher.apply(schema)) {
      // Base case: If this schema should be mutated, then we need to mutate it
      transformer.accept(schema);
    } else {
      // Otherwise, we need to find all the subschemas and mutate them.
      // technically, it might be more correct to do something like:
      // if schema["type"] == "array": find subschemas for items, additionalItems, contains
      // else if schema["type"] == "object": find subschemas for properties, patternProperties,
      // additionalProperties
      // else if oneof, allof, etc
      // but that sounds really verbose for no real benefit
      final List<JsonNode> subschemas = findSubschemas(schema);

      // recurse into each subschema
      for (final JsonNode subschema : subschemas) {
        mutateSchemas(matcher, transformer, subschema);
      }
    }
  }

  /**
   * Returns a list of all the direct children nodes to consider for subSchemas
   *
   * @param schema The JsonSchema node to start
   * @return a list of the JsonNodes to be considered
   */
  public static List<JsonNode> findSubschemas(final JsonNode schema) {
    final List<JsonNode> subschemas = new ArrayList<>();

    // array schemas
    findSubschemas(subschemas, schema, "items");
    findSubschemas(subschemas, schema, "additionalItems");
    findSubschemas(subschemas, schema, "contains");

    // object schemas
    if (schema.hasNonNull("properties")) {
      final ObjectNode propertiesNode = (ObjectNode) schema.get("properties");
      final Iterator<Entry<String, JsonNode>> propertiesIterator = propertiesNode.fields();
      while (propertiesIterator.hasNext()) {
        final Entry<String, JsonNode> property = propertiesIterator.next();
        subschemas.add(property.getValue());
      }
    }
    if (schema.hasNonNull("patternProperties")) {
      final ObjectNode propertiesNode = (ObjectNode) schema.get("patternProperties");
      final Iterator<Entry<String, JsonNode>> propertiesIterator = propertiesNode.fields();
      while (propertiesIterator.hasNext()) {
        final Entry<String, JsonNode> property = propertiesIterator.next();
        subschemas.add(property.getValue());
      }
    }
    findSubschemas(subschemas, schema, "additionalProperties");

    // combining restrictions - destinations have limited support for these, but we should handle the
    // schemas correctly anyway
    findSubschemas(subschemas, schema, "allOf");
    findSubschemas(subschemas, schema, "oneOf");
    findSubschemas(subschemas, schema, "anyOf");
    findSubschemas(subschemas, schema, "not");

    return subschemas;
  }

  /**
   * If schema contains key, then grab the subschema(s) at schema[key] and add them to the subschemas
   * list.
   * <p>
   * For example:
   * <ul>
   * <li>schema = {"items": [{"type": "string}]}
   * <p>
   * key = "items"
   * <p>
   * -> add {"type": "string"} to subschemas</li>
   * <li>schema = {"items": {"type": "string"}}
   * <p>
   * key = "items"
   * <p>
   * -> add {"type": "string"} to subschemas</li>
   * <li>schema = {"additionalProperties": true}
   * <p>
   * key = "additionalProperties"
   * <p>
   * -> add nothing to subschemas
   * <p>
   * (technically `true` is a valid JsonSchema, but we don't want to modify it)</li>
   * </ul>
   */
  public static void findSubschemas(final List<JsonNode> subschemas, final JsonNode schema, final String key) {
    if (schema.hasNonNull(key)) {
      final JsonNode subschemaNode = schema.get(key);
      if (subschemaNode.isArray()) {
        for (final JsonNode subschema : subschemaNode) {
          subschemas.add(subschema);
        }
      } else if (subschemaNode.isObject()) {
        subschemas.add(subschemaNode);
      }
    }
  }

}
