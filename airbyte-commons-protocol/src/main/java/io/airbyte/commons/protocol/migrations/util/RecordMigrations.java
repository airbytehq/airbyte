/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations.util;

import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.ARRAY_TYPE;
import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.ITEMS_KEY;
import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.OBJECT_TYPE;
import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.ONEOF_KEY;
import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.PROPERTIES_KEY;
import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.REF_KEY;
import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.TYPE_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.util.Iterator;
import java.util.Map.Entry;
import java.util.function.BiFunction;
import java.util.function.Function;

public class RecordMigrations {

  /**
   * Quick and dirty tuple. Used internally by
   * {@link #mutateDataNode(JsonSchemaValidator, Function, Transformer, JsonNode, JsonNode)}; callers
   * probably only actually need the node.
   *
   * matchedSchema is useful for mutating using a oneOf schema, where we need to recognize the correct
   * subschema.
   *
   * @param node Our attempt at mutating the node, under the given schema
   * @param matchedSchema Whether the original node actually matched the schema
   */
  public record MigratedNode(JsonNode node, boolean matchedSchema) {}

  /**
   * Extend BiFunction so that we can have named parameters.
   */
  @FunctionalInterface
  public interface Transformer extends BiFunction<JsonNode, JsonNode, MigratedNode> {

    @Override
    MigratedNode apply(JsonNode schema, JsonNode data);

  }

  /**
   * Works on a best-effort basis. If the schema doesn't match the data, we'll do our best to mutate
   * anything that we can definitively say matches the criteria. Should _not_ throw an exception if
   * bad things happen (e.g. we try to parse a non-numerical string as a number).
   *
   * @param schemaMatcher Accepts a JsonNode schema and returns whether its corresponding entry in the
   *        data should be mutated. Doesn't need to handle oneOf cases, i.e. should only care about
   *        type/$ref.
   * @param transformer Performs the modification on the given data node. Should not throw exceptions.
   */
  public static MigratedNode mutateDataNode(
                                            final JsonSchemaValidator validator,
                                            final Function<JsonNode, Boolean> schemaMatcher,
                                            final Transformer transformer,
                                            final JsonNode data,
                                            final JsonNode schema) {
    // If this is a oneOf node, then we need to handle each oneOf case.
    if (!schema.hasNonNull(REF_KEY) && !schema.hasNonNull(TYPE_KEY) && schema.hasNonNull(ONEOF_KEY)) {
      return mutateOneOfNode(validator, schemaMatcher, transformer, data, schema);
    }

    // If we should mutate the data, then mutate it appropriately
    if (schemaMatcher.apply(schema)) {
      return transformer.apply(schema, data);
    }

    // Otherwise, we need to recurse into non-primitive nodes.
    if (data.isObject()) {
      return mutateObjectNode(validator, schemaMatcher, transformer, data, schema);
    } else if (data.isArray()) {
      return mutateArrayNode(validator, schemaMatcher, transformer, data, schema);
    } else {
      // There's nothing to do in the case of a primitive node.
      // So we just check whether the schema is correct and return the node as-is.
      return new MigratedNode(data, validator.test(schema, data));
    }
  }

  /**
   * Attempt to mutate using each oneOf option in sequence. Returns the result from mutating using the
   * first subschema that matches the data, or if none match, then the result of using the first
   * subschema.
   */
  private static MigratedNode mutateOneOfNode(
                                              final JsonSchemaValidator validator,
                                              final Function<JsonNode, Boolean> schemaMatcher,
                                              final Transformer transformer,
                                              final JsonNode data,
                                              final JsonNode schema) {
    final JsonNode schemaOptions = schema.get(ONEOF_KEY);
    if (schemaOptions.size() == 0) {
      // If the oneOf has no options, then don't do anything interesting.
      return new MigratedNode(data, validator.test(schema, data));
    }

    // Attempt to mutate the node against each oneOf schema.
    // Return the first schema that matches the data, or the first schema if none matched successfully.
    MigratedNode migratedNode = null;
    for (final JsonNode maybeSchema : schemaOptions) {
      final MigratedNode maybeMigratedNode = mutateDataNode(validator, schemaMatcher, transformer, data, maybeSchema);
      if (maybeMigratedNode.matchedSchema()) {
        // If we've found a matching schema, then return immediately
        return maybeMigratedNode;
      } else if (migratedNode == null) {
        // Otherwise - if this is the first subschema, then just take it
        migratedNode = maybeMigratedNode;
      }
    }
    // None of the schemas matched, so just return whatever we found first
    return migratedNode;
  }

