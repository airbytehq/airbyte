/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations.v1;

import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.ONEOF_KEY;
import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.REF_KEY;
import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.TYPE_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.protocol.migrations.util.SchemaMigrations;
import io.airbyte.protocol.models.JsonSchemaReferenceTypes;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map.Entry;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.StreamSupport;

public class SchemaMigrationV1 {

  /**
   * Perform the {type: foo} -> {$ref: foo} upgrade. Modifies the schema in-place.
   */
  public static void upgradeSchema(final JsonNode schema) {
    SchemaMigrations.mutateSchemas(
        SchemaMigrationV1::isPrimitiveTypeDeclaration,
        SchemaMigrationV1::upgradeTypeDeclaration,
        schema);
  }

  /**
   * Perform the {$ref: foo} -> {type: foo} downgrade. Modifies the schema in-place.
   */
  public static void downgradeSchema(final JsonNode schema) {
    SchemaMigrations.mutateSchemas(
        SchemaMigrationV1::isPrimitiveReferenceTypeDeclaration,
        SchemaMigrationV1::downgradeTypeDeclaration,
        schema);
  }

  /**
   * Detects any schema that looks like a primitive type declaration, e.g.: { "type": "string" } or {
   * "type": ["string", "object"] }
   */
  static boolean isPrimitiveTypeDeclaration(final JsonNode schema) {
    if (!schema.isObject() || !schema.hasNonNull(TYPE_KEY)) {
      return false;
    }
    final JsonNode typeNode = schema.get(TYPE_KEY);
    if (typeNode.isArray()) {
      return StreamSupport.stream(typeNode.spliterator(), false)
          .anyMatch(n -> JsonSchemaReferenceTypes.PRIMITIVE_JSON_TYPES.contains(n.asText()));
    } else {
      return JsonSchemaReferenceTypes.PRIMITIVE_JSON_TYPES.contains(typeNode.asText());
    }
  }

  /**
   * Detects any schema that looks like a reference type declaration, e.g.: { "$ref":
   * "WellKnownTypes.json...." } or { "oneOf": [{"$ref": "..."}, {"type": "object"}] }
   */
  private static boolean isPrimitiveReferenceTypeDeclaration(final JsonNode schema) {
    if (!schema.isObject()) {
      // Non-object schemas (i.e. true/false) never need to be modified
      return false;
    } else if (schema.hasNonNull(REF_KEY) && schema.get(REF_KEY).asText().startsWith("WellKnownTypes.json")) {
      // If this schema has a $ref, then we need to convert it back to type/airbyte_type/format
      return true;
    } else if (schema.hasNonNull(ONEOF_KEY)) {
      // If this is a oneOf with at least one primitive $ref option, then we should consider converting it
      // back
      final List<JsonNode> subschemas = getSubschemas(schema, ONEOF_KEY);
      return subschemas.stream().anyMatch(
          subschema -> subschema.hasNonNull(REF_KEY)
              && subschema.get(REF_KEY).asText().startsWith("WellKnownTypes.json"));
    } else {
      return false;
    }
  }

