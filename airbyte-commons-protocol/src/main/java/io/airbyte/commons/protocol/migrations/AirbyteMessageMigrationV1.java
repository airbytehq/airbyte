/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.TextNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.JsonSchemaReferenceTypes;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStream;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map.Entry;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.StreamSupport;

public class AirbyteMessageMigrationV1 implements AirbyteMessageMigration<io.airbyte.protocol.models.v0.AirbyteMessage, AirbyteMessage> {

  private ConfiguredAirbyteCatalog catalog;

  public AirbyteMessageMigrationV1(ConfiguredAirbyteCatalog catalog) {
    this.catalog = catalog;
  }

  @Override
  public io.airbyte.protocol.models.v0.AirbyteMessage downgrade(AirbyteMessage oldMessage) {
    // TODO implement downgrade
    io.airbyte.protocol.models.v0.AirbyteMessage newMessage = Jsons.object(
        Jsons.jsonNode(oldMessage),
        io.airbyte.protocol.models.v0.AirbyteMessage.class);
    if (oldMessage.getType() == Type.CATALOG) {
      for (io.airbyte.protocol.models.v0.AirbyteStream stream : newMessage.getCatalog().getStreams()) {
        JsonNode schema = stream.getJsonSchema();
        downgradeSchema(schema);
      }
    } else if (oldMessage.getType() == Type.RECORD) {
      // TODO downgrade records
    }
    return newMessage;
  }

  @Override
  public AirbyteMessage upgrade(io.airbyte.protocol.models.v0.AirbyteMessage oldMessage) {
    // We're not introducing any changes to the structure of the record/catalog
    // so just clone a new message object, which we can edit in-place
    AirbyteMessage newMessage = Jsons.object(
        Jsons.jsonNode(oldMessage),
        AirbyteMessage.class);
    if (oldMessage.getType() == io.airbyte.protocol.models.v0.AirbyteMessage.Type.CATALOG) {
      for (AirbyteStream stream : newMessage.getCatalog().getStreams()) {
        JsonNode schema = stream.getJsonSchema();
        upgradeSchema(schema);
      }
    } else if (oldMessage.getType() == io.airbyte.protocol.models.v0.AirbyteMessage.Type.RECORD) {
      JsonNode oldData = newMessage.getRecord().getData();
      JsonNode newData = upgradeRecord(oldData);
      newMessage.getRecord().setData(newData);
    }
    return newMessage;
  }

  /**
   * Perform the {type: foo} -> {$ref: foo} upgrade. Modifies the schema in-place.
   */
  private void upgradeSchema(JsonNode schema) {
    mutateSchemas(
        this::isPrimitiveTypeDeclaration,
        this::upgradeTypeDeclaration,
        schema);
  }

  /**
   * Perform the {$ref: foo} -> {type: foo} downgrade. Modifies the schema in-place.
   */
  private void downgradeSchema(JsonNode schema) {
    mutateSchemas(
        this::isPrimitiveReferenceTypeDeclaration,
        this::downgradeTypeDeclaration,
        schema);
  }

  /**
   * Detects any schema that looks like a primitive type declaration, e.g.: { "type": "string" } or {
   * "type": ["string", "object"] }
   */
  private boolean isPrimitiveTypeDeclaration(JsonNode schema) {
    if (!schema.isObject() || !schema.hasNonNull("type")) {
      return false;
    }
    JsonNode typeNode = schema.get("type");
    if (typeNode.isArray()) {
      return StreamSupport.stream(typeNode.spliterator(), false)
          .anyMatch(n -> JsonSchemaReferenceTypes.PRIMITIVE_JSON_TYPES.contains(n.asText()));
    } else {
      return JsonSchemaReferenceTypes.PRIMITIVE_JSON_TYPES.contains(typeNode.asText());
    }
  }

  /**
   * Detects any schema that looks like a reference type declaration, e.g.: { "$ref": "WellKnownTypes.json...." } or
   * { "oneOf": [{"$ref": "..."}, {"type": "object"}] }
   */
  private boolean isPrimitiveReferenceTypeDeclaration(JsonNode schema) {
    if (!schema.isObject()) {
      return false;
    } else if (schema.hasNonNull("$ref") && schema.get("$ref").asText().startsWith("WellKnownTypes.json")) {
      return true;
    } else if (schema.hasNonNull("oneOf")) {
      List<JsonNode> subschemas = getSubschemas(schema, "oneof");
      return subschemas.stream().anyMatch(
          subschema -> subschema.hasNonNull("$ref")
              && subschema.get("$ref").asText().startsWith("WellKnownTypes.json"));
    } else {
      return false;
    }
  }