  /**
   * If data is an object, then we need to recursively mutate all of its fields.
   */
  private static MigratedNode mutateObjectNode(
                                               final JsonSchemaValidator validator,
                                               final Function<JsonNode, Boolean> schemaMatcher,
                                               final Transformer transformer,
                                               final JsonNode data,
                                               final JsonNode schema) {
    boolean isObjectSchema;
    // First, check whether the schema is supposed to be an object at all.
    if (schema.hasNonNull(REF_KEY)) {
      // If the schema uses a reference type, then it's not an object schema.
      isObjectSchema = false;
    } else if (schema.hasNonNull(TYPE_KEY)) {
      // If the schema declares {type: object} or {type: [..., object, ...]}
      // Then this is an object schema
      final JsonNode typeNode = schema.get(TYPE_KEY);
      if (typeNode.isArray()) {
        isObjectSchema = false;
        for (final JsonNode typeItem : typeNode) {
          if (OBJECT_TYPE.equals(typeItem.asText())) {
            isObjectSchema = true;
          }
        }
      } else {
        isObjectSchema = OBJECT_TYPE.equals(typeNode.asText());
      }
    } else {
      // If the schema doesn't declare a type at all (which is bad practice, but let's handle it anyway)
      // Then check for a properties entry, and assume that this is an object if it's present
      isObjectSchema = schema.hasNonNull(PROPERTIES_KEY);
    }

    if (!isObjectSchema) {
      // If it's not supposed to be an object, then we can't do anything here.
      // Return the data without modification.
      return new MigratedNode(data, false);
    } else {
      // If the schema _is_ for an object, then recurse into each field
      final ObjectNode mutatedData = (ObjectNode) Jsons.emptyObject();
      final JsonNode propertiesNode = schema.get(PROPERTIES_KEY);

      final Iterator<Entry<String, JsonNode>> dataFields = data.fields();
      boolean matchedSchema = true;
      while (dataFields.hasNext()) {
        final Entry<String, JsonNode> field = dataFields.next();
        final String key = field.getKey();
        final JsonNode value = field.getValue();
        if (propertiesNode != null && propertiesNode.hasNonNull(key)) {
          // If we have a schema for this property, mutate the value
          final JsonNode subschema = propertiesNode.get(key);
          final MigratedNode migratedNode = mutateDataNode(validator, schemaMatcher, transformer, value, subschema);
          mutatedData.set(key, migratedNode.node);
          if (!migratedNode.matchedSchema) {
            matchedSchema = false;
          }
        } else {
          // Else it's an additional property - we _could_ check additionalProperties,
          // but that's annoying. We don't actually respect that in destinations/normalization anyway.
          mutatedData.set(key, value);
        }
      }

      return new MigratedNode(mutatedData, matchedSchema);
    }
  }

  /**
   * Much like objects, arrays must be recursively mutated.
   */
  private static MigratedNode mutateArrayNode(
                                              final JsonSchemaValidator validator,
                                              final Function<JsonNode, Boolean> schemaMatcher,
                                              final Transformer transformer,
                                              final JsonNode data,
                                              final JsonNode schema) {
    // Similar to objects, we first check whether this is even supposed to be an array.
    boolean isArraySchema;
    if (schema.hasNonNull(REF_KEY)) {
      // If the schema uses a reference type, then it's not an array schema.
      isArraySchema = false;
    } else if (schema.hasNonNull(TYPE_KEY)) {
      // If the schema declares {type: array} or {type: [..., array, ...]}
      // Then this is an array schema
      final JsonNode typeNode = schema.get(TYPE_KEY);
      if (typeNode.isArray()) {
        isArraySchema = false;
        for (final JsonNode typeItem : typeNode) {
          if (ARRAY_TYPE.equals(typeItem.asText())) {
            isArraySchema = true;
          }
        }
      } else {
        isArraySchema = ARRAY_TYPE.equals(typeNode.asText());
      }
    } else {
      // If the schema doesn't declare a type at all (which is bad practice, but let's handle it anyway)
      // Then check for an items entry, and assume that this is an array if it's present
      isArraySchema = schema.hasNonNull(ITEMS_KEY);
    }

    if (!isArraySchema) {
      return new MigratedNode(data, false);
    } else {
      final ArrayNode mutatedItems = Jsons.arrayNode();
      final JsonNode itemsNode = schema.get(ITEMS_KEY);
      if (itemsNode == null) {
        // We _could_ check additionalItems, but much like the additionalProperties comment for objects:
        // it's a lot of work for no payoff
        return new MigratedNode(data, true);
      } else if (itemsNode.isArray()) {
        // In the case of {items: [schema1, schema2, ...]}
        // We need to check schema1 against the first element of the array,
        // schema2 against the second element, etc.
        boolean allSchemasMatched = true;
        for (int i = 0; i < data.size(); i++) {
          final JsonNode element = data.get(i);
          if (itemsNode.size() > i) {
            // If we have a schema for this element, then try mutating the element
            final MigratedNode mutatedElement = mutateDataNode(validator, schemaMatcher, transformer, element, itemsNode.get(i));
            if (!mutatedElement.matchedSchema()) {
              allSchemasMatched = false;
            }
            mutatedItems.add(mutatedElement.node());
          }
        }
        // If there were more elements in `data` than there were schemas in `itemsNode`,
        // then just blindly add the rest of those elements.
        for (int i = itemsNode.size(); i < data.size(); i++) {
          mutatedItems.add(data.get(i));
        }
        return new MigratedNode(mutatedItems, allSchemasMatched);
      } else {
        // IN the case of {items: schema}, we just check every array element against that schema.
        boolean matchedSchema = true;
        for (final JsonNode item : data) {
          final MigratedNode migratedNode = mutateDataNode(validator, schemaMatcher, transformer, item, itemsNode);
          mutatedItems.add(migratedNode.node);
          if (!migratedNode.matchedSchema) {
            matchedSchema = false;
          }
        }
        return new MigratedNode(mutatedItems, matchedSchema);
      }
    }
  }

}