  /**
   * Modifies the schema in-place to upgrade from the old-style type declaration to the new-style $ref
   * declaration. Assumes that the schema is an ObjectNode containing a primitive declaration, i.e.
   * either something like: {"type": "string"} or: {"type": ["string", "object"]}
   * <p>
   * In the latter case, the schema may contain subschemas. This method mutually recurses with
   * {@link SchemaMigrations#mutateSchemas(Function, Consumer, JsonNode)} to upgrade those subschemas.
   *
   * @param schema An ObjectNode representing a primitive type declaration
   */
  private static void upgradeTypeDeclaration(final JsonNode schema) {
    final ObjectNode schemaNode = (ObjectNode) schema;

    if (schemaNode.hasNonNull("airbyte_type")) {
      // If airbyte_type is defined, always respect it
      final String referenceType = JsonSchemaReferenceTypes.LEGACY_AIRBYTE_PROPERY_TO_REFERENCE.get(schemaNode.get("airbyte_type").asText());
      schemaNode.removeAll();
      schemaNode.put(REF_KEY, referenceType);
    } else {
      // Otherwise, fall back to type/format
      final JsonNode typeNode = schemaNode.get(TYPE_KEY);
      if (typeNode.isTextual()) {
        // If the type is a single string, then replace this node with the appropriate reference type
        final String type = typeNode.asText();
        final String referenceType = getReferenceType(type, schemaNode);
        schemaNode.removeAll();
        schemaNode.put(REF_KEY, referenceType);
      } else {
        // If type is an array of strings, then things are more complicated
        final List<String> types = StreamSupport.stream(typeNode.spliterator(), false)
            .map(JsonNode::asText)
            // Everything is implicitly nullable by just not declaring the `required `field
            // so filter out any explicit null types
            .filter(type -> !"null".equals(type))
            .toList();
        final boolean exactlyOneType = types.size() == 1;
        if (exactlyOneType) {
          // If there's only one type, e.g. {type: [string]}, just treat that as equivalent to {type: string}
          final String type = types.get(0);
          final String referenceType = getReferenceType(type, schemaNode);
          schemaNode.removeAll();
          schemaNode.put(REF_KEY, referenceType);
        } else {
          // If there are multiple types, we'll need to convert this to a oneOf.
          // For arrays and objects, we do a mutual recursion back into mutateSchemas to upgrade their
          // subschemas.
          final ArrayNode oneOfOptions = Jsons.arrayNode();
          for (final String type : types) {
            final ObjectNode option = (ObjectNode) Jsons.emptyObject();
            switch (type) {
              case "array" -> {
                option.put(TYPE_KEY, "array");
                copyKey(schemaNode, option, "items");
                copyKey(schemaNode, option, "additionalItems");
                copyKey(schemaNode, option, "contains");
                upgradeSchema(option);
              }
              case "object" -> {
                option.put(TYPE_KEY, "object");
                copyKey(schemaNode, option, "properties");
                copyKey(schemaNode, option, "patternProperties");
                copyKey(schemaNode, option, "additionalProperties");
                upgradeSchema(option);
              }
              default -> {
                final String referenceType = getReferenceType(type, schemaNode);
                option.put(REF_KEY, referenceType);
              }
            }
            oneOfOptions.add(option);
          }
          schemaNode.removeAll();
          schemaNode.set(ONEOF_KEY, oneOfOptions);
        }
      }
    }
  }

  /**
   * Modifies the schema in-place to downgrade from the new-style $ref declaration to the old-style
   * type declaration. Assumes that the schema is an ObjectNode containing a primitive declaration,
   * i.e. either something like: {"$ref": "WellKnownTypes..."} or: {"oneOf": [{"$ref":
   * "WellKnownTypes..."}, ...]}
   * <p>
   * In the latter case, the schema may contain subschemas. This method mutually recurses with
   * {@link SchemaMigrations#mutateSchemas(Function, Consumer, JsonNode)} to downgrade those
   * subschemas.
   *
   * @param schema An ObjectNode representing a primitive type declaration
   */
  private static void downgradeTypeDeclaration(final JsonNode schema) {
    if (schema.hasNonNull(REF_KEY)) {
      // If this is a direct type declaration, then we can just replace it with the old-style declaration
      final String referenceType = schema.get(REF_KEY).asText();
      ((ObjectNode) schema).removeAll();
      ((ObjectNode) schema).setAll(JsonSchemaReferenceTypes.REFERENCE_TYPE_TO_OLD_TYPE.get(referenceType));
    } else if (schema.hasNonNull(ONEOF_KEY)) {
      // If this is a oneOf, then we need to check whether we can recombine it into a single type
      // declaration.
      // This means we must do three things:
      // 1. Downgrade each subschema
      // 2. Build a new `type` array, containing the `type` of each subschema
      // 3. Combine all the fields in each subschema (properties, items, etc)
      // If any two subschemas have the same `type`, or the same field, then we can't combine them, but we
      // should still downgrade them.
      // See V0ToV1MigrationTest.CatalogDowngradeTest#testDowngradeMultiTypeFields for some examples.

      // We'll build up a node containing the combined subschemas.
      final ObjectNode replacement = (ObjectNode) Jsons.emptyObject();
      // As part of this, we need to build up a list of `type` entries. For ease of access, we'll keep it
      // in a List.
      final List<String> types = new ArrayList<>();

      boolean canRecombineSubschemas = true;
      for (final JsonNode subschemaNode : schema.get(ONEOF_KEY)) {
        // No matter what - we always need to downgrade the subschema node.
        downgradeSchema(subschemaNode);

        if (subschemaNode instanceof ObjectNode subschema) {
          // If this subschema is an object, then we can attempt to combine it with the other subschemas.

          // First, update our list of types.
          final JsonNode subschemaType = subschema.get(TYPE_KEY);
          if (subschemaType != null) {
            if (types.contains(subschemaType.asText())) {
              // If another subschema has the same type, then we can't combine them.
              canRecombineSubschemas = false;
            } else {
              types.add(subschemaType.asText());
            }
          }

          // Then, update the combined schema with this subschema's fields.
          if (canRecombineSubschemas) {
            final Iterator<Entry<String, JsonNode>> fields = subschema.fields();
            while (fields.hasNext()) {
              final Entry<String, JsonNode> field = fields.next();
              if (TYPE_KEY.equals(field.getKey())) {
                // We're handling the `type` field outside this loop, so ignore it here.
                continue;
              }
              if (replacement.has(field.getKey())) {
                // A previous subschema is already using this field, so we should stop trying to combine them.
                canRecombineSubschemas = false;
                break;
              } else {
                replacement.set(field.getKey(), field.getValue());
              }
            }
          }
        } else {
          // If this subschema is a boolean, then the oneOf is doing something funky, and we shouldn't attempt
          // to
          // combine it into a single type entry
          canRecombineSubschemas = false;
        }
      }

      if (canRecombineSubschemas) {
        // Update our replacement node with the full list of types
        final ArrayNode typeNode = Jsons.arrayNode();
        types.forEach(typeNode::add);
        replacement.set(TYPE_KEY, typeNode);

        // And commit our changes to the actual schema node
        ((ObjectNode) schema).removeAll();
        ((ObjectNode) schema).setAll(replacement);
      }
    }
  }