  /**
   * Modifies the schema in-place to upgrade from the old-style type declaration to the new-style $ref
   * declaration. Assumes that the schema is an ObjectNode containing a primitive declaration, i.e.
   * either something like: {"type": "string"} or: {"type": ["string", "object"]}
   *
   * In the latter case, the schema may contain subschemas. This method mutually recurses with
   * {@link #mutateSchemas(Function, Consumer, JsonNode)} to upgrade those subschemas.
   *
   * @param schema An ObjectNode representing a primitive type declaration
   */
  private void upgradeTypeDeclaration(JsonNode schema) {
    ObjectNode schemaNode = (ObjectNode) schema;

    if (schemaNode.hasNonNull("airbyte_type")) {
      // If airbyte_type is defined, always respect it
      String referenceType = JsonSchemaReferenceTypes.AIRBYTE_TYPE_TO_REFERENCE_TYPE.get(schemaNode.get("airbyte_type").asText());
      schemaNode.removeAll();
      schemaNode.put("$ref", referenceType);
    } else {
      // Otherwise, fall back to type/format
      JsonNode typeNode = schemaNode.get("type");
      if (typeNode.isTextual()) {
        // If the type is a single string, then replace this node with the appropriate reference type
        String type = typeNode.asText();
        String referenceType = getReferenceType(type, schemaNode);
        schemaNode.removeAll();
        schemaNode.put("$ref", referenceType);
      } else {
        // If type is an array of strings, then things are more complicated
        List<String> types = StreamSupport.stream(typeNode.spliterator(), false)
            .map(JsonNode::asText)
            // Everything is implicitly nullable by just not declaring the `required `field
            // so filter out any explicit null types
            .filter(type -> !"null".equals(type))
            .toList();
        if (types.size() == 1) {
          // If there's only one type, e.g. {type: [string]}, just treat that as equivalent to {type: string}
          String type = types.get(0);
          String referenceType = getReferenceType(type, schemaNode);
          schemaNode.removeAll();
          schemaNode.put("$ref", referenceType);
        } else {
          // If there are multiple types, we'll need to convert this to a oneOf.
          // For arrays and objects, we do a mutual recursion back into mutateSchemas to upgrade their
          // subschemas.
          ArrayNode oneOfOptions = Jsons.arrayNode();
          for (String type : types) {
            ObjectNode option = (ObjectNode) Jsons.emptyObject();
            switch (type) {
              case "array" -> {
                option.put("type", "array");
                copyKey(schemaNode, option, "items");
                copyKey(schemaNode, option, "additionalItems");
                copyKey(schemaNode, option, "contains");
                upgradeSchema(option);
              }
              case "object" -> {
                option.put("type", "object");
                copyKey(schemaNode, option, "properties");
                copyKey(schemaNode, option, "patternProperties");
                copyKey(schemaNode, option, "additionalProperties");
                upgradeSchema(option);
              }
              default -> {
                String referenceType = getReferenceType(type, schemaNode);
                option.put("$ref", referenceType);
              }
            }
            oneOfOptions.add(option);
          }
          schemaNode.removeAll();
          schemaNode.set("oneOf", oneOfOptions);
        }
      }
    }
  }

  private void downgradeTypeDeclaration(JsonNode schema) {
    // TODO
  }

  private static void copyKey(ObjectNode source, ObjectNode target, String key) {
    if (source.hasNonNull(key)) {
      target.set(key, source.get(key));
    }
  }

