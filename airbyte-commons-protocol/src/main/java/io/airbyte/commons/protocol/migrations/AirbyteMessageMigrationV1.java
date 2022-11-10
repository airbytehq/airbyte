package io.airbyte.commons.protocol.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.util.Optional;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.StreamSupport;

public class AirbyteMessageMigrationV1 implements AirbyteMessageMigration<AirbyteMessage, io.airbyte.protocol.models.v0.AirbyteMessage> {

  private static final Set<String> PRIMITIVE_TYPES = ImmutableSet.of(
    "string",
    "number",
    "integer",
    "boolean"
  );
  private static final Map<String, String> AIRBYTE_TYPE_TO_REFERENCE_TYPE = ImmutableMap.of(
      "timestamp_with_timezone", "WellKnownTypes.json#definitions/TimestampWithTimezone",
      "timestamp_without_timezone", "WellKnownTypes.json#definitions/TimestampWithoutTimezone",
      "time_with_timezone", "WellKnownTypes.json#definitions/TimeWithTimezone",
      "time_without_timezone", "WellKnownTypes.json#definitions/TimeWithoutTimezone",
      "integer", "WellKnownTypes.json#definitions/Integer",
      // these types never actually use airbyte_type, but including them for consistency
      "string", "WellKnownTypes.json#definitions/String",
      "number", "WellKnownTypes.json#definitions/Number",
      "boolean", "WellKnownTypes.json#definitions/Boolean",
      "date", "WellKnownTypes.json#definitions/Date"
  );

  @Override
  public AirbyteMessage downgrade(final io.airbyte.protocol.models.AirbyteMessage message,
                                  final Optional<ConfiguredAirbyteCatalog> configuredAirbyteCatalog) {
    return Jsons.object(Jsons.jsonNode(message), AirbyteMessage.class);
  }

  @Override
  public io.airbyte.protocol.models.v0.AirbyteMessage upgrade(AirbyteMessage oldMessage) {
    // We're not introducing any changes to the structure of the record/catalog
    // so just clone a new message object, which we can edit in-place
    io.airbyte.protocol.models.v0.AirbyteMessage newMessage = Jsons.object(
        Jsons.jsonNode(oldMessage),
        io.airbyte.protocol.models.v0.AirbyteMessage.class);
    if (oldMessage.getType() == Type.CATALOG) {
      for (AirbyteStream stream : newMessage.getCatalog().getStreams()) {
        JsonNode schema = stream.getJsonSchema();
        mutateSchemas(
            this::isPrimitiveTypeDeclaration,
            this::upgradeTypeDeclaration,
            schema);
      }
    } else if (oldMessage.getType() == Type.RECORD) {
      JsonNode data = newMessage.getRecord().getData();
      upgradeRecord((ObjectNode)data);
    }
    return newMessage;
  }

  /**
   * Detects any schema that looks like a primitive type declaration, e.g.:
   * { "type": "string" }
   * or
   * { "type": ["string", "object"] }
   */
  private boolean isPrimitiveTypeDeclaration(JsonNode schema) {
    if (!schema.isObject() || !schema.hasNonNull("type")) {
      return false;
    }
    JsonNode typeNode = schema.get("type");
    if (typeNode.isArray()) {
      return StreamSupport.stream(typeNode.spliterator(), false)
          .anyMatch(n -> PRIMITIVE_TYPES.contains(n.asText()));
    } else {
      return PRIMITIVE_TYPES.contains(typeNode.asText());
    }
  }