  private static void copyKey(final ObjectNode source, final ObjectNode target, final String key) {
    if (source.hasNonNull(key)) {
      target.set(key, source.get(key));
    }
  }

  /**
   * Given a primitive (string/int/num/bool) type declaration _without_ an airbyte_type, get the
   * appropriate $ref type. In most cases, this only depends on the "type" key. When type=string, also
   * checks the "format" key.
   */
  private static String getReferenceType(final String type, final ObjectNode schemaNode) {
    return switch (type) {
      case "string" -> {
        if (schemaNode.hasNonNull("format")) {
          yield switch (schemaNode.get("format").asText()) {
            case "date" -> JsonSchemaReferenceTypes.DATE_REFERENCE;
            // In these two cases, we default to the "with timezone" type, rather than "without timezone".
            // This matches existing behavior in normalization.
            case "date-time" -> JsonSchemaReferenceTypes.TIMESTAMP_WITH_TIMEZONE_REFERENCE;
            case "time" -> JsonSchemaReferenceTypes.TIME_WITH_TIMEZONE_REFERENCE;
            // If we don't recognize the format, just use a plain string
            default -> JsonSchemaReferenceTypes.STRING_REFERENCE;
          };
        } else if (schemaNode.hasNonNull("contentEncoding")) {
          if ("base64".equals(schemaNode.get("contentEncoding").asText())) {
            yield JsonSchemaReferenceTypes.BINARY_DATA_REFERENCE;
          } else {
            yield JsonSchemaReferenceTypes.STRING_REFERENCE;
          }
        } else {
          yield JsonSchemaReferenceTypes.STRING_REFERENCE;
        }
      }
      case "integer" -> JsonSchemaReferenceTypes.INTEGER_REFERENCE;
      case "number" -> JsonSchemaReferenceTypes.NUMBER_REFERENCE;
      case "boolean" -> JsonSchemaReferenceTypes.BOOLEAN_REFERENCE;
      // This is impossible, because we'll only call this method on string/integer/number/boolean
      default -> throw new IllegalStateException("Somehow got non-primitive type: " + type + " for schema: " + schemaNode);
    };
  }

  private static List<JsonNode> getSubschemas(final JsonNode schema, final String key) {
    final List<JsonNode> subschemas = new ArrayList<>();
    SchemaMigrations.findSubschemas(subschemas, schema, key);
    return subschemas;
  }

}