  /**
   * Given a primitive (string/int/num/bool) type declaration _without_ an airbyte_type, get the
   * appropriate $ref type. In most cases, this only depends on the "type" key. When type=string, also
   * checks the "format" key.
   */
  private String getReferenceType(String type, ObjectNode schemaNode) {
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

  /**
   * Generic utility method that recurses through all type declarations in the schema. For each type
   * declaration that are accepted by matcher, mutate them using transformer. For all other type
   * declarations, recurse into their subschemas (if any).
   *
   * Note that this modifies the schema in-place. Callers who need a copy of the old schema should
   * save schema.deepCopy() before calling this method.
   *
   * @param schema The JsonSchema node to walk down
   * @param matcher A function which returns true on any schema node that needs to be transformed
   * @param transformer A function which mutates a schema node
   */
  private static void mutateSchemas(Function<JsonNode, Boolean> matcher, Consumer<JsonNode> transformer, JsonNode schema) {
    if (schema.isBoolean()) {
      // We never want to modify a schema of `true` or `false` (e.g. additionalProperties: true)
      // so just return immediately
      return;
    }
    if (matcher.apply(schema)) {
      // Base case: If this schema has a primitive type, then we need to mutate it
      transformer.accept(schema);
    } else {
      // Otherwise, we need to find all the subschemas and mutate them.
      // technically, it might be more correct to do something like:
      // if schema["type"] == "array": find subschemas for items, additionalItems, contains
      // else if schema["type"] == "object": find subschemas for properties, patternProperties,
      // additionalProperties
      // else if oneof, allof, etc
      // but that sounds really verbose for no real benefit
      List<JsonNode> subschemas = new ArrayList<>();

      // array schemas
      findSubschemas(subschemas, schema, "items");
      findSubschemas(subschemas, schema, "additionalItems");
      findSubschemas(subschemas, schema, "contains");

      // object schemas
      if (schema.hasNonNull("properties")) {
        ObjectNode propertiesNode = (ObjectNode) schema.get("properties");
        Iterator<Entry<String, JsonNode>> propertiesIterator = propertiesNode.fields();
        while (propertiesIterator.hasNext()) {
          Entry<String, JsonNode> property = propertiesIterator.next();
          subschemas.add(property.getValue());
        }
      }
      if (schema.hasNonNull("patternProperties")) {
        ObjectNode propertiesNode = (ObjectNode) schema.get("patternProperties");
        Iterator<Entry<String, JsonNode>> propertiesIterator = propertiesNode.fields();
        while (propertiesIterator.hasNext()) {
          Entry<String, JsonNode> property = propertiesIterator.next();
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

      // recurse into each subschema
      for (JsonNode subschema : subschemas) {
        mutateSchemas(matcher, transformer, subschema);
      }
    }
  }

  /**
   * If schema contains key, then grab the subschema(s) at schema[key] and add them to the subschemas
   * list.
   *
   * For example: schema = {"items": [{"type": "string}]} key = "items" -> add {"type": "string"} to
   * subschemas
   *
   * schema = {"items": {"type": "string"}} key = "items" -> add {"type": "string"} to subschemas
   *
   * schema = {"additionalProperties": true} key = "additionalProperties" -> add nothing to subschemas
   * (technically `true` is a valid JsonSchema, but we don't want to modify it)
   */
  private static void findSubschemas(List<JsonNode> subschemas, JsonNode schema, String key) {
    if (schema.hasNonNull(key)) {
      JsonNode subschemaNode = schema.get(key);
      if (subschemaNode.isArray()) {
        for (JsonNode subschema : subschemaNode) {
          subschemas.add(subschema);
        }
      } else if (subschemaNode.isObject()) {
        subschemas.add(subschemaNode);
      }
    }
  }

  private static List<JsonNode> getSubschemas(JsonNode schema, String key) {
    List<JsonNode> subschemas = new ArrayList<>();
    findSubschemas(subschemas, schema, key);
    return subschemas;
  }

  /**
   * Returns a copy of oldData, with numeric values converted to strings. String and boolean values
   * are returned as-is for convenience, i.e. this is not a true deep copy.
   */
  private static JsonNode upgradeRecord(JsonNode oldData) {
    if (oldData.isNumber()) {
      // Base case: convert numbers to strings
      return Jsons.convertValue(oldData.asText(), TextNode.class);
    } else if (oldData.isObject()) {
      // Recurse into each field of the object
      ObjectNode newData = (ObjectNode) Jsons.emptyObject();

      Iterator<Entry<String, JsonNode>> fieldsIterator = oldData.fields();
      while (fieldsIterator.hasNext()) {
        Entry<String, JsonNode> next = fieldsIterator.next();
        String key = next.getKey();
        JsonNode value = next.getValue();

        JsonNode newValue = upgradeRecord(value);
        newData.set(key, newValue);
      }

      return newData;
    } else if (oldData.isArray()) {
      // Recurse into each element of the array
      ArrayNode newData = Jsons.arrayNode();
      for (JsonNode element : oldData) {
        newData.add(upgradeRecord(element));
      }
      return newData;
    } else {
      // Base case: this is a string or boolean, so we don't need to modify it
      return oldData;
    }
  }

  @Override
  public Version getPreviousVersion() {
    return AirbyteProtocolVersion.V0;
  }

  @Override
  public Version getCurrentVersion() {
    return AirbyteProtocolVersion.V1;
  }

}