  /**
   * Modifies the schema in-place to upgrade from the old-style type declaration to the new-style $ref declaration.
   * Assumes that the schema contains a primitive declaration, i.e. either something like:
   * {"type": "string"}
   * or:
   * {"type": ["string", "object"]}
   *
   * @param schema An ObjectNode representing a primitive type declaration
   */
  private void upgradeTypeDeclaration(JsonNode schema) {
    ObjectNode schemaNode = (ObjectNode)schema;

    if (schemaNode.hasNonNull("airbyte_type")) {
      // If airbyte_type is defined, always respect it
      String referenceType = AIRBYTE_TYPE_TO_REFERENCE_TYPE.get(schemaNode.get("airbyte_type").asText());
      schemaNode.removeAll();
      schemaNode.put("$ref", referenceType);
    } else {
      // Otherwise, fall back to type/format
      JsonNode typeNode = schemaNode.get("type");
      if (typeNode.isTextual()) {
        String type = typeNode.asText();
        String referenceType = getReferenceType(type, schemaNode);
        schemaNode.removeAll();
        schemaNode.put("$ref", referenceType);
      } else {
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
          // For arrays and objects, we do a mutual recursion back into mutateSchemas to upgrade their subschemas.
          ArrayNode oneOfOptions = Jsons.arrayNode();
          for (String type : types) {
            ObjectNode option = (ObjectNode) Jsons.emptyObject();
            switch (type) {
              case "array" -> {
                option.put("type", "array");
                copyKey(schemaNode, option, "items");
                copyKey(schemaNode, option, "additionalItems");
                copyKey(schemaNode, option, "contains");
                mutateSchemas(
                    this::isPrimitiveTypeDeclaration,
                    this::upgradeTypeDeclaration,
                    option);
              }
              case "object" -> {
                option.put("type", "object");
                copyKey(schemaNode, option, "properties");
                copyKey(schemaNode, option, "patternProperties");
                copyKey(schemaNode, option, "additionalProperties");
                mutateSchemas(
                    this::isPrimitiveTypeDeclaration,
                    this::upgradeTypeDeclaration,
                    option);
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

  private static void copyKey(ObjectNode source, ObjectNode target, String key) {
    if (source.hasNonNull(key)) {
      target.set(key, source.get(key));
    }
  }

  /**
   * Given a primitive (string/int/num/bool) type declaration _without_ an airbyte_type,
   * get the appropriate $ref type.
   */
  private String getReferenceType(String type, ObjectNode schemaNode) {
    return switch (type) {
      case "string" -> {
        if (schemaNode.hasNonNull("format")) {
          yield switch (schemaNode.get("format").asText()) {
            case "date" -> "WellKnownTypes.json#definitions/Date";
            // In these two cases, we default to the "with timezone" type, rather than "without timezone".
            // This matches existing behavior in normalization.
            case "date-time" -> "WellKnownTypes.json#definitions/TimestampWithTimezone";
            case "time" -> "WellKnownTypes.json#definitions/TimeWithTimezone";
            // If we don't recognize the format, just use a plain string
            default -> "WellKnownTypes.json#definitions/String";
          };
        } else {
          yield "WellKnownTypes.json#definitions/String";
        }
      }
      case "integer" -> "WellKnownTypes.json#definitions/Integer";
      case "number" -> "WellKnownTypes.json#definitions/Number";
      case "boolean" -> "WellKnownTypes.json#definitions/Boolean";
      // This is impossible, because we'll only call this method on string/integer/number/boolean
      default -> "WellKnownTypes.json#definitions/String";
    };
  }

  /**
   * Recurses through all type declarations in the schema. For each type declaration that are accepted by matcher,
   * mutate them using transformer. For all other type declarations, recurse into them.
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
      //   if schema["type"] == "array": find subschemas for items, additionalItems, contains
      //   else if schema["type"] == "object": find subschemas for properties, patternProperties, additionalProperties
      //   else if oneof, allof, etc
      // but that sounds really verbose for no real benefit
      List<JsonNode> subschemas = new ArrayList<>();

      // array schemas
      findSubschemas(subschemas, schema, "items");
      findSubschemas(subschemas, schema, "additionalItems");
      findSubschemas(subschemas, schema, "contains");

      // object schemas
      if (schema.hasNonNull("properties")) {
        ObjectNode propertiesNode = (ObjectNode)schema.get("properties");
        Iterator<Entry<String, JsonNode>> propertiesIterator = propertiesNode.fields();
        while (propertiesIterator.hasNext()) {
          Entry<String, JsonNode> property = propertiesIterator.next();
          subschemas.add(property.getValue());
        }
      }
      if (schema.hasNonNull("patternProperties")) {
        ObjectNode propertiesNode = (ObjectNode)schema.get("patternProperties");
        Iterator<Entry<String, JsonNode>> propertiesIterator = propertiesNode.fields();
        while (propertiesIterator.hasNext()) {
          Entry<String, JsonNode> property = propertiesIterator.next();
          subschemas.add(property.getValue());
        }
      }
      findSubschemas(subschemas, schema, "additionalProperties");

      // combining restrictions - destinations have limited support for these, but we should handle the schemas correctly anyway
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
   * If schema contains key, then grab the subschema(s) at schema[key] and add them to the subschemas list.
   *
   * For example:
   * schema = {"items": [{"type": "string}]}
   * key = "items"
   * -> add {"type": "string"} to subschemas
   *
   * schema = {"items": {"type": "string"}}
   * key = "items"
   * -> add {"type": "string"} to subschemas
   *
   * schema = {"additionalProperties": true}
   * key = "additionalProperties"
   * -> add nothing to subschemas (technically `true` is a valid JsonSchema, but we don't want to modify it)
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

  private static void upgradeRecord(ObjectNode data) {
    Iterator<Entry<String, JsonNode>> fieldsIterator = data.fields();
    Map<String, String> replacements = new HashMap<>();
    while (fieldsIterator.hasNext()) {
      Entry<String, JsonNode> next = fieldsIterator.next();
      String key = next.getKey();
      JsonNode value = next.getValue();
      if (value.isNumber()) {
        replacements.put(key, value.asText());
      } else if (value.isObject()) {
        // TODO
      } else if (value.isArray()) {
        // TODO
      }
    }

    for (Map.Entry<String, String> replacement : replacements.entrySet()) {
      data.put(replacement.getKey(), replacement.getValue());
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
